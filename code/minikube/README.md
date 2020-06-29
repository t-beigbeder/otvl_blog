# Development

## Python

    $ virtualenv -p python3.7 /path/to/venv/otvl_blog
    $ . /path/to/venv/otvl_blog/bin/activate
    $ pip install -r code/python/requirements-dev.txt

## Docker

    $ cd code/minikube
    $ docker build -t mk8s_server:1.0 .
    $ docker image tag mk8s_server:1.0 _registry_name_and_port_/mk8s_server:1.0
    $ docker push _registry_name_and_port_/mk8s_server:1.0
