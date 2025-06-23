#!/bin/sh
command=$@
source $ARDOC_HOME/ardoc_oracle_setup.sh 1>&2
hostnm=`hostname`
echo "ardoc_latest_ntag_wrapper: Info: starting Oracle nightstat == $command == on ${hostnm}" 1>&2
result=`python ${ARDOC_HOME}/ardoc_oracle_latest_ntag.py $command`
stat=$?
echo "$result"
exit $stat
