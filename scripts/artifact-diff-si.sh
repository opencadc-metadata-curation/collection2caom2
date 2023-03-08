#!/bin/bash

if [[ $# -lt 1 ]]; then
	echo "Usage: ${0} <collection> [<caom resource>] [<si resource>]"
	echo "Default caom resource is ivo://cadc.nrc.ca/argus"
	echo "Default si resource is ivo://cadc.nrc.ca/global/luskan"
	exit 1
fi

coll=${1}
caom_resource=${2:-ivo://cadc.nrc.ca/argus}
si_resource=${3:-ivo://cadc.nrc.ca/global/luskan}

echo "Running artifact diff for ${coll}" 

IMAGE="opencadc/gem2caom2"
SCRIPT="artifact-diff-si.py"

sudo docker pull ${IMAGE} || exit $?
cp $HOME/.ssl/cadcproxy.pem . || exit $?
cp $HOME/scripts/${SCRIPT} . || exit $?

sudo docker run --rm --name artifact-diff-${coll} -v ${PWD}:/usr/src/app ${IMAGE} python ${SCRIPT} ${coll} ${caom_resource} ${si_resource} || exit $?

rm ${SCRIPT}
