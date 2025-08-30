---
ow_article: true
template: article.html
title: Let’s encrypt K3s ingresses with cert-manager
version: "1.0"
publication_date: "2024/02/06"
summary_heading: "Let’s encrypt K3s ingresses"
summary: |
    How to generate "Let's encrypt" certificates with Cert-manager
    on a K3s kubernetes cluster.
head_image: /assets/images/le-k3s-ingresses/voilierAPortVendres.jpg
head_img_title: Voilier à Port-Vendres
---

## Introduction

A [previous article](/blog/k3s-loc-sp) presented the
[K3s](https://k3s.io/)
kubernetes open source distribution
and how it could be used for simple and efficient application hosting.

A common need in such scenarios is to expose some services as Ingresses
on HTTPS, and in consequence having to manage corresponding TLS certificates.
As discussed in the previous article, the Traefik Ingress Controller provides this feature
for [Let's Encrypt](https://letsencrypt.org/) and other ACME services,
but the controller has to be deployed on a single node.

This article details how to generate "Let's encrypt" certificates
using the [cert-manager](https://cert-manager.io/) component in a standard K3s environment,
making the solution more general and robust.

The purpose of this article is to present the solution from a rather operational point of view,
but also to give a general perspective of the tools involved,
and how they can be leveraged in other situations.

Useful links are provided at the bottom of this page.

## Ingresses and the Ingress Controller

From Web Clients to the Kubernetes Pods implementing the Web Services,
several steps are involved that are detailed here.

<img markdown="1" src=/assets/images/le-k3s-ingresses/ingress.png title="Ingresses and the Ingress Controller" alt="Ingresses and the Ingress Controller schema" class="img-fluid">

Network ports exposed by pods can be made available at the cluster level
by using kubernetes [Services](https://kubernetes.io/docs/concepts/services-networking/service/)
which provide a stable internal network address.
[Ingresses](https://kubernetes.io/docs/concepts/services-networking/ingress/)
are Kubernetes resources that enable, among others, to expose HTTPS and HTTP kubernetes services
to be accessed from outside the cluster.
For this to work, an
[Ingress Controller](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/)
must be running on the cluster to manage ingresses resources
and expose them to the external network.
The ingress controller is also exposed as a kubernetes service but its type is `LoadBalancer`
and it relies on a component called an External Load Balancer:

- in a Cloud deployment, such load balancers are provided by the actual cloud provider
and take the responsibility to assign a public IP address with corresponding public DNS entries
and to balance the TCP requests it receives to one or several backend services,
among which the ingress controller in our case
- in the case of a local deployment, K3s implements by default a
[Load Balancer](https://docs.k3s.io/networking#service-load-balancer)
that can play the load balancing role on the local network,
or if no External Load Balancer is configured

NB: ingresses have technically nothing to do with network communication,
so the diagrams provided on this page are rather "logical" than technical ones.
This is the ingress controller that handle communication between the load balancer and the target services.

To give more context about the role of ingresses in relation with TLS certificates,
the following figure is an example of the routing capability provided by ingress resources:

<img markdown="1" src/assets/images/le-k3s-ingresses/ingress-routes.png title="Ingresses and related routes" alt="Ingresses and related routes schema" class="img-fluid">

Two distinct DNS entries are exposed by the external load balancer to be routed to the ingress controller.
The application ingress declares one route for each DNS
to forward the request to one or another Pod Service. This is an example of server name based routing,
and as the ingress resource is dedicated to the HTTP protocol, path-based routing can be used as well.

So in a cluster hosting many Web Applications and APIs, we can expect their related ingresses
to request the exposure of many distinct DNS entries for services to be accessed over the HTTPS protocol,
thus requiring related TLS certificates to be issued and then renewed periodically.
This is why a tool intended to manage such a repetitive and time consuming process is so profitable.

## The Certificate Manager component

### A standard kubernetes addon

[Certificate Manager](https://cert-manager.io/docs/cli/controller/)(cert-manager)
is a Kubernetes addon to automate the management and issuance of
TLS certificates from various issuing sources.
A general presentation is available [here](https://venafi.com/open-source/cert-manager/),
and the product documentation is available [here](https://cert-manager.io/docs/).

cert-manager has become a standard addon for kubernetes clusters.
Certificates are machine identities
and the overall security of the solution is of first importance.
cert-manager benefits from a large community feedback for a long time.
It is well documented, maintained and supported.

In the case of a self-hosted kubernetes cluster,
cert-manager is probably currently the best solution to manage certificates.
Concerning managed kubernetes solutions,
even if major cloud providers come with their own certificate management tooling,
cert-manager is also often able to integrate with their solutions as well
(see [this](https://cert-manager.io/docs/configuration/issuers/)),
and this may be required for non-standard use-cases.
In the case of OVH managed kubernetes solution, it seems that cert-manager is the standard solution.

### Simple to install, simplifies operations

For newcomers, cert-manager may appear somewhat complex because it provides many features,
it includes several sub-components,
and finally it comes with its own
[Custom Resources](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/).

In fact it is not, but rather it is both easy to install and to operate.
Likewise, the custom resources it installs
provide some user-friendly visibility on the managed certificates, related secret keys
and on-going issuance or renewal operations.

To be fair, it should rather be said that cert-manager is complex, as certificate management is,
but this complexity is mainly hidden to the user.

### Installation

This addon comes with several kubernetes resources and CRDs to be installed,
but the installation without customization is as simple as (choose latest stable `<cm-release>`):

    $ kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/<cm-release>/cert-manager.yaml

    $ kubectl get pods -n cert-manager
    NAME                                       READY   STATUS    RESTARTS       AGE
    cert-manager-5c9d8879fd-scbmm              1/1     Running   10 (26m ago)   15d
    cert-manager-cainjector-6cc9b5f678-jdvfj   1/1     Running   17 (25m ago)   15d
    cert-manager-webhook-7bb7b75848-wsp8x      1/1     Running   17 (25m ago)   15d

Installation with Helm charts is also available as documented
[here](https://cert-manager.io/docs/installation/helm/)
and provides all options for customization.

### Cert-manager main components

Without being fully accurate, the following schema explains the roles of the
cert-manager resources and components that are deployed during the installation:

<img markdown="1" src=/assets/images/le-k3s-ingresses/architecture.png title="Cert-Manager addon main components" alt="Cert-Manager addon main components schema" class="img-fluid">

- the controller watches ingresses that request cert-manager services to manage their certificates
- ingresses' configurations refer to an Issuer that is a custom resource
- an issuer provides some information on how to communicate with a certificate authority
such as Let's encrypt
- an issuer can be restricted to a namespace or operate cluster-wide,
balancing between security and simplicity

Let's see a practical example using an ACME Issuer.

## Automating Let's encrypt certificates management

For automating Let's encrypt certificates management, an issuer is defined,
for instance as following:

    apiVersion: cert-manager.io/v1
    kind: ClusterIssuer
    metadata:
      name: letsencrypt
    spec:
      acme:
        email: your@email.here
        server: https://acme-v02.api.letsencrypt.org/directory
        privateKeySecretRef:
          # Secret resource that will be used to store the account's private key.
          name: letsencrypt-issuer-account-key
        solvers:
          - http01:
              ingress:
                class: traefik

It appears that issuers respective configurations are typed according to their category,
here using an `acme` entry
including the configuration required to access the Let's encrypt CA and a solver.
The need to define the ingress to be used by this issuer deserves some explanation
that is available
[here](https://cert-manager.io/docs/reference/api-docs/#acme.cert-manager.io/v1.ACMEChallengeSolverHTTP01):

_The ingress based HTTP01 challenge solver will solve challenges by creating or modifying Ingress resources
in order to route requests for ‘/.well-known/acme-challenge/XYZ’ to ‘challenge solver’ pods
that are provisioned by cert-manager for each Challenge to be completed._

More on this in the following section.

Once deployed, the issuer may be referenced by ingresses using annotations, for instance:

    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: "example-router"
      annotations:
        cert-manager.io/cluster-issuer: letsencrypt
    spec:
      tls:
        - hosts:
            - site.example.com
            - api.example.com
          secretName: example-router
      rules:
        - host: site.example.com
          ...

On that example, cert-manager will issue a request for a certificate containing both mentioned hosts
as subject alternate names.

Here is a sample of the use of the `certificate` custom resource type,
demonstrating its usefulness:

    $ kubectl describe certificate example-router
    Name:         example-router
    ...
    API Version:  cert-manager.io/v1
    Kind:         Certificate
    ...
    Spec:
      Dns Names:
        site.example.com
        ...
      Issuer Ref:
        Group:      cert-manager.io
        Kind:       ClusterIssuer
        Name:       letsencrypt
    ...
    Status:
      ...
      Not After:               2024-04-23T19:22:29Z
      Not Before:              2024-01-24T19:22:30Z
      ...

You can find
[here](https://github.com/t-beigbeder/otvl_blog/blob/master/code/le-k3s-ingresses/sample.yaml)
a complete kubernetes manifest file that demonstrate the previously mentioned concepts.

The following section details how the ACME challenge is implemented and then handled by cert-manager.

## The ACME protocol and TLS redirects

The ACME protocol is intended to verify that the server requesting a certificate
is actually owned by the DNS name owner.
If that server is able to receive some secret information (the challenge)
sent on the given DNS name by the ACME server,
the requester will answer back to the ACME server and therefore validate ownership.
The ACME server will issue a trusted certificate and send it to the requester.

The diagram below extends the previous one in the context of the ACME issuer.

<img markdown="1" src=/assets/images/le-k3s-ingresses/acme.png title="Cert-Manager acme issuer" alt="Cert-Manager acme issuer schema" class="img-fluid">

A solver pod is launched that is responsible to request a certificate to the Let's encrypt server
and to handle the ACME protocol. A corresponding service and ingress also need to be created.
This explains why the issuer configuration
has to mention which ingress controller to use for that purpose.

cert-manager takes care to only request routing to the ingress controller for ACME related HTTP requests.

This is fine and works well... except if we ask Traefik to perform automatic TLS redirection,
which is a good practice and as such a very useful service provided by the Traefik ingress controller.
But in that case, the ACME server will receive HTTP redirects that it is not supposed to handle.

So the K3s Traefik configuration provided at K3s installation time
(see the [previous article](/blog/k3s-loc-sp))
should specifically
mention a priority level higher than the default one (very high)
so that the solver ingress may come with higher priority (*):

    apiVersion: helm.cattle.io/v1
    kind: HelmChartConfig
    metadata:
      name: traefik
      namespace: kube-system
    spec:
      valuesContent: |-
        ...
        ports:
          web:
            redirectTo:
              port: websecure
              # enable cert-manager ACME solver to escape redirection for the challenge to succeed
              priority: 1000

(*) Although the behavior is not clearly documented,
as a priority such as 1000 like it is set above
should be higher than the acme-challenge path length,
perhaps is the Traefik redirect internal router specific for this,
anyway it works.

On a single-node deployment, you can simply modify the following file afterwards,

    /var/lib/rancher/k3s/server/manifests/traefik-config.yaml

then delete the ingress controller pod, and wait for it to be created again.

## Additional notes

Here are additional topics that you may find interesting in the context of what is discussed here.

### Several interesting kinds of issuers

The cert-manager Issuer is intended to configure communication
with a specific kind of certificate authority,
like an ACME authority as it was detailed above.
Cloud providers specific issuers being left apart, you can also enjoy using:

- a private certificate authority, including [Vault](https://www.vaultproject.io/)
- self-signed certificates provisioned by `cert-manager` itself
- see the full list [here](https://cert-manager.io/docs/configuration/)


### The Kubernetes Gateway API

The [Gateway API](https://gateway-api.sigs.k8s.io/)
_is an official Kubernetes project focused on L4 and L7 routing in Kubernetes_,
it can be considered as a generalization of the Ingress API.
This is a promising feature, not yet widely implemented as it is rather new.
From what is explained above, related
[Gateway](https://kubernetes.io/docs/concepts/services-networking/gateway/#api-kind-gateway)
resources can be used in place of ingresses.

cert-manager is
[able to handle](https://cert-manager.io/docs/usage/gateway/)
gateway resources in a similar way as it does concerning ingresses.

### Metallb

[MetalLB](https://metallb.universe.tf/)
_is a load-balancer implementation for bare metal Kubernetes clusters, using standard routing protocols._

As mentioned above, K3s comes with a built-in load balancer.
To enable Metallb, it has to be explicitly
[disabled](https://docs.k3s.io/networking#disabling-servicelb).

## Conclusion

cert-manager is very easy to install, use and operate on a self-hosted cluster running K3s,
at least concerning ACME authorities like Let's encrypt.
As mentioned, the only attention point concerns TLS redirections and is easy to fix.

cert-manager is also useful in many other contexts and technical environments,
as briefly mentioned in different parts of this article.

Again, thanks must be addressed to the Kubernetes communities and companies
for providing such high quality and useful open-source software
and all the support that comes with it.
There are a lot of ways to support them.

## References and further information

- [cert-manager documentation](https://cert-manager.io/docs/)
- [cert-manager general presentation](https://venafi.com/open-source/cert-manager/)
- [Secure Web Applications with Traefik Proxy, cert-manager, and Let’s Encrypt](https://traefik.io/blog/secure-web-applications-with-traefik-proxy-cert-manager-and-lets-encrypt/?utm_source=pocket_saves)
- [Combining Ingress Controllers and External Load Balancers with Kubernetes](https://traefik.io/blog/combining-ingress-controllers-and-external-load-balancers-with-kubernetes/)
- [Globally enabled http to https blocks cert manager http challenge](https://community.traefik.io/t/globally-enabled-http-to-https-blocks-cert-manager-http-challenge/20047)
- [ACME HTTP-01 challenge](https://letsencrypt.org/docs/challenge-types/#http-01-challenge)
- [The challenges of on-premise Kubernetes clusters and how to solve them](https://www.padok.fr/en/blog/on-premise-kubernetes)

And also (other keyboards):

- [mythical synthesizers played by great duo](https://transversales.bandcamp.com/album/golden-apples-of-the-sun-3)
