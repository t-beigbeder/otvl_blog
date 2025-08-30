---
ow_article: true
template: article.html
title: Deploying a high-availability K3s cluster on AWS
version: "1.0"
publication_date: "2024/06/19"
summary_heading: "Deploying a high-availability K3s cluster on AWS"
summary: |
    This article describes an experiment to deploy a K3s high-availability cluster on AWS,
    from solution to implementation.
    The solution leverages standard K3s components and remains cloud-agnostic as much as possible.
head_image: ../../assets/images/k3s-ha-experiment/mimosasABlagnac.jpg
head_img_title: Mimosas, pin et nuages au printemps à Blagnac
---

## Introduction

A [previous article](../k3s-loc-sp) presented the
[K3s](https://k3s.io/)
Kubernetes open source distribution
and how it could be used for development or simple application hosting on a single node.

As Kubernetes offers great support to load-balancing and high-availability,
it would be a pity not leveraging those features in K3s

- during development: testing distributed deployment and failure recovery scenarios,
- hosting: providing load-balancing and high-availability to the hosted applications that support it

This article describes an experiment for such a purpose:

- the simplest K3s solution providing high-availability to the cluster and its workloads,
- leveraging _off the shelf_ K3s components (the Traefik ingress controller, ServiceLB),
- adding [cert-manager](https://cert-manager.io/docs/)
for requesting Let's Encrypt HTTPS certificates for the workload ingresses,
- deploying a basic nginx static site for demonstration purpose,
- the whole being hosted on AWS but remaining mostly cloud-agnostic,
just leveraging very standard infrastructure

It is an experiment, because the solution could not be the most optimal one considering network performance,
and also because it should be secured concerning cluster roles.
Anyway the general design should be very relevant for most application hosting.

It is an experiment also as it helps to understand how standard Kubernetes components
and the network infrastructure can collaborate to provide high availability,
presented as a white box
instead of relying on vendor-specific solutions whose behavior remains quite obscure for non-specialists.
This is why many of us love Open Source, isn't it?
Detailed explanations are provided for this purpose when relevant.

The solution is first described, then the design of specific parts is detailed,
and finally some focus on relevant implementation parts is provided.

Useful links are provided at the bottom of this page.

## Solution

The solution relies on a K3s High Availability cluster with an embedded DB, as described
[here](https://docs.k3s.io/architecture#high-availability-k3s).
For the experimentation purpose, deploying a 3 servers cluster is enough,
but the solution could easily be extended thanks to K3s cluster management tools.

The servers are EC2 instances that are deployed in distinct AWS availability zones to provide best availability.

If the application workloads need to publish external network services,
the use of an external Load Balancer is also required to access Kubernetes hosted services on any node of the cluster.
To allow any TCP-based protocol to be balanced, an AWS Network Load Balancer must be deployed rather than an ALB.

The solution demonstrates the use of those components by deploying a simple Nginx static Web Server
accessed over HTTPS with a Let's Encrypt certificate.

As detailed in a [previous article](../le-k3s-ingresses), cert-manager is required for certificates provisioning
in the case of a multi-node cluster.

Those components and their interactions are summarized on the following schema.
Kubernetes workloads are distributed on the distinct nodes of the cluster
according to their respective deployment specifications and the current state of the cluster.

<img markdown="1" src=../../assets/images/k3s-ha-experiment/solution.png title="K3s High Availability solution" alt="K3s High Availability solution schema" class="img-fluid">

The AWS Network Load Balancer distributes network requests to the Traefik ingress controller service,
which is responsible to route them to the different deployed ingresses.
This is the critical specific part of the solution regarding load balancing and high availability.
Its design is detailed in the last part of the next section.

In our case HTTPS port 443 needs to be exposed for the nginx demonstration,
but also HTTP port 80 which is used by the ACME challenge for certificate generation.

## Design

### EC2 instances configuration

A SSH bastion enabling the operator's access with his or her public key is created
with the required DevOps automation and administration software:
OpenTofu, Ansible, Helm and kubectl

The three K3s cluster's nodes are created with the K3s service components
and also nerdctl for administration support.

The solution also requires the use of a home-made pod as explained below.
As this mockup doesn't involve the use of a CI-CD service,
a container build service must be provided:
to make the resulting infrastructure as affordable as possible,
the third cluster node is leveraged for this through the installation of buildkit.

The distribution of the resulting container image in the cluster requires
the use of an external registry service,
other build and deployment tools are self-sufficient,
except for the support of Let's Encrypt certificate generation service as already mentioned,
and obviously a Git remote repository, GitHub in our case.

In summary, the following schema describes the hosting infrastructure that is set up for this experiment.

<img markdown="1" src=../../assets/images/k3s-ha-experiment/hosting.png title="K3s High Availability hosting" alt="K3s High Availability hosting schema" class="img-fluid">

To keep it simple, default subnets are used in the VPC
but strict firewall rules are setup thanks to security groups.
This part of the design should be made more secure for production, following the principle of defense in depth,
by using network segmentation.

### Cluster set up

The initial cluster set up is straightforward using K3s installation tool:

- provide a cluster secret key
- install the first K3s server node with the secret and the option cluster-init
- install the two other server nodes with the secret and the first node URL to join the initialized cluster

Once the cluster is up and running, install the cert-manager components,
some explanations on its architecture being provided in a [previous article](../le-k3s-ingresses).

The load-balancing solution requires another component to be deployed in the cluster,
which is detailed now.

### Load balancer failure detection

The AWS Network Load Balancer solution is based on so-called target groups
which are network attachments for the network services to be balanced, in our case HTTPS and HTTP
on the EC2 nodes of the cluster.
Those target groups require a health check mechanism
so that network traffic will not be forwarded to a failing node,
until this node is repaired and up again.

We need to implement a network service on each node of the cluster that will answer to the health check request.
To make its deployment easier, we prefer using Kubernetes itself, and the design will be:

- a container image implementing a TCP echo network service
- a Kubernetes daemonset to launch the TCP echo pod on each node of the cluster
- a Kubernetes service with type NodePort to expose the network service at a specific TCP port

This is summarized on the schema below:

<img markdown="1" src=../../assets/images/k3s-ha-experiment/lb-failure.png title="Load balancer failure detection mechanism" alt="Load balancer failure detection mechanism schema" class="img-fluid">

Once a node being qualified as healthy, HTTP and HTTPS traffic (in our case)
will be forwarded to the Kubernetes network service
kube-proxy on the node selected by the Network Load Balancer,
that will in turn forward the traffic to the targeted Pod.

## Implementation

### General

If you are interested with the implementation, here are some general indications:

- the AWS infrastructure is provisioned using OpenTofu,
see [here](https://github.com/t-beigbeder/otvl_devops_tools/tree/main/src/opentofu/mockups/k3s_ha_aws)
- the bastion is configured using Ansible from a remote development environment,
see [here](https://github.com/t-beigbeder/otvl_devops_tools/blob/main/src/ansible/mockups/mockups_bastion.yml)
- the K3s nodes are configured using Ansible as well, from an environment that may be the bastion itself,
see [here](https://github.com/t-beigbeder/otvl_devops_tools/blob/main/src/ansible/mockups/mockup_k3s_ha.yml)

### Network security

AWS security groups are setup according to the solution general requirements concerning
the used protocols: SSH, HTTP, HTTPS and the TCP port for TCP echo failure detection.

K3s also uses HTTPS over 6443 concerning the API server.

Inside the cluster, network security rules are well defined following the K3s documentation
[here](https://docs.k3s.io/installation/requirements#inbound-rules-for-k3s-nodes)

### TCP echo failure detection

The TCP echo service simply uses the Linux network utility `socat`,
see [here](https://github.com/t-beigbeder/otvl_devops_tools/blob/main/src/docker/mockups/tcpecho/Dockerfile)
for the container build
and [here](https://github.com/t-beigbeder/otvl_devops_tools/tree/main/src/helm/mockups/tcpecho)
concerning its deployment with Helm as a daemonset on each node.

## Conclusion

Beyond its mere use to better understand network distribution and high availability features
in Kubernetes and related network infrastructure, this solution can be leveraged from different perspectives:

- reducing adherence with vendor-specific cloud infrastructure,
- reducing learning curve required to support such vendor-specific technologies,
- integrating hybrid solutions, for instance if DNS services, TLS certificates management and
load balancing services are not provided by the same vendor

### Notes

A few miscellaneous remarks:

- investigating Network Load Balancer issues is uneasy as access logs are not available for mere TCP traffic;
- AWS EC2 auto-scaling groups should be leveraged to provide dynamic cluster sizing in real-world scenarios;
- the later would require a rather different way to deploy, as K3s service installation and cluster joining
should be automatically configured, for instance by cloud-init at instance provisioning time

## References and further information

- [K3s documentation](https://docs.k3s.io/)
- [mockup git repository](https://github.com/t-beigbeder/otvl_devops_tools)

And also (keep sharing good things):

- [Somewhere between Andes, Chicago and Amsterdam](https://intlanthem.bandcamp.com/album/mestizx)
