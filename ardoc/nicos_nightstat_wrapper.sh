#!/bin/sh
command=$@
source $NICOS_HOME/NICOS_oracle_setup.sh
hostnm=`hostname`
#echo "[NICOS] Starting Oracle nightstat == $command == on ${hostnm}"
result=`python ${NICOS_HOME}/nicos_oracle_nightstat.py $command`
stat=$?
echo "$result"
exit $stat