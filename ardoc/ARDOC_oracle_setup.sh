st6=1
if [ -f /etc/redhat-release ]; then
cat /etc/redhat-release | grep "release 6" > /dev/null 2>&1; st6=$?
fi
processor=`uname -p`
export TNS_ADMIN=$HOME/oracle/admin

if [ "$processor" != 'aarch64' ]; then
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
echo "ardoc_oracle_setup.sh: oraversion $oraversion"
. $ORACLE_CERN/script/setoraenv.sh -s $oraversion
export LD_LIBRARY_PATH=$ORACLE_CERN/linux64/$oraversion/lib:$LD_LIBRARY_PATH
export TNS_ADMIN=$HOME/oracle/admin
fi
