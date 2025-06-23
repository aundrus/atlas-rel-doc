#!/bin/sh
command=$@
source $NICOS_HOME/NICOS_oracle_setup.sh 1>&2
hostnm=`hostname`
#echo "[NICOS] Starting Oracle nightstat == $command == on ${hostnm}"
result=`python ${NICOS_HOME}/nicos_select_domain_for_training.py $command`
stat=$?
echo "$result"
exit $stat
