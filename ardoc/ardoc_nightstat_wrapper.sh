#!/bin/sh
command=$@
source $ARDOC_HOME/ardoc_oracle_setup.sh
hostnm=`hostname`
echo "ardoc_nightstat_wrapper: Info: starting Oracle nightstat == $command == on ${hostnm}"
result=`python ${ARDOC_HOME}/ardoc_oracle_nightstat.py $command`
stat=$?
echo "$result"
exit $stat
