---
ow_article: true
template: article.html
title: "Developing and simple hosting with K3s"
version: "1.0"
publication_date: "2024/01/06"
summary_heading: "Developing and simple hosting with K3s"
summary: |
    K3s is a lightweight yet very effective Kubernetes distribution.
    This article provides feedback for deploying and using K3s
    in the context of development but also simple production.
head_image: ../../assets/images/k3s-loc-sp/versEtangDeSoulcem.jpg
head_img_title: Vers l'étang de Soulcem
---

## Introduction

[K3s](https://k3s.io/) is a lightweight yet very effective
[Kubernetes](https://kubernetes.io/) open source distribution.

While Docker and the Kubernetes orchestrator
are among the most popular hosting solutions for application components,
two interesting questions often remain open:

- how to work locally as a developer:
this is useful to set up, test and debug
the deployment more efficiently than if working remotely,
but also to leverage local computing resources
- how to orchestrate application containers in production environments
where there is no managed Kubernetes solution, or no cost-effective one either

This article provides feedback for deploying and using K3s
in the context of development but also simple production.

## Installing K3s for development

### Kubernetes control plane installation

Depending on your way of working and preference,
you can install K3s either directly on the development host if it is running Linux,
or on a separate Linux Virtual Machine that you will access remotely with `kubectl`.
Unless you want to test multi-nodes specific use-cases in development,
the default installation with all the components on a single node
is all what you need.

K3s installs the container runtime [containerd](https://github.com/containerd/containerd)
for running Docker-compatible containers, and that is a strong system requirement.
If you are already running Docker on the host, install K3s on a separate Virtual Machine,
or configure the installer to
[use](https://docs.k3s.io/advanced#using-docker-as-the-container-runtime)
it.

When ready, connect to the target host and run:

```shell
# curl -sfL https://get.k3s.io | sh -
```

Depending on system and network resources,
this single command will take a few dozens of seconds and deploy a fully operational
Kubernetes cluster as detailed below.

It is worth mentioning that the resulting cluster
will restart happily after a K3s host restart,
making the solution convenient when the development environment is stopped.

That being said,
this doesn't prevent obviously the application pods to take care of their data by themselves.

### Analyzing the K3s architecture

Having a look at the [architecture document](https://docs.k3s.io/architecture),
this simple deployment means that we run the K3s server components on the installed host,
and there is no additional K3s agent node.

We find on this document the following familiar Kubernetes components:

- "`api-server`" is the cluster API entry point;
- "`scheduler`" is responsible to allocate resources to the containers to be run;
- "`controller-manager`" is responsible to apply requested changes on the cluster;
- "`kubelet`" is an agent running on each node to control the state of containers;
- "`kube-proxy`" is responsible to configure network rules to enable secured network
  communication among the components and with external systems;

We also find the "`kine`" component that,
in this default installation,
enables the K3s server to store the cluster configuration and state
in a `SQLite` database, but could handle `etcd` as well.

<img markdown="1" src=../../assets/images/k3s-loc-sp/architecture.png title="K3s deployed architecture" alt="Deployed architecture schema" class="img-fluid">

What is specific to K3s is that those components are packaged and run
in a single Linux process, the `k3s` service on the previous schema,
making the use of CPU, memory and network resources as efficient as possible.
Other Kubernetes distributions
typically run them as individual containers and Linux system services.

    # systemctl status k3s.service
    ● k3s.service - Lightweight Kubernetes
         Loaded: loaded (/etc/systemd/system/k3s.service; enabled; preset: enabled)
         Active: active (running) since Wed 2024-01-03 09:21:54 CET; 3h 10min ago
           Docs: https://k3s.io
       Main PID: 2570 (k3s-server)
          Tasks: 213
         Memory: 1.7G
            CPU: 26min 24.955s

A few containers are also deployed for the control plane:

    # kubectl get pods -n kube-system
    NAME                                      READY   STATUS      RESTARTS   AGE
    local-path-provisioner-84db5d44d9-72qfw   1/1     Running     0          4h50m
    helm-install-traefik-crd-w7fs6            0/1     Completed   0          4h50m
    coredns-6799fbcd5-bctpp                   1/1     Running     0          4h50m
    helm-install-traefik-6lmt2                0/1     Completed   1          4h50m
    svclb-traefik-e23bb5a4-4zrcl              2/2     Running     0          4h47m
    traefik-8c645c69c-xrrcr                   1/1     Running     0          4h47m
    metrics-server-67c658944b-rlrzk           1/1     Running     0          4h50m

Among those, [Traefik](https://doc.traefik.io/traefik/)
is a reverse proxy and load balancer
that in our case is also able to play the role of a Kubernetes
[Ingress Controller](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/).
Traefik can use an ACME provider such as Let's Encrypt to request and renew TLS certificates
corresponding to the DNS of the hosted applications services
as declared in Kubernetes
[Ingresses](https://kubernetes.io/docs/concepts/services-networking/ingress/).

## Switching from Docker to Containerd

If you chose to use the default container runtime installation of K3s,
things are a little bit less easy than when using the Docker product
that comes packaged with its full featured command line interface.

Here are some installation steps to be performed on the K3s server.

### Introducing Nerdcrl

First thing is to install a user-friendly command line tool to work with containers.
This tool is open source too and is called [`Nerdctl`](https://github.com/containerd/nerdctl).

You can find uses of `ctr` and `crictl` tools too,
and they are installed with K3s,
but they are meant
for low-level interactions with containers as explained
[here](https://github.com/containerd/nerdctl/blob/main/docs/faq.md#how-is-nerdctl-different-from-ctr-and-crictl-).

A minimal installation is enough in the case K3s is already installed.
The rootless mode is not necessary either when you don't have specific security constraints.
So just download the
[binary](https://github.com/containerd/nerdctl/releases)
and install it in the PATH environment
for instance `/usr/local/bin`.

Nerdctl must be configured to use the K3s containerd installation:

    # vi /etc/nerdctl/nerdctl.toml
    address        = "/run/k3s/containerd/containerd.sock"
    namespace      = "k8s.io"

Let us test the installation:

    # nerdctl ps | grep traefik
    c0a135145594    docker.io/rancher/mirrored-library-traefik:2.10.5    "/entrypoint.sh --gl…"    3 minutes ago    Up                 k8s://kube-system/traefik-6cbd94bb8d-pgsl6/traefik
    # nerdctl images|grep traefik
    rancher/mirrored-library-traefik    2.10.5                  ca9c8fbe0010    2 days ago      linux/amd64    147.9 MiB    41.1 MiB
    rancher/mirrored-library-traefik    <none>                  ca9c8fbe0010    2 days ago      linux/amd64    147.9 MiB    41.1 MiB

An ansible role for doing that is available
[here](https://github.com/t-beigbeder/otvl_ansible/tree/master/src/ansible/playbooks/otvl_service/otvl_nerdctl).

Nerdctl provides a
[CLI](https://github.com/containerd/nerdctl/blob/main/docs/command-reference.md)
mostly compatible with Docker's one, just change `docker` with `nerdctl`,
which makes the switch as smooth as possible.
You can control images and containers as usual.
You can even launch docker compose stacks.
But you cannot build new images yet.

### Introducing BuildKit

Nerdctl is able to build docker images with the familiar `nerdctl build` sub-command
as soon as [BuildKit](https://github.com/moby/buildkit) is installed.

BuildKit is the new backend for building Docker images.
It is also packaged with recent releases of Docker,
so you may have already used it in this context.
Compared to the legacy Docker builder, it provides much better performance
through various optimizations.

Download BuildKit binaries from the project
[releases](https://github.com/moby/buildkit/releases)
and install them in the PATH environment
for instance `/usr/local/bin`.

BuildKit must be configured to use the K3s containerd installation:

    # vi /etc/buildkit/buildkitd.toml
    [worker.oci]
      enabled = false

    [worker.containerd]
      enabled = true
      address = "/run/k3s/containerd/containerd.sock"
      namespace = "k8s.io"

The buildkitd daemon must be installed as a systemd service:

    # vi /etc/systemd/system/buildkit.service
    [Unit]
    Description=BuildKit
    Documentation=https://github.com/moby/buildkit

    [Service]
    Type=simple
    TimeoutStartSec=10
    Restart=always
    RestartSec=10
    ExecStart=/usr/local/bin/buildkitd

    [Install]
    WantedBy=multi-user.target

    # systemctl daemon-reload
    # systemctl enable buildkit.service
    # systemctl start buildkit.service

Let us test the installation:

    # cat > Dockerfile <<EOF
    from nginx
    RUN echo "that's it" > message.txt
    EOF
    # nerdctl build -t nginx-custo:0.1 .
    [+] Building 0.4s (6/6) FINISHED
     => [internal] load build definition from Dockerfile
     ...
     => => naming to docker.io/library/nginx-custo:0.1                                                              0.0s
     => => unpacking to docker.io/library/nginx-custo:0.1                                                           0.0s

An ansible role for deploying BuildKit as above is available
[here](https://github.com/t-beigbeder/otvl_ansible/tree/master/src/ansible/playbooks/otvl_service/otvl_buildkit).

Now you are ready to use the `nerdctl build` subcommand for building new Docker images.

The images are available locally for direct use by Kubernetes Pod containers,
so there is no need for a Docker images registry in this context.

### Kubectl configuration

To access the K3s cluster with `kubectl` from a remote or non-root position
just copy the file `/etc/rancher/k3s/k3s.yaml`
into the local file `$HOME/.kube/config`,
then change the server url

    server: https://127.0.0.1:6443

with the name of the K3s server

    server: https://<k3s-server-name>:6443

### Ready for development

The Kubernetes environment is now fully operational for the development activities:

- building container images
- deploying Kubernetes workloads as Pods using those images,
- deploying related resources such as services and ingresses,
- accessing hosted workloads through the Ingress Controller and other gateway services

As K3s is production-ready, can the previous kind of deployment be used
for hosting production workloads?

## Simple hosting for production

### Introduction

Many deployment scenarios require a high level of availability.
While K3s provides all the required features for
[supporting](https://docs.k3s.io/architecture#high-availability-k3s)
it,
this is obviously not the case of this simple deployment,
as there are those two main single points of failure:

- the server node for the K3S server and user-plane workloads
- the SQLite database for storing the cluster configuration and state

Anyway, high availability does not necessarily mean _always available_,
and even this simple deployment can provide a very good availability level
as soon as it is effectively backed with automatic deployment.
And as the deployment is lightweight like we saw it, the recovery time can be pretty low.
We could say that the lack of redundancy is compensated
by the simplicity of what is to be deployed.

If we want to apply this solution for production workloads,
we can either build the application container images
on the K3s server using continuous deployment scripts,
or, in order to improve the global reliability and availability,
we can rather build those images using continuous integration scripts
that push them in a registry
from where they can be pulled at deployment time.

The following schema describes the deployment for both solutions,
with a registry hosted as a Kubernetes Pod on the K3s cluster.

<img markdown="1" src=../../assets/images/k3s-loc-sp/deployment.png title="K3s production simple deployment" alt="Production simple deployment schema" class="img-fluid">

Two topics require some attention:

- configuring the Ingress Controller for HTTPS TLS termination
and related ACME certificates
- configuring the registry for hosting on Kubernetes

They are detailed in the following sections.

### Configure the Traefik Ingress Controller

We want to expose Web services and applications on internet using HTTPS.
For this, corresponding services deploy a Kubernetes Ingress resource,
which is handled by the Traefik Ingress Controller
before being forwarded to the actual service.
Traefik provides TLS termination but also implements
HTTPS certificates generation and renewal using the ACME protocol.

The configuration of Traefik in the K3s context is a little bit convoluted
but well documented [here](https://docs.k3s.io/networking#traefik-ingress-controller).
This redirects to the Traefik Helm
[documentation](https://github.com/traefik/traefik-helm-chart/blob/master/traefik/VALUES.md).

In our case, we will provide the following configuration to K3s:

    # vi /var/lib/rancher/k3s/server/manifests/traefik-config.yaml
    apiVersion: helm.cattle.io/v1
    kind: HelmChartConfig
    metadata:
      name: traefik
      namespace: kube-system
    spec:
      valuesContent: |-
        persistence:
          enabled: true
        logs:
          general:
            level: INFO
          access:
            enabled: true

        ports:
          web:
            redirectTo:
              port: websecure
          websecure:
            tls:
              certResolver: leresolver
        certResolvers:
          leresolver:
            storage: /data/acme.json
            tlsChallenge: false
            httpChallenge:
              entryPoint: web
    # systemctl restart k3s.service

This is a mix of Helm and Traefik-like configuration, from which the main information is:

- redirect HTTP traffic to HTTPS
- use the Let's Encrypt ACME resolver to generate certificates for the cluster ingresses

The ACME-generated certificates are kept persistent in a Kubernetes physical volume
generated on local storage by the Helm template.

It is worth knowing that this configuration does not scale well:
on a multi-node control plane, the distributed Traefik ingress controllers
will each communicate with the ACME provider without coordination,
eventually failing to get a correct certificate.

A collection of ansible roles for deploying K3s and the Traefik Ingress Controller
as described previously are available
[here](https://github.com/t-beigbeder/otvl_ansible/tree/master/src/ansible/playbooks/otvl_service/k3s).

### Deploy a Container Registry on K3s

The open source Container Registry
[distribution](https://distribution.github.io/distribution)
is lightweight and simple to configure for hosting.

We want to provide a secure transport with HTTPS and to authenticate accesses:

- the Traefik Ingress Controller will provide TLS termination for HTTPS,
forwarding traffic over HTTP to the hosted registry,
a thing that was detailed in the previous section,
- a second Traefik instance will play the role of reverse proxy,
providing authentication and HTTP headers setting, as mentioned
[here](https://distribution.github.io/distribution/about/deploying/#importantrequired-http-headers)

We could have for instance the containers registry deployed as a Pod and exposed with a Service:

    apiVersion: v1
    kind: Pod
    metadata:
      name: ctr-reg
      labels:
        app.kubernetes.io/name: ctr-reg
    spec:
      ...
      containers:
        - name: ctr-reg
          image: registry:2
          ports:
            - containerPort: 5000
          volumeMounts:
            - name: "ctr-vol"
              mountPath: /var/lib/registry
            - name: "ctr-vcf"
              mountPath: /etc/docker/registry/config.yml
      volumes:
        ...
      restartPolicy: OnFailure
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: "ctr-reg"
    spec:
      selector:
        app.kubernetes.io/name: "ctr-reg"
      ports:
        - name: "reg-port"
          port: 5000
          protocol: TCP

And deploy a Traefik reverse proxy for authentication and HTTP protocol settings:

    apiVersion: v1
    kind: Pod
    metadata:
      name: ctr-router
      labels:
        app.kubernetes.io/name: ctr-router
    spec:
      ...
      containers:
        - name: ctr-router
          image: "traefik:v2.10"
          command: ["/usr/local/bin/traefik"]
          args: ["--configFile=/traefik/static_config.yml"]
          ports:
            - containerPort: 5000
          volumeMounts:
            ...
      volumes:
        ...
      restartPolicy: OnFailure
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: "ctr-router"
    spec:
      selector:
        app.kubernetes.io/name: "ctr-router"
      ports:
        - name: "router-port"
          port: 5000
          protocol: TCP
    ---
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: "ctr-router"
    spec:
      rules:
        - host: "<your DNS>"
          http:
            paths:
              - path: /
                pathType: Prefix
                backend:
                  service:
                    name:  "ctr-router"
                    port:
                      number: 5000

While the Traefik reverse proxy simply communicates over HTTP with the registry,
it is necessary to tell the registry that the origin protocol is HTTPS.

Thus from /traefik/static_config.yml:

    providers:
      file:
        filename: /traefik/dynamic_conf.yml
        watch: true
    entryPoints:
      web:
        address: ':5000'

to /traefik/dynamic_conf.yml:

    http:
      routers:
        to-app:
          rule: "PathPrefix(`/`)"
          priority: 1
          middlewares:
            - basic-auth
            - https-header
          service: reg
      middlewares:
        "basic-auth":
          basicAuth:
            users:
              - "<user>:$apr1$<password>"
        https-header:
          headers:
            customRequestHeaders:
              X-Forwarded-Proto: "https"
      services:
        "reg":
          loadBalancer:
            servers:
              - url: "http://ctr-reg:5000"

A collection of ansible roles for deploying the Distribution registry as detailed above
are available
[here](https://github.com/t-beigbeder/otvl_ansible/tree/master/src/ansible/playbooks/otvl_service/otvl_ctr).

### Additional notes

When dealing with failure recovery, the cluster may have to be redeployed from scratch,
including the hosted Pods.
This require each hosted Pod to take the responsibility to backup its data in a safe place,
and then to restore it at installation time.
Various cloud storage solutions can be used for such a need.

Concerning the Let's Encrypt ACME provider,
the number of certificates generated for a given DNS zone is limited in time.
So repeated failure recoveries could lead to reach this limit,
while this is very unlikely. More on this [here](https://letsencrypt.org/docs/rate-limits/).

## Conclusion

Except if you want to deploy a Containers Registry,
the deployment of a simple K3s cluster for development or for production
as seen above is simple enough to be achieved manually.
Build and deployment automation can reduce the time for failure recovery,
but more often for infrastructure upgrade,
and ansible roles and playbooks for doing that are available in the following
[git repository](https://github.com/t-beigbeder/otvl_ansible).

K3s is really a great solution for developing and for simple hosting on Kubernetes.
I personally use it for both activities,
and concerning the production, the K3s cluster is hosting, no talking about the control plane

- 5 web sites with low activity, totalling
- 17 pods
- 27 lightweight containers (using Apache, Traefik,
[Cabri](https://github.com/t-beigbeder/otvl_cabri)
and Python for APIs)

all running on a 2 vCores / 4 GB RAM Virtual Machine.
I guess this can be called no bullshit Green IT, with all due respect to cows and bulls.

Such simple hosting can be of great interest for SOHO self-hosting.

Finally, such an article cannot be closed without sending a big thank you
to all Kubernetes communities, providing real open source solutions
with the support of so many individuals and often backed by fair companies.
Such projects cannot succeed without them, and there are a lot of ways to support them.

## References

- [K3s project](https://github.com/k3s-io/k3s/)
- [K3s documentation](https://docs.k3s.io/)
- [Containerd project](https://github.com/containerd/containerd)
- [Traefik documentation](https://doc.traefik.io/traefik/)
- [Nerdctl](https://github.com/containerd/nerdctl)
- [BuildKit](https://github.com/moby/buildkit)
- [Distribution (container registry)](https://distribution.github.io/distribution)
