#!/bin/sh
command=$@
source $ARDOC_HOME/ARDOC_oracle_setup.sh
hostnm=`hostname`
#echo "[ARDOC] Starting Oracle nightstat == $command == on ${hostnm}"
result=`python ${ARDOC_HOME}/ardoc_oracle_domains.py $command`
stat=$?
echo "$result"
exit $stat
