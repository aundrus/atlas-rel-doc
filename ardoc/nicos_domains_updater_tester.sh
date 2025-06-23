#!/bin/sh
command=$@

export NICOS_NIGHTLY_NAME=MR-CI-builds
export NICOS_GEN_CONFIG_AREA=/tmp/workarea-MR-65825-2023-09-15-15-48-jDD/nicos_local_gen_config_area
export NICOS_PROJECT_ARRAY="Athena"
export NICOS_PROJECT_NAME="Athena"
export NICOS_PROJECT_RELNAME="MR-65825-2023-09-15-15-48"
export NICOS_ARCH="x86_64-centos7-gcc112-opt"
export NICOS_EPOCH=1694785727.384203602
export NICOS_HOME="/afs/cern.ch/atlas/software/dist/ci/git_ci/nicos_doc_builder_CI01_dev_V2/nicos_doc_builder/"
export CI_RESULTS_DICT=/build2/ci-builds/main/results593177.py
export gitlabMergeRequestId="593177"
export gitlabMergeRequestIid="65825"
export gitlabTargetBranch="main"

${NICOS_HOME}/nicos_oracle_domains_updater_wrapper.sh
stat=$?
echo "result $stat"
exit $stat
