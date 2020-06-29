#!/usr/bin/env bash
. /srv/pkg/otvl_web_server_venv/bin/activate
cd ${SRV_DATA} && \
  python \
    -m otvl_blog.minikube.server \
    -p "${API_PORT}" \
    -a "${API_ADDRESS}"