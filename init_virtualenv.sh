#!/bin/bash

# init_virtualenv
# ===============
#
# create a virtualenv for this python project

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
apt-get -y -q install rabbitmq-server python-dev python-virtualenv
virtualenv --no-site-packages $SCRIPT_DIR
. $SCRIPT_DIR/bin/activate
pip -q install plumbum
pip -q install pika
