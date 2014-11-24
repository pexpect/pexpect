#!/bin/bash
#
# This script assumes that the project 'ptyprocess' is
# available in the parent of the project's folder.
set -e
set -o pipefail

function usage() {
	echo "$0 (2.6|2.7|3.3|3.4)"
}
if [ -z $1 ]; then
	usage
	exit 1
fi

pyversion=$1
here=$(cd `dirname $0`; pwd)
osrel=$(uname -s)

. `which virtualenvwrapper.sh`
rmvirtualenv teamcity-pexpect || true
mkvirtualenv -p `which python${pyversion}` teamcity-pexpect

# install ptyprocess
cd $here/../../ptyprocess
python setup.py install

# run tests
cd $here/..
py.test-${pyversion} \
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
