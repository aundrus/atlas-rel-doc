#!/bin/sh
comname=`basename $0`
if [ "$comname" = "ardoc_oracle_starter.sh" ]; then
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

if [ "$ARDOC_NIGHTLY_NAME" = "" ]; then
echo "ardoc_oracle_starter: Error: ARDOC_NIGHTLY_NAME is not defined: no oracle initialization "
echo "ardoc_oracle_starter: Info: which python: " `which python` `python --version`
python $ARDOC_HOME/ardoc_send_mail.py -l "FATAL" -m "ARDOC_NIGHTLY_NAME is not defined"
${exitcomtool} 1
fi

if [ "$short" -eq 1 ]; then ${exitcomtool} 0; fi

$ARDOC_HOME/ardoc_oracle_wrapper.sh 3 python $ARDOC_HOME/ardoc_oracle_starter.py -c $conf -n $nightlyn; st=$?
$ARDOC_HOME/ardoc_nightstat_wrapper.sh -n $ARDOC_NIGHTLY_NAME -s 0 --short

if [ "$st" -ne 0 ]; then
echo "ardoc_oracle_starter: Error: ardoc_oracle_starter.py returned $st"
python $ARDOC_HOME/ardoc_send_mail.py -l "FATAL" -m "ardoc_oracle_starter.py returned $st"
${exitcomtool} 1
else
  if [ -f ${ARDOC_GEN_CONFIG_AREA}/jobid.txt ]; then
     jobid=`cat ${ARDOC_GEN_CONFIG_AREA}/jobid.txt | head -1`
     echo "ardoc_oracle_starter: assigned job id $jobid"
  else
     echo "ardoc_oracle_starter: Error job id text file was not created: ${ARDOC_GEN_CONFIG_AREA}/jobid.txt"
     python $ARDOC_HOME/ardoc_send_mail.py -l "FATAL" -m "job id text file was not created: ${ARDOC_GEN_CONFIG_AREA}/jobid.txt"
     ${exitcomtool} 1
  fi     
fi
