#!/bin/sh
set -eu
cd $HOME
if [ ! -f .bashrc ] ; then
    cp /etc/skel/.bashrc .bashrc
fi
exec "$@"