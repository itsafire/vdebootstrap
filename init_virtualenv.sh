#!/bin/bash

# init_virtualenv
# ===============
#
# create a virtualenv for this python project

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "installing libzmql"
apt-get -y -q install libzmq1
apt-get -y -q install python-dev 
virtualenv --no-site-packages $SCRIPT_DIR
. $SCRIPT_DIR/bin/activate
pip -q install blumbum
pip -q install pyzmq
 
