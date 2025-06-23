#!/bin/sh
comname=`basename $0`
if [ "$comname" = "nicos_oracle_starter.sh" ]; then
exitcomtool="exit"
else
exitcomtool="return"
fi

#echo "exitcomtool $exitcomtool"

conf="i686-slc4-gcc34-dbg"
nightlyn="EXP"
short=0

while [ $# -ne 0 ]; do
        case $1 in
            -n) nightlyn=$2; shift;;
            -c) conf=$2; shift;;
        esac
        shift
done

if [ "$NICOS_NIGHTLY_NAME" = "" ]; then
echo "nicos_oracle_starter: Error: NICOS_NIGHTLY_NAME is not defined: no oracle initialization "
echo "nicos_oracle_starter: Info: which python: " `which python` `python --version`
python $NICOS_HOME/nicos_send_mail.py -l "FATAL" -m "NICOS_NIGHTLY_NAME is not defined"
${exitcomtool} 1
fi

if [ "$short" -eq 1 ]; then ${exitcomtool} 0; fi

$NICOS_HOME/nicos_oracle_wrapper.sh 3 python $NICOS_HOME/nicos_oracle_starter.py -c $conf -n $nightlyn; st=$?
$NICOS_HOME/nicos_nightstat_wrapper.sh -n $NICOS_NIGHTLY_NAME -s 0 --short

if [ "$st" -ne 0 ]; then
echo "nicos_oracle_starter: Error: nicos_oracle_starter.py returned $st"
python $NICOS_HOME/nicos_send_mail.py -l "FATAL" -m "nicos_oracle_starter.py returned $st"
${exitcomtool} 1
else
  if [ -f ${NICOS_GEN_CONFIG_AREA}/jobid.txt ]; then
     jobid=`cat ${NICOS_GEN_CONFIG_AREA}/jobid.txt | head -1`
     echo "nicos_oracle_starter: assigned job id $jobid"
  else
     echo "nicos_oracle_starter: Error job id text file was not created: ${NICOS_GEN_CONFIG_AREA}/jobid.txt"
     python $NICOS_HOME/nicos_send_mail.py -l "FATAL" -m "job id text file was not created: ${NICOS_GEN_CONFIG_AREA}/jobid.txt"
     ${exitcomtool} 1
  fi     
fi
