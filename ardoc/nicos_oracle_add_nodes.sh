#!/bin/sh
comname=`basename $0`
if [ "$comname" = "nicos_oracle_add_nodes.sh" ]; then
exitcomtool="exit"
else
exitcomtool="return"
fi
export NICOS_HOME=`pwd`
source $NICOS_HOME/NICOS_oracle_setup.sh

array=("aibuild16-005" \
"aibuild16-006" \
"aibuild16-007" \
"aibuild16-008" \
"aibuild16-009" \
"aibuild16-010" \
"aibuild16-011" \
"aibuild16-012" \
"aibuild16-013" \
"aibuild16-014" \
"aibuild16-016" \
"aibuild16-018" \
"aibuild16-019" \
"aibuild16-020" \
"aibuild16-023" \
"aibuild16-028" \
"aibuild16-029" \
"aibuild16-031" \
"aibuild16-032" \
"aibuild16-033" \
"aibuild16-038" \
"aibuild16-043" \
"aibuild20-016" \
"aibuild20-017" \
"aibuild20-018" \
"aibuild20-019" \
"aibuild20-020" \
"aibuild20-041" \
"aibuild20-044")


for name in ${array[@]}
do
fname="${name}.cern.ch"
echo "nicos_oracle_add_nodes.sh: Info: ADDING $fname to table NODES"
python $NICOS_HOME/nicos_oracle_add_node.py -n $fname; st=?
done
