#!/bin/sh
comname=`basename $0`
if [ "$comname" = "ardoc_oracle_starter.sh" ]; then
exitcomtool="exit"
else
exitcomtool="return"
fi

conf=""
nightlyn="EXP"

#while [ $# -ne 0 ]; do
#        case $1 in
#            -n) nightlyn=$2; shift;;
#            -c) conf=$2; shift;;
#        esac
#        shift
#done

if [ "$ARDOC_NIGHTLY_NAME" = "" -o "$ARDOC_ARCH" = "" ]; then
echo "ardoc_oracle_starter: Error: ARDOC_NIGHTLY_NAME (${ARDOC_NIGHTLY_NAME}) or ARDOC_ARCH (${ARDOC_ARCH}) is not defined: no oracle initialization"
python $ARDOC_HOME/ardoc_send_mail.py -l "FATAL" -m "ARDOC_NIGHTLY_NAME or ARDOC_ARCH is not defined"
${exitcomtool} 1
fi

$ARDOC_HOME/ardoc_oracle_wrapper.sh 3 python $ARDOC_HOME/ardoc_oracle_starter.py -c $conf -n $nightlyn; st=$?
$ARDOC_HOME/ardoc_nightstat_wrapper.sh -n $ARDOC_NIGHTLY_NAME -s 0 --short

jobid=""
if [ "$st" -ne 0 ]; then
echo "ardoc_oracle_starter: Error: ardoc_oracle_starter.py returned $st"
python $ARDOC_HOME/ardoc_send_mail.py -l "FATAL" -m "ardoc_oracle_starter.py returned $st"
${exitcomtool} 1
else
  if [ -f ${ARDOC_GEN_CONFIG_AREA}/jobid.txt ]; then
     jobid=`cat ${ARDOC_GEN_CONFIG_AREA}/jobid.txt | head -1`
     echo "ardoc_oracle_starter: assigned job id $jobid"
  else
     echo "ardoc_oracle_starter: Error: job id text file was not created: ${ARDOC_GEN_CONFIG_AREA}/jobid.txt"
     python $ARDOC_HOME/ardoc_send_mail.py -l "FATAL" -m "job id text file was not created: ${ARDOC_GEN_CONFIG_AREA}/jobid.txt"
     ${exitcomtool} 1
  fi     
fi
if [[ ! ${jobid} =~ ^[0-9]+$ ]]; then
    echo "ardoc_oracle_starter: Error: job id is non digit: $jobid"
    python $ARDOC_HOME/ardoc_send_mail.py -l "FATAL" -m "job id is non digit: $jobid"
    ${exitcomtool} 1
fi
export ARDOC_JOBID="$jobid"

dirlog=`dirname $ARDOC_LOG`
flogora=$dirlog/ardoc_general.logora
$ARDOC_HOME/ardoc_oracle_wrapper.sh 3 python $ARDOC_HOME/ardoc_oracle_job_project_ini.py >> ${flogora} 2>&1; st01=$?
$ARDOC_HOME/ardoc_db_access -e -s "CONFIG" >> ${flogora} 2>&1; st03=$?

if [ "$st01" -ne 0 ]; then
echo "ardoc_oracle_starter: Error: ardoc_oracle_job_project_ini.py returned $st01"
python $ARDOC_HOME/ardoc_send_mail.py -l "FATAL" -m "ardoc_oracle_job_project_ini.py returned $st01"
${exitcomtool} 1
fi
if [ "$st03" -ne 0 ]; then
echo "ardoc_oracle_starter: Error: ardoc_db_access returned $st03"
python $ARDOC_HOME/ardoc_send_mail.py -l "FATAL" -m "ardoc_db_access -e -s \"CONFIG\" returned $st03"
fi
