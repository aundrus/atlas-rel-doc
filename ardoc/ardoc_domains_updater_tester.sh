#!/bin/sh
command=$@

export ARDOC_NIGHTLY_NAME=MR-CI-builds
export ARDOC_GEN_CONFIG_AREA=/tmp/workarea-MR-65825-2023-09-15-15-48-jDD/ardoc_local_gen_config_area
export ARDOC_PROJECT_ARRAY="Athena"
export ARDOC_PROJECT_NAME="Athena"
export ARDOC_PROJECT_RELNAME="MR-65825-2023-09-15-15-48"
export ARDOC_ARCH="x86_64-centos7-gcc112-opt"
export ARDOC_EPOCH=1694785727.384203602
export ARDOC_HOME="/afs/cern.ch/atlas/software/dist/ci/git_ci/ardoc_doc_builder_CI01_dev_V2/ardoc_doc_builder/"
export CI_RESULTS_DICT=/build2/ci-builds/main/results593177.py
export gitlabMergeRequestId="593177"
export gitlabMergeRequestIid="65825"
export gitlabTargetBranch="main"

${ARDOC_HOME}/ardoc_oracle_domains_updater_wrapper.sh
stat=$?
echo "result $stat"
exit $stat
