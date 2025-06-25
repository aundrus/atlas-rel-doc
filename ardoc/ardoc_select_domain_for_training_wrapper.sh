#!/bin/sh
command=$@
source $ARDOC_HOME/ARDOC_oracle_setup.sh 1>&2
hostnm=`hostname`
#echo "[ARDOC] Starting Oracle nightstat == $command == on ${hostnm}"
result=`python ${ARDOC_HOME}/ardoc_select_domain_for_training.py $command`
stat=$?
echo "$result"
exit $stat
