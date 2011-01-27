#!/bin/ksh
#
# This assumes the environment is setup properly, it will generate
# a production-ready EGG for deployement.
#

if [ ! -e "setup.py" ]; then
	echo "Please run from the root, where setup.py lives."
	exit
fi

. virtualenv/bin/activate

python setup.py egg_info -RDb "" sdist bdist_egg

