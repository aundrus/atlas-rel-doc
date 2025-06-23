st6=1
st7=1
if [ -f /etc/redhat-release ]; then
cat /etc/redhat-release | grep "release 6" > /dev/null 2>&1; st6=$?
fi
if [ -f /etc/redhat-release ]; then
cat /etc/redhat-release | grep "release 7" > /dev/null 2>&1; st7=$?
fi

platf="x86_64-slc5-gcc43-opt"
if [ "$st6" -eq 0 ]; then
platf=x86_64-slc6-gcc46-opt
fi
#if [ "$st7" -eq 0 ]; then
#platf=x86_64-centos7-gcc8-opt
#fi         

unset PYTHONHOME
unset PYTHONPATH

export TNS_ADMIN=$HOME/oracle/admin
export ORACLE_CERN=/afs/cern.ch/project/oracle
if [ "${st6}" -eq 0 ]; then
  oraversion=`$ORACLE_CERN/script/setoraenv.sh -l | grep  "^181" | grep "\-\->" | head -1 | cut -f1 -d' '`
  [[ "$oraversion" = '' ]] && oraversion=`$ORACLE_CERN/script/setoraenv.sh -l | grep  "^18" | grep "\-\->" | head -1 | cut -f1 -d' '`
else
  oraversion=`$ORACLE_CERN/script/setoraenv.sh -l | grep  "^192" | grep "\-\->" | head -1 | cut -f1 -d' '`
  [[ "$oraversion" = '' ]] && oraversion=`$ORACLE_CERN/script/setoraenv.sh -l | grep  "^19" | grep "\-\->" | head -1 | cut -f1 -d' '`
#  oraversion=`$ORACLE_CERN/script/setoraenv.sh -l | grep  "^181" | grep "\-\->" | head -1 | cut -f1 -d' '`                                  
#  [[ "$oraversion" = '' ]] && oraversion=`$ORACLE_CERN/script/setoraenv.sh -l | grep  "^18" | grep "\-\->" | head -1 | cut -f1 -d' '`
fi
echo "NICOS_oracle_setup.sh: oraversion $oraversion"
. $ORACLE_CERN/script/setoraenv.sh -s $oraversion
export LD_LIBRARY_PATH=$ORACLE_CERN/linux64/$oraversion/lib:$LD_LIBRARY_PATH
export PATH=/cvmfs/sft.cern.ch/lcg/external/Python/2.6.5p2/${platf}/bin:$PATH
export LD_LIBRARY_PATH=/cvmfs/sft.cern.ch/lcg/external/Python/2.6.5p2/${platf}/lib:$LD_LIBRARY_PATH
export PYTHONPATH=/cvmfs/sft.cern.ch/lcg/external/pytools/1.8_python2.6/${platf}/lib/python2.6/site-packages:$PYTHONPATH
export TNS_ADMIN=$HOME/oracle/admin
