# Develop

## Python

    $ virtualenv -p python3.7 /path/to/venv/k8s_local_gpu
    $ . /path/to/venv/k8s_local_gpu/bin/activate
    $ pip install -r code/k8s_local_gpu/data/requirements-dev.txt \
      -f https://download.pytorch.org/whl/torch_stable.html

# Build

## Docker

In the following sections "192.168.122.139:5000" is the address of a private Docker registry,
to be adapted to your context.

    $ cd code/minikube
    $ docker build -t mk8s_server:1.0 .
    $ docker image tag mk8s_server:1.0 192.168.122.139:5000/mk8s_server:1.0
    $ docker push 192.168.122.139:5000/mk8s_server:1.0

# Run

In the following sections "192.168.122.139:5000" is the address of a private Docker registry,
to be adapted to your context.

To enable access to an insecure private registry from a Minikube cluster,
we must create the cluster with the --insecure flag,
providing for instance the CIDR network address for the registry server,
as demonstrated below:

    ## on host 192.168.122.139, launch a private registry
    $ docker run -d -p 5000:5000 --name registry -v /path/to/local/docker/registry:/var/lib/registry registry:2
    ## on the KVM host, create a Minikube cluster
    $ minikube -p mk8s-test02 -n=2 --insecure-registry 192.168.122.0/24 start

## Kubernetes

    $ kubectl apply -f code/minikube/data/k8s/mk8s_server_deployment.yml
    $ kubectl apply -f code/minikube/data/k8s/mk8s_server_service_load_balancer.yml

