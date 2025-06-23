export ARDOC_HOME=/afs/cern.ch/atlas/software/dist/ci/ardoc_dev
if [ ! -d /build1 ]; then
echo "Error: /build1 does not exist"
return
fi
[[ ! -d /build1/script_tests/work_area ]] && mkdir -p /build1/script_tests/work_area

export ARDOC_LOG=/build1/script_tests/work_area
cd /build1/script_tests
