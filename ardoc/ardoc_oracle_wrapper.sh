#!/bin/sh
timeminutes=$1
shift
command=$@
source $ARDOC_HOME/ARDOC_oracle_setup.sh
hostnm=`hostname`

echo "[ARDOC] Starting Oracle interface $command on ${hostnm}, limit $timeminutes minutes, PYTHONPATH $PYTHONPATH"

(sleep 1; \
 spp=`ps -ww -u $UID -o pid,ppid,args | grep -e "$command" | grep -v grep | grep -v "wrapper" | head -1 | awk '{print $1}'` ;\
 if [ "$spp" = "" ]; then spp=99999999; fi;\
 sppg=`ps -ww -u $UID -o pgid,ppid,args | grep -e "$command" | grep -v grep | grep -v "wrapper" | head -1 |  awk '{print $1}'` ;\
 a=1; while [ "$a" -le "$timeminutes" ]; do \
 sleep 60; \
 echo "[ARDOC, Oracle wrapper] minutes elapsed: $a "; \
 let "a+=1"; \
 spp_check=`ps -ww -u $UID -o pid,ppid,args | grep -e "$command" | grep -v grep | grep -v "wrapper" | head -1 | awk '{print $1}'` ;\
 if [ "$spp" != "$spp_check" ]; then echo "[ARDOC, Oracle wrapper] completion of Oracle interface process is detected"; break; fi; done;\
 spp_check=`ps -ww -u $UID -o pid,ppid,args | grep -e "$command" | grep -v grep | grep -v "wrapper" | head -1 | awk '{print $1}'` ;\
 if [ "$spp" = "$spp_check" ]; then echo "[ARDOC, Oracle wrapper] Oracleinterface process killed as time quota spent"; ${ARDOC_HOME}/ardoc_kill_fam.pl $spp 2; sleep 5; ${ARDOC_HOME}/ardoc_kill_fam.pl $spp 9 ; fi;\
 ps -ww -u $UID -o pgid,pid,args | grep -e "$command" | grep -v grep | grep -v "wrapper" | while read apgid apid acmd; do \
 if [ "$sppg" != "" -a "$apgid" = "$sppg" -a "$apid" != "" ]; then echo "[ARDOC, Oracle wrapper] runaway process $apid...."; echo " "; sleep 5; ps -ww -u $UID -o pgid,pid,args | grep -e "$command" | grep -v grep | grep -v "wrapper" | grep " ${apid} ">/dev/null 2>&1; st=$?; if [ "$st" -eq 0 ]; then kill -9 $apid; echo "[ARDOC, Oracle wrapper] process $apid is killed"; echo " "; fi; fi;\
done)&

start_test=`date`

eval time $command
stcom=$?
#echo "TTTTTTT $command"

echo "[ARDOC, Oracle interface wrapper start time] $start_test"
echo "[ARDOC, Oracle interface wrapper end time]" `date`

exit $stcom
