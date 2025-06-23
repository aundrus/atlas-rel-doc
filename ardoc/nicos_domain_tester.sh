#!/bin/sh
command=$@

export NICOS_GEN_CONFIG_AREA=/tmp/workarea-MR-60463-2023-02-21-22-47-qYc/nicos_local_gen_config_area
export NICOS_PROJECT_ARRAY="Athena"
export NICOS_PROJECT_NAME="Athena"
export NICOS_ARCH="x86_64-centos7-gcc112-opt"
export NICOS_EPOCH="1677016020.657166746"
export NICOS_HOME="/afs/cern.ch/atlas/software/dist/ci/git_ci/nicos_doc_builder_CI01_dev_V2/nicos_doc_builder"
export MR_TRAINING_DOMAIN="Tracking/Acts"

${NICOS_HOME}/nicos_oracle_domains_wrapper.sh
stat=$?
echo "result $stat"
exit $stat
