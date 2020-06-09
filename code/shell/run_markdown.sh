#!/usr/bin/env bash
. ${VENV_PATH}/bin/activate
cmd_dir=`dirname $0`
if [ "`echo $cmd_dir | cut -c1`" != "/" ] ; then
    cmd_dir="`pwd`/$cmd_dir"
fi
cp -a docs/images docs/*.md data/work/
python -m markdown < docs/index.md > data/work/index.html
python -m markdown < docs/k8s-local-dev.md > data/work/k8s-local-dev.html