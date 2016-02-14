#!/bin/bash
#
# This script assumes that the project 'ptyprocess' is
# available in the parent of the project's folder.
set -e
set -o pipefail

if [ -z $1 ]; then
	echo "$0 (2.6|2.7|3.3|3.4|3.5)"
	exit 1
fi

export PYTHONIOENCODING=UTF8
export LANG=en_US.UTF-8

pyversion=$1
version_flit=3.5
shift
here=$(cd `dirname $0`; pwd)
osrel=$(uname -s)
venv=teamcity-pexpect
venv_flit=flit-builder

function prepare_virtualenvwrapper() {
	venv_wrapper=$(which virtualenvwrapper.sh)
	. ${venv_wrapper}
	if [ -z $venv_wrapper ]; then
		echo "virtualenvwrapper.sh not found in PATH." >&2
		exit 1
	fi
}

function make_wheel_for_ptyprocess() {
	mkvirtualenv -p`which python${version_flit}` ${venv_flit} || true
	workon ${venv_flit}
	# explicitly use pip3.5 to install/upgrade flit, a dependency for building
	# the ptyprocess wheel package.  Flit is not compatible with python 2.7.
	pip${version_flit} install --upgrade flit

	# create ptyprocess wheel
	cd $here/../../ptyprocess
	rm -f dist/*
	flit wheel
	deactivate
}

function prepare_environment() {
	# create a virtualenv for target python version, install ptyprocess and test dependencies
	rmvirtualenv ${venv} || true
	mkvirtualenv -p `which python${pyversion}` ${venv} || true
	workon ${venv}
	pip uninstall --yes ptyprocess || true
	pip install ../ptyprocess/dist/ptyprocess-*.whl
	pip install --upgrade pytest-cov coverage coveralls pytest-capturelog
}

function do_test() {
	# run tests
	cd $here/..
	ret=0
	py.test \
		--cov pexpect \
		--cov-config .coveragerc \
		--junit-xml=results.${osrel}.py${pyversion}.xml \
		--verbose \
		--verbose \
		"$@" || ret=$?

	if [ $ret -ne 0 ]; then
		# we always exit 0, preferring instead the jUnit XML
		# results to be the dominate cause of a failed build.
		echo "py.test returned exit code ${ret}." >&2
		echo "the build should detect and report these " \
			"failing tests from the jUnit xml report." >&2
	fi
}

function report_coverage() {
	# combine all coverage to single file, report for this build,
	# then move into ./build-output/ as a unique artifact to allow
	# the final "Full build" step to combine and report to coveralls.io
	`dirname $0`/teamcity-coverage-report.sh
	mkdir -p build-output
	mv .coverage build-output/.coverage.${osrel}.py{$pyversion}.$RANDOM.$$
}

prepare_virtualenvwrapper
make_wheel_for_ptyprocess
prepare_environment
do_test
report_coverage
