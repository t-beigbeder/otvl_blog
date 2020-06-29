# Develop

## Python

    $ virtualenv -p python3.7 /path/to/venv/otvl_blog
    $ . /path/to/venv/otvl_blog/bin/activate
    $ pip install -r code/python/requirements-dev.txt

# Build

## Docker

    $ cd code/minikube
    $ docker build -t mk8s_server:1.0 .
    $ docker image tag mk8s_server:1.0 192.168.122.139:5000/mk8s_server:1.0
    $ docker push 192.168.122.139:5000/mk8s_server:1.0

# Run

## Kubernetes

