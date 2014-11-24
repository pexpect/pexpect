#!/bin/bash
#
# This script assumes that the project 'ptyprocess' is
# available in the parent of the project's folder.
set -e
set -o pipefail

if [ -z $1 ]; then
	echo "$0 (2.6|2.7|3.3|3.4)"
	exit 1
fi

pyversion=$1
here=$(cd `dirname $0`; pwd)
osrel=$(uname -s)
venv=teamcity-pexpect
venv_wrapper=$(which virtualenvwrapper.sh)

if [ -z $venv_wrapper ]; then
	echo "virtualenvwrapper.sh not found in PATH."
fi

. ${venv_wrapper}
workon ${venv} || mkvirtualenv -p `which python${pyversion}` ${venv} || true

# install ptyprocess
cd $here/../../ptyprocess
python setup.py install

# install all test requirements
pip install --upgrade pytest pytest pytest-cov coverage coveralls pytest-capturelog

# run tests
cd $here/..
py.test \
	--cov pexpect \
	--cov-config .coveragerc \
	--junit-xml=results.${osrel}.py${pyversion}.xml \
	--verbose \
	--verbose

# combine all coverage to single file, publish as build
# artifact in {pexpect_projdir}/build-output
mkdir -p build-output
coverage combine
mv .coverage build-output/.coverage.${osrel}.py{$pyversion}.$RANDOM.$$
