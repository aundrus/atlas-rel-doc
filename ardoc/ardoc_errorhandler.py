#!/usr/bin/env python3

#
# ARDOC - NIghtly COntrol System
# Author Alex Undrus <undrus@bnl.gov>
#
# ----------------------------------------------------------
# ardoc_errorhandler.py - Python migration of ardoc_errorhandler.pl
# ----------------------------------------------------------
#
import os
import sys
import re
import subprocess
from pathlib import Path
import stat
import argparse

def compar(name):
    """
    A comparison function used for sorting test names.
    """
    test_1 = name.split('___')
    val_c = ""
    if len(test_1) > 1:
        test_1.pop(0)  # Remove first element
        xxxx = test_1[0]
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
    for m in range(len(testd)):
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
    type_name = "test"
    
    # Get environment variables
    ARDOC_TESTLOG = os.environ.get("ARDOC_TESTLOG", "")
    ARDOC_RELHOME = os.environ.get("ARDOC_RELHOME", "")
    ARDOC_INTTESTS_DIR = os.environ.get("ARDOC_INTTESTS_DIR", "")
    ARDOC_WEBDIR = os.environ.get("ARDOC_WEBDIR", "")
    ARDOC_PROJECT_NAME = os.environ.get("ARDOC_PROJECT_NAME", "")
    ARDOC_NIGHTLY_NAME = os.environ.get("ARDOC_NIGHTLY_NAME", "")
    ARDOC_ARCH = os.environ.get("ARDOC_ARCH", "")
    ARDOC_FULL_ERROR_ANALYSIS = os.environ.get("ARDOC_FULL_ERROR_ANALYSIS", "")
    ARDOC_WORK_AREA = os.environ.get("ARDOC_WORK_AREA", "")
    ARDOC_TEST_DBFILE = os.environ.get("ARDOC_TEST_DBFILE", "")
    ARDOC_WEBPAGE = os.environ.get("ARDOC_WEBPAGE", "")
    release = os.environ.get("ARDOC_PROJECT_RELNAME", "")
    project = os.environ.get("ARDOC_PROJECT_NAME", "")
    nightly = os.environ.get("ARDOC_NIGHTLY_NAME", "")
    ARDOC_HOME = os.environ.get("ARDOC_HOME", "")

    ARDOC_TESTLOGDIR = Path(ARDOC_TESTLOG).parent
    ARDOC_TESTLOGDIR_TEMP = ARDOC_TESTLOGDIR / "temp"
    WTLogdir = f"ARDOC_TestLog_{release}"
    WTLogdir_full = Path(ARDOC_WEBDIR) / WTLogdir
    WTLogdir_full.mkdir(parents=True, exist_ok=True)

    testprepage = "ardoc_testprepage"
    dirdir = Path(ARDOC_RELHOME) / ARDOC_INTTESTS_DIR

    # Get all log files
    try: 
       allfiles = [
          f for f in os.listdir(ARDOC_TESTLOGDIR)
          if re.match(r"^.+log$", f)
       ]
    except OSError:
       allfiles = []

#    print("LIST ALL FILES in ",ARDOC_TESTLOGDIR," : ", allfiles)    

    list91 = [f for f in allfiles if not f.startswith("ardoc_")]
    list_files = [f for f in list91 if not f.endswith("logloglog")]

    # Sort files
    list_files.sort(key=compar)

#    print("LIST FILES ",list_files)
    filet_nn = Path(ARDOC_WORK_AREA) / f"{testprepage}_number"

    # Read test database
    test_db = []
    number_tests_db = 0
    if ARDOC_TEST_DBFILE and Path(ARDOC_TEST_DBFILE).is_file():
        try:
            with open(ARDOC_TEST_DBFILE) as f:
                test_db = [line.strip() for line in f if line.strip()]
            test_db_nn = [line for line in test_db if re.search(r'\w', line)]
            number_tests_db = len(test_db_nn)
            print(f"ardoc_errorhandler: number of tests in test_db {number_tests_db}")
        except OSError:
            pass

    # Write number of tests
    if filet_nn.exists():
        filet_nn.unlink()
    with open(filet_nn, 'w') as tf:
        tf.write(f"{number_tests_db}\n")

    filet = Path(ARDOC_WORK_AREA) / testprepage
    if filet.exists():
        filet.unlink()

    # Process test files - core functionality
    body = []
    body_count = 0
    body_prev = []
    addr_total = []
    addr_total_prev = []
    testname_subject_prev = ""
    dplusd_m = ""

    # Filter valid files
    listfiles1 = []
    for listfile in list_files:
        lin1 = listfile.replace(' ', '')
        if len(lin1) == 0:
            continue
        if listfile in ['.', '..'] or listfile.endswith('~'):
            continue
        listfiles1.append(listfile)

    with open(filet, 'w') as tf:
        for mlf, listfile in enumerate(listfiles1):
            listfields = listfile.split('.')
            listfields.pop()  # Remove extension
            listfile_base = '.'.join(listfields)
            listfileh = f"{listfile_base}.html"

            testname = listfile.split('.')[0]
            fields = testname.split('_')
            first_fields = []
            last_fields = []
            testdir = ""
            m_last = 0

            # Find valid directory path
            for m in range(len(fields)):
                first_fields.append(fields[m])
                testdir1 = '/'.join(first_fields)
                if testdir1 in ['.', '/', '/.']:
                    testdir1 = ""
                direc = Path(ARDOC_RELHOME) / prefix_relhome / testdir1
                if not direc.is_dir():
                    m_last = m
                    break
                testdir = testdir1

            for m in range(m_last, len(fields)):
                last_fields.append(fields[m])
            testname_base = '_'.join(last_fields)

            # Search for test suite
            testsuite = "undefined"
            addr_t = []

            for db_line in test_db:
                if db_line.startswith('#'):
                    continue
                lin1 = db_line.replace(' ', '')
                if len(lin1) == 0:
                    continue

                # Remove trailing/leading whitespaces
                lll = ' '.join(db_line.split())
                db_fields = lll.split()
                if len(db_fields) < 6:
                    continue

                testname1 = db_fields[1]
                testname2 = testname1.split('.')[0]
                testdir1 = db_fields[2]
                testdir2 = container_extractor(testdir1, ARDOC_RELHOME, prefix_relhome)
                testname_compar = f"{testdir2}_{testname2}"

                testsui = db_fields[4]
                testtime = db_fields[5]

                if testname_compar == testname:
                    for m in range(7, len(db_fields)):
                        addr_t.append(db_fields[m])
                    testsuite = testsui
                    testdir = testdir2
                    testname_base = testname2
                    break

            # Run error tester
            lower_AFEA = ARDOC_FULL_ERROR_ANALYSIS.lower()
            if lower_AFEA not in ["true", "yes"] and "CITest" in testname:
                # Light error analysis
                cmd = ["python3", f"{ARDOC_HOME}/ardoc_errortester.py", "-elst", testname, release]
            else:
                cmd = ["python3", f"{ARDOC_HOME}/ardoc_errortester.py", "-est", testname, release]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                strng1 = result.stdout.splitlines()
                if lower_AFEA in ["true", "yes"]:
                    print(f" full test_tester: {testname}_ERROR_MESSAGE {release} : {strng1}")
                elif lower_AFEA not in ["true", "yes"] and "CITest" in testname:
                    print(f" light test_tester: {testname}_ERROR_MESSAGE {release} : {strng1}")
                else:
                    print(f" test_tester: {testname}_ERROR_MESSAGE {release} : {strng1}")
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                strng1 = [""]

            strng = strng1[0] if strng1 else ""
            fieldstr = strng.split()
            patterns = fieldstr[3:] if len(fieldstr) > 3 else []

            tproblems = 0
            if len(fieldstr) > 0:
                if fieldstr[0] == "M" and strng:
                    tproblems = 0.5
                    print(f"ardoc_testhandler.py: test minor warnings in {testname} !!!")
                    print(f"                      pattern to blame: {patterns} !!!")
                elif fieldstr[0] == "W" and strng:
                    tproblems = 1
                    print(f"ardoc_testhandler.py: test warnings in {testname} !!!")
                    print(f"                      pattern to blame: {patterns} !!!")
                elif fieldstr[0] == "G" and strng:
                    tproblems = 2

            if tproblems == 2:
                print(f"ardoc_testhandler.py: test problems in {testname} !!!")
                print(f"                      pattern to blame: {patterns} !!!")

            # Get exit code
            fec_base = listfile.replace('.loglog', '.exitcode')
            fec = ARDOC_TESTLOGDIR / fec_base
            exitcod = "N/A"
            if fec.is_file():
                try:
                    with open(fec, 'r') as fk:
                        exitcod = fk.readline().strip()
                except OSError:
                    pass

            print(f"RECORD to testprepage: {testname} {listfileh} {testdir} {testname_base} {exitcod}")
            directory_field = fieldstr[2] if len(fieldstr) > 2 else ""
            patterns_str = ' '.join(patterns)
            tf.write(f"{testname} {testsuite} {listfileh} {tproblems} {exitcod} {testdir} {testname_base} {' '.join(addr_t)} \"\"\" {directory_field} \"\"\" \"{patterns_str}\" \n")

def main():
    """
    Main function - processes arguments and coordinates error analysis
    """
    # Parse arguments
    parser = argparse.ArgumentParser(description='ARDOC Error Handler')
    parser.add_argument('--jid', default='NONE', help='Job ID')
    args = parser.parse_args()
    
    jid = args.jid
    
    # Get environment variables
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
    ARDOC_LOGDIR = os.environ.get("ARDOC_LOGDIR", "")
    ARDOC_LOG = os.environ.get("ARDOC_LOG", "")
    ARDOC_TESTLOG = os.environ.get("ARDOC_TESTLOG", "")
    ARDOC_PROJECTBUILD_DIR = os.environ.get("ARDOC_PROJECTBUILD_DIR", "")
    ARDOC_WEBDIR = os.environ.get("ARDOC_WEBDIR", "")
    ARDOC_WEBPAGE = os.environ.get("ARDOC_WEBPAGE", "")
    ARDOC_NIGHTLY_NAME = os.environ.get("ARDOC_NIGHTLY_NAME", "")
    ARDOC_ARCH = os.environ.get("ARDOC_ARCH", "")
    ARDOC_RELHOME = os.environ.get("ARDOC_RELHOME", "")
    ARDOC_HOME = os.environ.get("ARDOC_HOME", "")

    ARDOC_TESTLOGDIR = Path(ARDOC_TESTLOG).parent
    prevdir = os.getcwd()

    # Mail settings
    nomail = 1  # Mail disabled by default
    nomail_t = [1, 1, 1]  # Test mail settings

    # File paths
    fileorig = ARDOC_DBFILE
    base_file = Path(ARDOC_DBFILE).name
    filename = ARDOC_DBFILE
    filename_gen = ARDOC_DBFILE
    filename_res = ARDOC_DBFILE
    prepage = "ardoc_prepage"
    prepage_problems = "ardoc_prepage_problems"
    testprepage = "ardoc_testprepage"
    release = ARDOC_PROJECT_RELNAME
    project = ARDOC_PROJECT_NAME
    nightly = ARDOC_NIGHTLY_NAME
    ARDOC_LOGDIR = Path(ARDOC_LOG).parent

    # Process test results
    print("========1==")
    ardoc_testhandler(2)  # Process integration/unit tests
    print("========2==")
    
    # Change to build directory
    ndir = Path(ARDOC_RELHOME) / ARDOC_PROJECTBUILD_DIR
    os.chdir(ndir)

    # Setup web directories
    WLogdir = f"ARDOC_Log_{release}"
    WTLogdir = f"ARDOC_TestLog_{release}"
    ndir = Path(ARDOC_WEBDIR) / WLogdir
    ndir.mkdir(parents=True, exist_ok=True)

    filet = Path(ARDOC_WORK_AREA) / testprepage
    file = Path(ARDOC_WORK_AREA) / prepage

    part_t = "no"
    if part_t == "no":
        # Copy log files to web directory
        try:
            allcpfiles = os.listdir(ARDOC_LOGDIR)
            listf1 = [f for f in allcpfiles if not re.search(r'\.loglog.+$', f)]
            listf = [f for f in listf1 if not f.endswith('.loglog')]
            
            for lf in listf:
                if lf in ['.', '..'] or lf.endswith('~'):
                    continue
                src = Path(ARDOC_LOGDIR) / lf
                dst = Path(ARDOC_WEBDIR) / WLogdir / lf
                if src.is_file():
                    try:
                        subprocess.run(['cp', '-pf', str(src), str(dst)], check=True)
                    except subprocess.CalledProcessError:
                        pass
        except OSError:
            pass

        # Remove specific files from web directory
        general_log = Path(ARDOC_WEBDIR) / WLogdir / "ardoc_general.loglog"
        if general_log.exists():
            general_log.unlink()

        # Remove prepage file if it exists
        if file.exists():
            file.unlink()

        # Read database file
        try:
            with open(filename_gen, 'r') as dbf:
                dbc = [line.strip() for line in dbf]
        except OSError:
            dbc = []

        # Build container address mapping
        container_addr = {}
        for line in dbc:
            if line.startswith('#'):
                continue
            lin1 = line.replace(' ', '')
            if len(lin1) == 0:
                continue
            lll = ' '.join(line.split())
            fields = lll.split()
            if len(fields) < 2:
                continue
            package = fields[0]
            tag = fields[1]
            addr = fields[3:] if len(fields) > 3 else []
            
            package_fields = package.split("/")
            if len(package_fields) == 1:
                container_addr[package] = addr

        # Process packages - core functionality for prepage generation
        try:
            with open(filename, 'r') as dbf:
                dbc = [line.strip() for line in dbf]
        except OSError:
            dbc = []

        scount = 0
        totcount = 0

        with open(file, 'w') as fl:
            for line in dbc:
                if line.startswith('#'):
                    continue
                lin1 = line.replace(' ', '')
                if len(lin1) == 0:
                    continue

                lll = ' '.join(line.split())
                fields = lll.split()
                if len(fields) < 2:
                    continue
                
                package = fields[0]
                tag = fields[1]
                addr = fields[2:] if len(fields) > 2 else []

                pkgn = package.replace('/', '_')
                if not pkgn:
                    pkgn = package
                pkgbs = Path(package).name
                fieldsp = package.split("/")
                cont_addr = []
                
                if len(fields) > 1:
                    package_cont = fieldsp[0]
                    if package_cont in container_addr:
                        cont_addr = container_addr[package_cont]
                        container_addr[package] = addr

                # Run error tester for build logs
                cmd = ["python3", f"{ARDOC_HOME}/ardoc_errortester.py", "-es", pkgn, release, filename, package]
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    strng1 = result.stdout.splitlines()
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    strng1 = [""]

                strng = strng1[0] if strng1 else ""
                fieldstr = strng.split()
                patterns = fieldstr[3:] if len(fieldstr) > 3 else []

                problems = 0
                if len(fieldstr) > 0:
                    if fieldstr[0] == "G" and strng:
                        problems = 2
                        print(f"ardoc_errorhandler.py: error level build problems with {pkgn} of {release} !!!")
                        print(f"ardoc_errorhandler.py: offending pattern: {patterns}")
                    elif fieldstr[0] == "W" and strng:
                        problems = 1
                        print(f"ardoc_errorhandler.py: warning level build problems with {pkgn} of {release} !!!")
                        print(f"ardoc_errorhandler.py: offending pattern: {patterns}")
                    elif fieldstr[0] == "M" and strng:
                        problems = 0.5
                        print(f"ardoc_errorhandler.py: minor warning level build problems with {pkgn} of {release} !!!")
                        print(f"ardoc_errorhandler.py: offending pattern: {patterns}")

                # Check for test problems
                test_problems = [0, 0, 0]
                type_names = ["", "qatest", "test"]
                i_init = 2

                for i in range(i_init, 3):  # i=2: unit tests
                    try:
                        with open(filet, 'r') as ttt:
                            ttpp = [line.strip() for line in ttt]
                    except OSError:
                        ttpp = []

                    comp1 = pkgn.lower()
                    test_problems[i] = 0

                    for test_line in ttpp:
                        if test_line.startswith('#'):
                            continue
                        lin1 = test_line.replace(' ', '')
                        if len(lin1) == 0:
                            continue
                        lll = ' '.join(test_line.split())
                        test_fields = lll.split()
                        if len(test_fields) < 4:
                            continue
                        
                        testname = test_fields[0]
                        trecent_logfiles = test_fields[2]
                        tproblems = float(test_fields[3])
                        
                        comp2 = testname.lower()
                        if comp1 == comp2:
                            test_problems[i] = tproblems
                            break

                    if test_problems[i] == 0.5:
                        print(f"ardoc_errorhandler.py: {type_names[i]} minor warnings with {pkgn} !!!")
                    elif test_problems[i] == 1:
                        print(f"ardoc_errorhandler.py: {type_names[i]} warnings with {pkgn} !!!")
                    elif test_problems[i] >= 2:
                        print(f"ardoc_errorhandler.py: {type_names[i]} problems with {pkgn} !!!")

                # Find log files
                try:
                    allfiles = os.listdir(ARDOC_LOGDIR)
                except OSError:
                    allfiles = []
                
                stg = f"{pkgn}.loglog"
                listx = [f for f in allfiles if f == stg]
                list_files = [f for f in listx if f not in ['.', '..']]
                
                if list_files:
                    # Sort by modification time, newest first
                    list_files.sort(key=lambda x: os.path.getmtime(Path(ARDOC_LOGDIR) / x), reverse=True)
                    listfilesf = list_files[0]
                else:
                    listfilesf = ""

                if listfilesf:
                    listfields = listfilesf.split('.')
                    listfields.pop()
                    listfilesf_base = '.'.join(listfields)
                    listfilesh = f"{listfilesf_base}.html"
                else:
                    # Generate missing logfile
                    lf = Path(ARDOC_LOGDIR) / f"{pkgn}.loglog"
                    with open(lf, 'w') as ff:
                        ff.write(" ARDOC determined that make did nothing for this package.\n")
                        ff.write(" Error in package configuration or structure is possible.\n")
                    
                    listfilesf = f"{ARDOC_LOGDIR}/{pkgn}.loglog"
                    listfilesh = f"{ARDOC_LOGDIR}/{pkgn}.html"
                    
                    # Copy files
                    src = Path(ARDOC_LOGDIR) / f"{pkgn}.loglog"
                    dst1 = Path(ARDOC_WEBDIR) / WLogdir / f"{pkgn}.html"
                    dst2 = Path(ARDOC_LOGDIR) / f"{pkgn}.html"
                    try:
                        subprocess.run(['cp', '-pf', str(src), str(dst1)], check=True)
                        subprocess.run(['cp', '-pf', str(src), str(dst2)], check=True)
                    except subprocess.CalledProcessError:
                        pass
                    
                    problems = 2
                    fieldstr = ["G", pkgn.replace('_', '/'), "", "absent logfile"]
                    patterns = ["absent logfile"]
                    print(f"ardoc_errorhandler: generating missing logfile {fieldstr}")
                    strng = f"G {fieldstr[1]} . {fieldstr[3]}"

                listfiles = Path(listfilesh).name
                recent_logfile = listfiles

                pkgcontainer = Path(package).parent
                if str(pkgcontainer) == ".":
                    pkgcontainer = "N/A"
                pkgbase = Path(package).name

                # Convert addresses to lowercase
                addr_lower = [a.lower() for a in addr]
                lin1 = ' '.join(addr_lower)
                line_clean = lin1.replace(' ', '')

                totcount += 1
                if problems in [2, 1]:
                    scount += 1

                # Write to prepage file
                directory_field = fieldstr[2] if len(fieldstr) > 2 else ""
                patterns_str = ' '.join(patterns)
                
                if line_clean and line_clean != "-":
                    fl.write(f"{pkgbase} {pkgcontainer} {recent_logfile} {problems} {test_problems[1]} {test_problems[2]} {' '.join(addr)} \"\"\" {directory_field} \"\"\" {patterns_str}\n")
                else:
                    fl.write(f"{pkgbase} {pkgcontainer} {recent_logfile} {problems} {test_problems[1]} {test_problems[2]} {' '.join(addr)} \"\"\" {directory_field} \"\"\" {patterns_str}\n")

        # Calculate percentage of problems
        percen = 0
        if totcount != 0:
            percen = int((scount / totcount) * 100)
            if percen > 50:
                print(f"ardoc_errorhandler.py: high percentage of packages with compilation problems : {percen} : emails disabled")
                nomail = 2
            else:
                print(f"ardoc_errorhandler.py: percentage of packages with compilation problems : {percen}")

    os.chdir(prevdir)

if __name__ == "__main__":
    main()
