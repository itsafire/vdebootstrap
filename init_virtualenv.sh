#!/bin/bash

# 
# init_virtualenv
# ===============
#
# create a virtualenv for this python project
#
# 

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
apt-get -y -q install rabbitmq-server python-dev python-virtualenv
virtualenv --no-site-packages $SCRIPT_DIR
. $SCRIPT_DIR/bin/activate
# using easy_install instead of pip since pip install of templer is broken
easy_install templer.core
[-e bootstrap.py ] || wget http://svn.zope.org/*checkout*/zc.buildout/trunk/bootstrap/bootstrap.py
python bootstrap.py

echo 'U R up and ready. "bin/buildout"'
echo 'remember to ". bin/activate" when start a new session.'
