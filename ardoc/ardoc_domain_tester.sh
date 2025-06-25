#!/bin/sh
command=$@

export ARDOC_GEN_CONFIG_AREA=/tmp/workarea-MR-60463-2023-02-21-22-47-qYc/ardoc_local_gen_config_area
export ARDOC_PROJECT_ARRAY="Athena"
export ARDOC_PROJECT_NAME="Athena"
export ARDOC_ARCH="x86_64-centos7-gcc112-opt"
export ARDOC_EPOCH="1677016020.657166746"
export ARDOC_HOME="/afs/cern.ch/atlas/software/dist/ci/git_ci/ardoc_doc_builder_CI01_dev_V2/ardoc_doc_builder"
export MR_TRAINING_DOMAIN="Tracking/Acts"

${ARDOC_HOME}/ardoc_oracle_domains_wrapper.sh
stat=$?
echo "result $stat"
exit $stat
