#!/usr/bin/env python3

#
# ARDOC - NIghtly COntrol System
# Author Alex Undrus <undrus@bnl.gov>
#
# ----------------------------------------------------------
# ardoc_errorhandler.py
# ----------------------------------------------------------
#
import os
import sys
import re
import subprocess
from pathlib import Path
import stat

def compar(name):
    """
    A comparison function used for sorting.
    """
    test_1 = name.split('___')
    val_c = ""
    if len(test_1) > 1:
        xxxx = test_1[1]
        test_11 = xxxx.split("__")
        xxxx = test_11[0]
        test_11[0] = xxxx + "00"
        val_c = "__".join(test_11)
    else:
        test_2 = name.split("__")
        if len(test_2) > 1:
            xxxx = test_2.pop(0)
            xxyy = xxxx.split("_")
            xxnn = xxyy.pop()
            test_2[0] = test_2[0] + xxnn
            val_c = "__".join(test_2)
        else:
            val_c = test_2[0]
    return val_c

def container_extractor(testdirx, ardoc_relhome, prefix_relhome):
    """
    Extracts a container name from a path.
    """
    testd = testdirx.split('/')
    for m in range(len(testd), 0, -1):
        testj = '/'.join(testd)
        filfil = Path(ardoc_relhome) / prefix_relhome / testj / "cmt/version.cmt"
        if filfil.is_file():
            break
        testd.pop()
    return '_'.join(testd)

def ardoc_testhandler(par):
    """
    Handles test results.
    if par = 1 -> qa tests, if par != 1 int and unit tests
    """
    prefix_relhome = "aogt8"
    type = "test"
    
    ARDOC_TESTLOG = os.environ.get("ARDOC_TESTLOG", "")
    ARDOC_RELHOME = os.environ.get("ARDOC_RELHOME", "")
    ARDOC_INTTESTS_DIR = os.environ.get("ARDOC_INTTESTS_DIR", "")
    ARDOC_INTTESTS_FILES = os.environ.get("ARDOC_INTTESTS_FILES", "")
    ATN_HOME = os.environ.get("ATN_HOME", "")
    ARDOC_WEBDIR = os.environ.get("ARDOC_WEBDIR", "")
    ARDOC_PROJECT_NAME = os.environ.get("ARDOC_PROJECT_NAME", "")
    ARDOC_NIGHTLY_NAME = os.environ.get("ARDOC_NIGHTLY_NAME", "")
    ARDOC_ARCH = os.environ.get("ARDOC_ARCH", "")
    ARDOC_FULL_ERROR_ANALYSIS = os.environ.get("ARDOC_FULL_ERROR_ANALYSIS", "")
    ARDOC_WORK_AREA = os.environ.get("ARDOC_WORK_AREA", "")
    ARDOC_TEST_DBFILE = os.environ.get("ARDOC_TEST_DBFILE", "")
    release = os.environ.get("ARDOC_PROJECT_RELNAME", "")
    ARDOC_HOME = os.environ.get("ARDOC_HOME", "")

    ARDOC_TESTLOGDIR = Path(ARDOC_TESTLOG).parent
    ARDOC_TESTLOGDIR_TEMP = ARDOC_TESTLOGDIR / "temp"
    WTLogdir = f"ARDOC_TestLog_{release}"
    WTLogdir_full = Path(ARDOC_WEBDIR) / WTLogdir
    WTLogdir_full.mkdir(parents=True, exist_ok=True)

    testprepage = "ardoc_testprepage"
    dirdir = Path(ARDOC_RELHOME) / ARDOC_INTTESTS_DIR

    allfiles = [f for f in os.listdir(ARDOC_TESTLOGDIR) if f.endswith(".log")]
    list91 = [f for f in allfiles if not f.startswith("ardoc_")]
    list_files = [f for f in list91 if not f.endswith("logloglog")]

    list_files.sort(key=compar)

    filet_nn = Path(ARDOC_WORK_AREA) / f"{testprepage}_number"

    test_db = []
    number_tests_db = 0
    if ARDOC_TEST_DBFILE and Path(ARDOC_TEST_DBFILE).is_file():
        with open(ARDOC_TEST_DBFILE) as f:
            test_db = [line.strip() for line in f if line.strip()]
        number_tests_db = len(test_db)
        print(f"ardoc_errorhandler: number of tests in test_db {number_tests_db}")

    with open(filet_nn, "w") as f:
        f.write(f"{number_tests_db}\n")

    filet = Path(ARDOC_WORK_AREA) / testprepage
    if filet.exists():
        filet.unlink()

    with open(filet, "w") as tf:
        body = []
        body_count = 0
        body_prev = []
        addr_total = []
        addr_total_prev = []
        testname_subject_prev = ""
        dplusd_m = ""

        listfiles1 = [f for f in list_files if f.strip() and not f.startswith('.') and not f.endswith('~')]

        for mlf, listfile in enumerate(listfiles1):
            listfile_base = '.'.join(listfile.split('.')[:-1])
            listfileh = f"{listfile_base}.html"
            testname = listfile.split('.')[0]
            fields = testname.split('_')
            first_fields = []
            last_fields = []
            testdir = ""
            m_last = 0

            for m, field in enumerate(fields):
                first_fields.append(field)
                testdir1 = "/".join(first_fields)
                if testdir1 in (".", "/", "/."):
                    testdir1 = ""
                direc = Path(ARDOC_RELHOME) / prefix_relhome / testdir1
                if not direc.is_dir():
                    m_last = m
                    break
                testdir = testdir1
            
            last_fields = fields[m_last:]
            testname_base = "_".join(last_fields)

            testsuite = "undefined"
            addr_t = []

            for line in test_db:
                if line.startswith('#'):
                    continue
                lll = ' '.join(line.split())
                fields_db = lll.split()
                testname1 = fields_db[1]
                testname2 = testname1.split('.')[0]
                testdir1 = fields_db[2]
                testdir2 = container_extractor(testdir1, ARDOC_RELHOME, prefix_relhome)
                testname_compar = f"{testdir2}_{testname2}"
                
                if testname_compar == testname:
                    testsui = fields_db[4]
                    testtime = fields_db[5]
                    addr_t.extend(fields_db[7:])
                    testsuite = testsui
                    testdir = testdir2
                    testname_base = testname2
                    break
            
            strng1 = []
            lower_AFEA = ARDOC_FULL_ERROR_ANALYSIS.lower()
            errortester_cmd = ["python3", f"{ARDOC_HOME}/ardoc_errortester.py"]
            if lower_AFEA not in ("true", "yes") and "CITest" in testname:
                errortester_cmd.extend(["-elst", testname, release])
                print(f" light test_tester: {testname}_ERROR_MESSAGE {release} : ", end="")
            else:
                errortester_cmd.extend(["-est", testname, release])
                if lower_AFEA in ("true", "yes"):
                    print(f" full test_tester: {testname}_ERROR_MESSAGE {release} : ", end="")
                else:
                    print(f" test_tester: {testname}_ERROR_MESSAGE {release} : ", end="")
            
            result = subprocess.run(errortester_cmd, capture_output=True, text=True)
            strng1 = result.stdout.strip().split('\n')
            print(' '.join(strng1))

            strng = strng1[0] if strng1 else ""
            fieldstr = strng.split()
            patterns = fieldstr[3:] if len(fieldstr) > 3 else []
            
            tproblems = 0
            if strng.startswith("M"):
                tproblems = 0.5
                print(f"ardoc_testhandler.py: test minor warnings in {testname} !!!")
                print(f"                      pattern to blame: {' '.join(patterns)} !!!")
            elif strng.startswith("W"):
                tproblems = 1
                print(f"ardoc_testhandler.py: test warnings in {testname} !!!")
                print(f"                      pattern to blame: {' '.join(patterns)} !!!")
            elif strng.startswith("G"):
                tproblems = 2

            if tproblems == 2:
                print(f"ardoc_testhandler.py: test problems in {testname} !!!")
                print(f"                      pattern to blame: {' '.join(patterns)} !!!")
                
                # Email logic would go here, it is complex and commented out in original
                # For now, skipping the email part as it was commented in perl.

            fec_base = listfile.replace('.loglog', '.exitcode')
            fec = ARDOC_TESTLOGDIR / fec_base
            exitcod = "N/A"
            if fec.is_file():
                with open(fec) as f:
                    exitcod = f.readline().strip()
            
            print(f"RECORD to testprepage: {testname} {listfileh} {testdir} {testname_base} {exitcod}")
            tf.write(f"{testname} {testsuite} {listfileh} {tproblems} {exitcod} {testdir} {testname_base} {' '.join(addr_t)} \"\"\" {fieldstr[2] if len(fieldstr) > 2 else ''} \"\"\" \"{' '.join(patterns)}\" \n")

    # Copy log files to web directory
    for lf in os.listdir(ARDOC_TESTLOGDIR):
        if lf.endswith('.loglog') or lf.endswith('.html'):
            continue
        lf_full = ARDOC_TESTLOGDIR / lf
        if lf_full.is_file() and not lf.startswith('.') and not lf.endswith('~'):
            lf_size = lf_full.stat().st_size
            dest_file = WTLogdir_full / lf
            with open(dest_file, "w") as df:
                if lf_size <= 4000000:
                    df.write("ARDOC NOTICE: THIS FILE IS ALSO AVAILABLE AT:\n")
                    df.write(f"{lf_full}\n")
                    # with open(lf_full) as sf:
                    #     df.write(sf.read())
                else:
                    df.write("ARDOC NOTICE: THIS FILE IS TRUNCATED DUE TO LARGE SIZE\n")
                    df.write(f"LARGER, POSSIBLY NOT TRUNCATED COPY IS {lf_full}\n")
                    # with open(lf_full) as sf:
                    #     df.write(sf.read(4000000))

def main():
    """
    Main function for the script.
    """
    ARDOC_WORK_AREA = os.environ.get("ARDOC_WORK_AREA", "")
    ARDOC_DBFILE = os.environ.get("ARDOC_DBFILE", "")
    ARDOC_MAIL = os.environ.get("ARDOC_MAIL", "")
    ARDOC_MAIL_WARNINGS = os.environ.get("ARDOC_MAIL_WARNINGS", "")
    ARDOC_MAIL_MINOR_WARNINGS = os.environ.get("ARDOC_MAIL_MINOR_WARNINGS", "")
    ARDOC_MAIL_UNIT_TESTS = os.environ.get("ARDOC_MAIL_UNIT_TESTS", "")
    ARDOC_MAIL_INT_TESTS = os.environ.get("ARDOC_MAIL_INT_TESTS", "")
    ARDOC_MAIL_PROJECT_KEYS = os.environ.get("ARDOC_MAIL_PROJECT_KEYS", "")
    ARDOC_PROJECT_RELNAME = os.environ.get("ARDOC_PROJECT_RELNAME", "")
    ARDOC_PROJECT_NAME = os.environ.get("ARDOC_PROJECT_NAME", "")
    ARDOC_LOG = os.environ.get("ARDOC_LOG", "")
    ARDOC_LOGDIR = os.environ.get("ARDOC_LOGDIR", "")
    ARDOC_TESTLOG = os.environ.get("ARDOC_TESTLOG", "")
    ARDOC_PROJECTBUILD_DIR = os.environ.get("ARDOC_PROJECTBUILD_DIR", "")
    ARDOC_WEBDIR = os.environ.get("ARDOC_WEBDIR", "")
    ARDOC_WEBPAGE = os.environ.get("ARDOC_WEBPAGE", "")
    ARDOC_NIGHTLY_NAME = os.environ.get("ARDOC_NIGHTLY_NAME", "")
    ARDOC_ARCH = os.environ.get("ARDOC_ARCH", "")
    ARDOC_RELHOME = os.environ.get("ARDOC_RELHOME", "")
    ARDOC_HOME = os.environ.get("ARDOC_HOME", "")

    if not ARDOC_LOGDIR and ARDOC_LOG:
        ARDOC_LOGDIR = Path(ARDOC_LOG).parent

    prevdir = os.getcwd()

    nomail = 1
    nomail_t = [1, 1, 1]

    filename = ARDOC_DBFILE
    prepage = "ardoc_prepage"
    testprepage = "ardoc_testprepage"
    release = ARDOC_PROJECT_RELNAME
    project = ARDOC_PROJECT_NAME
    nightly = ARDOC_NIGHTLY_NAME

    # NO TEST RESULTS PROCESSING AT THIS MOMENT
    ardoc_testhandler(2)

    ndir = Path(ARDOC_RELHOME) / ARDOC_PROJECTBUILD_DIR
    os.chdir(ndir)

    WLogdir = f"ARDOC_Log_{release}"
    ndir_web = Path(ARDOC_WEBDIR) / WLogdir
    ndir_web.mkdir(parents=True, exist_ok=True)

    filet = Path(ARDOC_WORK_AREA) / testprepage
    file_prepage = Path(ARDOC_WORK_AREA) / prepage

    part_t = "no"
    if part_t == "no":
        for lf in os.listdir(ARDOC_LOGDIR):
            if not lf.endswith('.loglog') and not lf.startswith('.') and not lf.endswith('~'):
                subprocess.run(["cp", "-pf", str(Path(ARDOC_LOGDIR) / lf), str(ndir_web / ".")])
        
        (ndir_web / "ardoc_general.loglog").unlink(missing_ok=True)
        
        if file_prepage.exists():
            file_prepage.unlink()

        dbc = []
        if Path(filename).is_file():
            with open(filename) as f:
                dbc = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        container_addr = {}
        for line in dbc:
            fields = line.split()
            package = fields[0]
            addr = fields[3:]
            if '/' not in package:
                container_addr[package] = addr
        
        scount = 0
        totcount = 0

        with open(file_prepage, "w") as fl:
            for line in dbc:
                fields = line.split()
                package = fields[0]
                tag = fields[1]
                addr = fields[2:]
                pkgn = package.replace('/', '_')
                if not pkgn:
                    pkgn = package
                
                errortester_cmd = ["python3", f"{ARDOC_HOME}/ardoc_errortester.py", "-es", pkgn, release, filename, package]
                result = subprocess.run(errortester_cmd, capture_output=True, text=True)
                strng1 = result.stdout.strip()
                
                fieldstr = strng1.split()
                patterns = fieldstr[3:] if len(fieldstr) > 3 else []
                
                problems = 0
                if strng1.startswith("G"):
                    problems = 2
                    print(f"ardoc_errorhandler.py: error level build problems with {pkgn} of {release} !!!")
                    print(f"ardoc_errorhandler.py: offending pattern: {' '.join(patterns)}")
                elif strng1.startswith("W"):
                    problems = 1
                    print(f"ardoc_errorhandler.py: warning level build problems with {pkgn} of {release} !!!")
                    print(f"ardoc_errorhandler.py: offending pattern: {' '.join(patterns)}")
                elif strng1.startswith("M"):
                    problems = 0.5
                    print(f"ardoc_errorhandler.py: minor warning level build problems with {pkgn} of {release} !!!")
                    print(f"ardoc_errorhandler.py: offending pattern: {' '.join(patterns)}")

                # More logic to be ported here

    os.chdir(prevdir)


if __name__ == "__main__":
    main()
