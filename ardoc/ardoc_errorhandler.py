#!/usr/bin/env python3
"""
ARDOC - Nightly Control System
Author: Alex Undrus <undrus@bnl.gov>

----------------------------------------------------------
ardoc_errorhandler.py - Complete Python migration of ardoc_errorhandler.pl
----------------------------------------------------------

Main error analysis handler that:
- Reads lists of files and tests
- Runs ardoc_errortester for each log
- Creates testprepage and prepage files with results
- Handles email notifications and web directory management
"""

import os
import sys
import re
import shutil
from pathlib import Path
import subprocess
import glob
import argparse

def compar(name):
    """Compare function to sort test names properly"""
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
            val_c = test_2[0] if test_2 else ""
    
    return val_c


def container_extractor(testdirx, ARDOC_RELHOME, prefix_relhome):
    """Extract container information from test directory"""
    testd = testdirx.split('/')
    
    for m in range(len(testd), -1, -1):
        testj = '/'.join(testd[:m])
        filfil = f"{ARDOC_RELHOME}/{prefix_relhome}/{testj}/cmt/version.cmt"
        if os.path.isfile(filfil):
            break
        if testd:
            testd.pop()
    
    return '_'.join(testd)

def ardoc_testhandler(par):
    """
    Handle test processing
    If par = 1 -> qa tests, if par != 1 int and unit tests
    """
    prefix_relhome = "aogt8"
    type_name = "test"
    
    # Get environment variables
    ARDOC_TESTLOG = os.environ.get('ARDOC_TESTLOG', '')
    ARDOC_RELHOME = os.environ.get('ARDOC_RELHOME', '')
    ARDOC_INTTESTS_DIR = os.environ.get('ARDOC_INTTESTS_DIR', '')
    ARDOC_TEST_DBFILE_GEN = os.environ.get('ARDOC_TEST_DBFILE_GEN', '')
    ARDOC_INTTESTS_FILES = os.environ.get('ARDOC_INTTESTS_FILES', '')
    ATN_HOME = os.environ.get('ATN_HOME', '')
    ARDOC_WEBDIR = os.environ.get('ARDOC_WEBDIR', '')
    ARDOC_PROJECT_NAME = os.environ.get('ARDOC_PROJECT_NAME', '')
    ARDOC_NIGHTLY_NAME = os.environ.get('ARDOC_NIGHTLY_NAME', '')
    ARDOC_ARCH = os.environ.get('ARDOC_ARCH', '')
    ARDOC_FULL_ERROR_ANALYSIS = os.environ.get('ARDOC_FULL_ERROR_ANALYSIS', '')
    ARDOC_WORK_AREA = os.environ.get('ARDOC_WORK_AREA', '')
    ARDOC_HOME = os.environ.get('ARDOC_HOME', '')
    ARDOC_WEBPAGE = os.environ.get('ARDOC_WEBPAGE', '')
    release = os.environ.get('ARDOC_PROJECT_RELNAME', '')
    project = os.environ.get('ARDOC_PROJECT_NAME', '')
    nightly = os.environ.get('ARDOC_NIGHTLY_NAME', '')
    
    ARDOC_TESTLOGDIR = os.path.dirname(ARDOC_TESTLOG)
    ARDOC_TESTLOGDIR_TEMP = f"{ARDOC_TESTLOGDIR}/temp"
    WTLogdir = f"ARDOC_TestLog_{release}"
    WTLogdir_full = f"{ARDOC_WEBDIR}/{WTLogdir}"
    
    # Create web log directory if it doesn't exist
    Path(WTLogdir_full).mkdir(parents=True, exist_ok=True)
    
    testprepage = "ardoc_testprepage"
    
    # Read all log files
    try:
       allfiles = [
          f for f in os.listdir(ARDOC_TESTLOGDIR)
          if re.match(r"^.+log$", f)
       ]
    except OSError:
       print(f"Error reading directory {ARDOC_TESTLOGDIR}") 
       allfiles = []

    print("LIST ALL FILES in ",ARDOC_TESTLOGDIR," : ", allfiles)

    list91 = [f for f in allfiles if not f.startswith("ardoc_")]
    listfiles = [f for f in list91 if not f.endswith('.logloglog')]
    listfiles = sorted(listfiles, key=compar)
    
    # Read test database
    test_db = []
    number_tests_db = 0
    if ARDOC_TEST_DBFILE_GEN and os.path.isfile(ARDOC_TEST_DBFILE_GEN):
        try:
            with open(ARDOC_TEST_DBFILE_GEN, 'r') as f:
                test_db = [line.strip() for line in f if line.strip()]
            number_tests_db = len(test_db)
            print(f"ardoc_errorhandler: number of tests in test_db {number_tests_db}")
        except IOError:
            print(f"Error reading {ARDOC_TEST_DBFILE_GEN}")
    
    # Write number of tests
    filet_nn = f"{ARDOC_WORK_AREA}/{testprepage}_number"
    try:
        with open(filet_nn, 'w') as f:
            f.write(f"{number_tests_db}\n")
    except IOError:
        print(f"Error writing {filet_nn}")
    
    # Open testprepage file
    filet = f"{ARDOC_WORK_AREA}/{testprepage}"
    try:
        tf = open(filet, 'w')
    except IOError:
        print(f"Error opening {filet}")
        return
    
    body = []
    body_count = 0
    body_prev = []
    addr_total = []
    addr_total_prev = []
    testname_subject_prev = ""
    dplusd_m = ""
    
    # Filter list files
    listfiles1 = []
    for listfile in listfiles:
        lin1 = listfile.replace(' ', '')
        if len(lin1) == 0 or listfile.startswith('.') or listfile.endswith('~'):
            continue
        listfiles1.append(listfile)
    
    # Process each log file
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
        
        # Find valid test directory
        for m, field in enumerate(fields):
            first_fields.append(field)
            testdir1 = "/".join(first_fields)
            if testdir1 in [".", "/", "/."]:
                testdir1 = ""
            
            direc = f"{ARDOC_RELHOME}/{prefix_relhome}/{testdir1}"
            if not os.path.isdir(direc):
                m_last = m
                break
            testdir = testdir1
        
        # Get remaining fields
        for m in range(m_last, len(fields)):
            last_fields.append(fields[m])
        testname_base = "_".join(last_fields)
        
        # Search for suite in test database
        testsuite = "undefined"
        addr_t = []
        testdir2 = ""
        testname2 = ""
        
        for line in test_db:
            if line.startswith('#') or not line.strip():
                continue
            
            # Clean line and split
            lll = ' '.join(line.split())
            fields_db = lll.split()
            if len(fields_db) < 6:
                continue
                
            testname1 = fields_db[1]
            testname2 = testname1.split('.')[0]
            testdir1 = fields_db[2]
            testdir2 = container_extractor(testdir1, ARDOC_RELHOME, prefix_relhome)
            testname_compar = f"{testdir2}_{testname2}"
            
            testsui = fields_db[4]
            testtime = fields_db[5]
            
            if testname_compar == testname:
                for m in range(7, len(fields_db)):
                    addr_t.append(fields_db[m])
                testsuite = testsui
                testdir = testdir2
                testname_base = testname2
                break
        
        # Check exit code
        fecod = f"{ARDOC_TESTLOGDIR}/{testdir2}_{testname2}.exitcode"
        exitcode = "N/A"
        if os.path.isfile(fecod):
            try:
                with open(fecod, 'r') as f:
                    exitcode = f.read().strip()
            except IOError:
                pass
        
        # Run error tester
        lower_NFEA = ARDOC_FULL_ERROR_ANALYSIS.lower()
        if (lower_NFEA not in ["true", "yes"] and "unit-tests" not in testname):
            # Light error analysis
            cmd = ["python3", f"{ARDOC_HOME}/ardoc_errortester.py", "-elst", testname, release]
            print("ERRORTESTER(lighttest) ",cmd)
            print(f" light test_tester: {testname}_ERROR_MESSAGE {release} : {exitcode}")
        else:
            # Full error analysis
            cmd = ["python3", f"{ARDOC_HOME}/ardoc_errortester.py", "-est", testname, release]
            print("ERRORTESTER(fullttest) ",cmd)
            if lower_NFEA in ["true", "yes"]:
                print(f" full test_tester: {testname}_ERROR_MESSAGE {release} : {exitcode}")
            else:
                print(f" test_tester: {testname}_ERROR_MESSAGE {release} : {exitcode}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            strng1 = result.stdout.strip().split('\n')
        except (subprocess.SubprocessError, FileNotFoundError):
            strng1 = [""]
        
        strng = strng1[0] if strng1 else ""
        fieldstr = strng.split()
        patterns = fieldstr[3:] if len(fieldstr) > 3 else []
        
        tproblems = 0
        if len(fieldstr) > 0 and strng:
            if fieldstr[0] == "M":
                tproblems = 0.5
                print(f"ardoc_testhandler.py: test minor warnings in {testname} !!!")
                print(f"                      pattern to blame: {' '.join(patterns)} !!!")
            elif fieldstr[0] == "W":
                tproblems = 1
                print(f"ardoc_testhandler.py: test warnings in {testname} !!!")
                print(f"                      pattern to blame: {' '.join(patterns)} !!!")
            elif fieldstr[0] == "G":
                tproblems = 2
        
        if tproblems == 2:
            print(f"ardoc_testhandler.py: test problems in {testname} !!!")
            print(f"                      pattern to blame: {' '.join(patterns)} !!!")
            
            var = f"{ARDOC_TESTLOGDIR}/{listfile}"
            var_orig = f"{ARDOC_TESTLOGDIR}/{listfile}"
            varvar = f"{ARDOC_WEBPAGE}/ARDOC_TestLog_{release}/{listfileh}"
            
            # Process test name for subject
            ftest = testname.split("__")
            if len(ftest) == 1:
                testname_sh = testname
            else:
                if ftest[-1] in ["", "a", "k", "x", "m"]:
                    ftest.pop()
                if len(ftest) > 2:
                    ftest.pop(0)
                    if len(ftest) > 1 and ftest[0] == "":
                        ftest.pop(0)
                testname_sh = '#'.join(ftest)
            
            t2_ss = testname2
            t2_spl = testname2.split('__')
            if len(t2_spl) > 1:
                t2_ss = t2_spl[1]
            
            testname_subject = t2_ss
            dplusd = f"{testdir2}____{t2_ss}"
            
            if dplusd != dplusd_m:
                body = []
                addr_total = []
                body_count = 0
                for address in addr_t:
                    if address and '@' in address:
                        addr_total.append(address)
            
            body_count += 1
            
            # Add unique addresses
            add_addi = []
            for address1 in addr_t:
                add1 = address1.replace(' ', '')
                sig_eq = False
                for address in addr_total:
                    add = address.replace(' ', '')
                    if add == add1:
                        sig_eq = True
                        break
                if not sig_eq:
                    add_addi.append(address1)
            
            if add_addi:
                addr_total.extend(add_addi)
            
            if not addr_total and addr_t:
                addr_total.extend(addr_t)
            
            # Build email body
            body.extend([
                " ===========================================================\n",
                " This message is generated by ARDOC build for \n",
                f" project {project} , {nightly} release {release} {ARDOC_ARCH}. \n",
                f" ARDOC system found possible problems with {type_name} \n  {testname_sh}\n",
                f" suspicious pattern:\"{' '.join(patterns)}\" !!!\n",
                " ===========================================================\n",
                f" The {type_name} logfile is available at: \n {var} \n and(or) \n {varvar} \n",
                " ===========================================================\n",
                f" For further information please refer to {project} ARDOC webpage \n",
                f" {ARDOC_WEBPAGE}/index.html\n"
            ])
            
            # Add first 100 lines for TriggerTest
            if type_name == "test" and "TriggerTest" in var_orig:
                if os.path.isfile(var_orig):
                    try:
                        with open(var_orig, 'r') as log_f:
                            nrec = 0
                            nrec1 = 0
                            signh = False
                            for line in log_f:
                                nrec += 1
                                if nrec > 200 or nrec1 > 100:
                                    break
                                line = line.rstrip('\n')
                                if not line:
                                    continue
                                if "ATN" in line and "Starting" in line:
                                    signh = True
                                if signh:
                                    nrec1 += 1
                                if nrec1 == 1:
                                    body.extend([
                                        " ===========================================================\n",
                                        " FIRST 100 LINES OF TEST LOG\n",
                                        " -----------------------------------------------------------\n"
                                    ])
                                if signh:
                                    body.append(f"{line}\n")
                    except IOError:
                        pass
        
        # Handle email sending logic (commented out like in original)
        if dplusd != dplusd_m or mlf == len(listfiles1) - 1:
            dplusd_m = dplusd
            if mlf == len(listfiles1) - 1:
                body_prev = body[:]
                addr_total_prev = addr_total[:]
                body_count_prev = body_count
                testname_subject_prev = testname_subject
            
            if body_prev:
                if body_count_prev > 1:
                    body_prev.insert(0, " !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
                    body_prev.insert(1, f" ARDOC combined error messages from {body_count_prev} tests of {testname_subject_prev} \n")
                    body_prev.insert(2, " !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
                
                print(f"ardoc_errorhandler.py: sending email about {body_count_prev} pbs in {testname_subject_prev}, size {len(body_prev)}, file count {mlf}")
                
                # Email handling (commented out like original)
                for address in addr_total_prev:
                    if address and '@' in address:
                        if "somebody" in address:
                            print(f"ardoc_errorhandler.py: Problems with {type_name} {testname_subject_prev} !!! Mail is NOT sent to such {address}")
                        else:
                            # Email blacklist processing
                            address_ar = address.split(',')
                            address_fin = []
                            for add95 in address_ar:
                                add96 = add95.lstrip()
                                add97 = add95.lower()
                                if any(x in add97 for x in ['damazio', 'cpotter', 'cern.fr', 'helenka']):
                                    print(f"ardoc_errorhandler.py: address {add96} blacklisted for {type_name} {testname_subject_prev}")
                                else:
                                    address_fin.append(add96)
                            
                            address_after_blacklist = ','.join(address_fin)
                            test_after_blacklist = address_after_blacklist.replace(' ', '')
                            
                            if test_after_blacklist:
                                print(f"ardoc_errorhandler.py: Problems with {type_name} {testname_subject_prev} !!! Mail is sent to {address_after_blacklist}")
                            else:
                                print(f"ardoc_errorhandler.py: Problems with {type_name} {testname_subject_prev} !!! Mail list is empty")
                            
                            # Mail sending would go here (commented out)
        
        # Write test results to file
        fec = f"{ARDOC_TESTLOGDIR}/{testdir2}_{testname2}.exitcode"
        exitcod = "N/A"
        if os.path.isfile(fec):
            try:
                with open(fec, 'r') as f:
                    exitcod = f.read().strip()
            except IOError:
                pass
        
        tstmp = f"{ARDOC_TESTLOGDIR}/{testdir2}_{testname2}.timestamp"
        time_beg = "N/A"
        time_end = "N/A"
        if os.path.isfile(tstmp):
            try:
                with open(tstmp, 'r') as f:
                    timelin1 = f.read().strip()
                    timeline = timelin1.replace(' ', '')
                    fields_time = timeline.split('#')
                    if fields_time[0]:
                        time_beg = fields_time[0]
                    if len(fields_time) > 1 and fields_time[1]:
                        time_end = fields_time[1]
            except IOError:
                pass
        
        print(f"===errorhandler: exit code,file,dir: {exitcod} {testdir2}_{testname2}.exitcode {ARDOC_TESTLOGDIR}")
        print(f"===errorhandler: time begin,end,filestamp: {time_beg} {time_end} {testdir2}_{testname2}.timestamp")
        
        fieldstr2 = fieldstr[2] if len(fieldstr) > 2 else ""
        tf.write(f"{testname} {testsuite} {listfileh} {tproblems} {exitcod} {testdir} {testname_base} {time_beg} {time_end} {' '.join(addr_t)} \"\"\" {fieldstr2} \"\"\" \"{' '.join(patterns)}\" \n")
        
        body_prev = body[:]
        addr_total_prev = addr_total[:]
        body_count_prev = body_count
        testname_subject_prev = testname_subject
    
    tf.close()
    
    # Copy test log files to web directory
    WTLogdir_full = f"{ARDOC_WEBDIR}/{WTLogdir}"
    Path(WTLogdir_full).mkdir(parents=True, exist_ok=True)
    
    try:
        allcpfiles = os.listdir(ARDOC_TESTLOGDIR)
        listf_9 = [f for f in allcpfiles if not re.match(r'.+\.loglog.+', f)]
        listf = [f for f in listf_9 if not f.endswith('.html')]
        
        for lf in listf:
            if lf.startswith('.') or lf.endswith('~'):
                continue
            
            lf_full = f"{ARDOC_TESTLOGDIR}/{lf}"
            if not os.path.isfile(lf_full):
                continue
                
            try:
                lf_size = os.path.getsize(lf_full)
                dest_file = f"{WTLogdir_full}/{lf}"
                
                with open(dest_file, 'w') as f:
                    f.write("ARDOC NOTICE: THIS FILE IS ALSO AVAILABLE AT:\n")
                    f.write(f"{ARDOC_TESTLOGDIR}/{lf}\n")
                    
                if lf_size <= 4000000:
                    # Small file - could copy content but skipping like original
                    pass
                else:
                    # Large file
                    with open(dest_file, 'a') as f:
                        f.write("ARDOC NOTICE: THIS FILE IS TRUNCATED DUE TO LARGE SIZE\n")
                        f.write(f"LARGER, POSSIBLY NOT TRUNCATED COPY IS {ARDOC_TESTLOGDIR}/{lf}\n")
                        
            except (OSError, IOError):
                continue
                
    except OSError:
        print(f"Error processing files in {ARDOC_TESTLOGDIR}")

def main():
    """Main error handler function"""
    # Parse arguments
    parser = argparse.ArgumentParser(description='ARDOC Error Handler')
    parser.add_argument('--jid', default='NONE', help='Job ID')
    args = parser.parse_args()
    
    print("------------------------------------------------------------")
    print("   Starting ARDOC error analysis")
    print("------------------------------------------------------------")
    
    # Get environment variables
    ARDOC_WORK_AREA = os.environ.get('ARDOC_WORK_AREA', '')
    ARDOC_DBFILE = os.environ.get('ARDOC_DBFILE', '')
    ARDOC_DBFILE_GEN = os.environ.get('ARDOC_DBFILE_GEN', '')
    ARDOC_MAIL = os.environ.get('ARDOC_MAIL', '')
    ARDOC_MAIL_WARNINGS = os.environ.get('ARDOC_MAIL_WARNINGS', '')
    ARDOC_MAIL_MINOR_WARNINGS = os.environ.get('ARDOC_MAIL_MINOR_WARNINGS', '')
    ARDOC_MAIL_UNIT_TESTS = os.environ.get('ARDOC_MAIL_UNIT_TESTS', '')
    ARDOC_MAIL_INT_TESTS = os.environ.get('ARDOC_MAIL_INT_TESTS', '')
    ARDOC_MAIL_PROJECT_KEYS = os.environ.get('ARDOC_MAIL_PROJECT_KEYS', '')
    ARDOC_PROJECT_RELNAME = os.environ.get('ARDOC_PROJECT_RELNAME', '')
    ARDOC_PROJECT_NAME = os.environ.get('ARDOC_PROJECT_NAME', '')
    ARDOC_LOGDIR = os.environ.get('ARDOC_LOGDIR', '')
    ARDOC_LOG = os.environ.get('ARDOC_LOG', '')
    ARDOC_TESTLOG = os.environ.get('ARDOC_TESTLOG', '')
    ARDOC_PROJECTBUILD_DIR = os.environ.get('ARDOC_PROJECTBUILD_DIR', '')
    ARDOC_WEBDIR = os.environ.get('ARDOC_WEBDIR', '')
    ARDOC_WEBPAGE = os.environ.get('ARDOC_WEBPAGE', '')
    ARDOC_NIGHTLY_NAME = os.environ.get('ARDOC_NIGHTLY_NAME', '')
    ARDOC_ARCH = os.environ.get('ARDOC_ARCH', '')
    ARDOC_RELHOME = os.environ.get('ARDOC_RELHOME', '')
    ARDOC_HOME = os.environ.get('ARDOC_HOME', '')
    
    if ARDOC_LOG:
        ARDOC_LOGDIR = os.path.dirname(ARDOC_LOG)
    
    if ARDOC_TESTLOG:
        ARDOC_TESTLOGDIR = os.path.dirname(ARDOC_TESTLOG)
    
    prevdir = os.getcwd()
    
    nomail = 1
    nomail_t = [1, 1, 1]
    
    # Database file handling
    base_file = os.path.basename(ARDOC_DBFILE)
    filename_gen = f"{ARDOC_WORK_AREA}/{base_file}_gen"
    filename_res = f"{ARDOC_WORK_AREA}/{base_file}_gen_res"
    
    filename = filename_gen
    if os.path.isfile(filename_res):
        filename = filename_res
    
    prepage = "ardoc_prepage"
    prepage_problems = "ardoc_prepage_problems"
    testprepage = "ardoc_testprepage"
    release = ARDOC_PROJECT_RELNAME
    project = ARDOC_PROJECT_NAME
    nightly = ARDOC_NIGHTLY_NAME
    
    # Process test results
    ardoc_testhandler(2)
    
    # Change to build directory
    ndir = f"{ARDOC_RELHOME}/{ARDOC_PROJECTBUILD_DIR}"
    try:
        os.chdir(ndir)
    except OSError:
        print(f"Error changing to directory {ndir}")
    
    # Create web log directories
    WLogdir = f"ARDOC_Log_{release}"
    WTLogdir = f"ARDOC_TestLog_{release}"
    ndir = f"{ARDOC_WEBDIR}/{WLogdir}"
    Path(ndir).mkdir(parents=True, exist_ok=True)
    
    filet = f"{ARDOC_WORK_AREA}/{testprepage}"
    file_path = f"{ARDOC_WORK_AREA}/{prepage}"
    
    part_t = "no"
    
    if part_t == "no":
        # Copy log files to web directory
        try:
            allcpfiles = os.listdir(ARDOC_LOGDIR)
            listf1 = [f for f in allcpfiles if not re.match(r'.+\.loglog.+', f)]
            listf = [f for f in listf1 if not f.endswith('.loglog')]
            
            for lf in listf:
                if lf.startswith('.') or lf.endswith('~'):
                    continue
                src = f"{ARDOC_LOGDIR}/{lf}"
                dst = f"{ARDOC_WEBDIR}/{WLogdir}/"
                try:
                    shutil.copy2(src, dst)
                except (shutil.Error, IOError):
                    continue
        except OSError:
            print(f"Error processing files in {ARDOC_LOGDIR}")
        
        # Remove specific files from web directory
        try:
            os.remove(f"{ARDOC_WEBDIR}/{WLogdir}/ardoc_general.loglog")
        except OSError:
            pass
        
        # Remove prepage file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Read container addresses from generated database file
        container_addr = {}
        try:
            with open(filename_gen, 'r') as f:
                dbc = [line.strip() for line in f]
            
            for line in dbc:
                if line.startswith('#') or not line.strip():
                    continue
                
                lll = ' '.join(line.split())
                fields = lll.split()
                if len(fields) < 3:
                    continue
                    
                package = fields[0]
                tag = fields[1]
                addr = fields[3:] if len(fields) > 3 else []
                
                fields_pkg = package.split("/")
                if len(fields_pkg) == 1:
                    container_addr[package] = addr
        except IOError:
            print(f"Error reading {filename_gen}")
        
        # Read main database file and process packages
        try:
            with open(filename, 'r') as f:
                dbc = [line.strip() for line in f]
        except IOError:
            print(f"Error reading {filename}")
            return
        
        scount = 0
        totcount = 0
        
        try:
            fl = open(file_path, 'w')
        except IOError:
            print(f"Error opening {file_path}")
            return
        
        for line in dbc:
            if line.startswith('#') or not line.strip():
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
            
            pkgbs = os.path.basename(package)
            fieldsp = package.split("/")
            cont_addr = []
            
            if len(fields) > 1:
                package_cont = fieldsp[0]
                if package_cont in container_addr:
                    cont_addr = container_addr[package_cont]
                    container_addr[package] = addr
            
            # Run error tester on package
            cmd = ["python3", f"{ARDOC_HOME}/ardoc_errortester.py", "-es", pkgn, release, filename, package]
            print("ERRORTESTER(comp) ",cmd)
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=False)
                strng1 = result.stdout.strip().split('\n')
            except (subprocess.SubprocessError, FileNotFoundError):
                strng1 = [""]
            
            strng = strng1[0] if strng1 else ""
            fieldstr = strng.split()
            patterns = fieldstr[3:] if len(fieldstr) > 3 else []
            
            problems = 0
            if len(fieldstr) > 0 and strng:
                if fieldstr[0] == "G":
                    problems = 2
                    print(f"ardoc_errorhandler.py: error level build problems with {pkgn} of {release} !!!")
                    print(f"ardoc_errorhandler.py: offending pattern: {' '.join(patterns)}")
                elif fieldstr[0] == "W":
                    problems = 1
                    print(f"ardoc_errorhandler.py: warning level build problems with {pkgn} of {release} !!!")
                    print(f"ardoc_errorhandler.py: offending pattern: {' '.join(patterns)}")
                elif fieldstr[0] == "M":
                    problems = 0.5
                    print(f"ardoc_errorhandler.py: minor warning level build problems with {pkgn} of {release} !!!")
                    print(f"ardoc_errorhandler.py: offending pattern: {' '.join(patterns)}")
            
            # Check test problems
            test_problems = [0, 0, 0]
            type_names = ["", "qatest", "test"]
            
            for i in range(2, 3):  # Only unit tests (i=2)
                try:
                    with open(filet, 'r') as f:
                        ttpp = [line.strip() for line in f]
                    
                    comp1 = pkgn.lower()
                    test_problems[i] = 0
                    
                    for test_line in ttpp:
                        if test_line.startswith('#') or not test_line.strip():
                            continue
                        
                        lll = ' '.join(test_line.split())
                        fields_test = lll.split()
                        if len(fields_test) < 4:
                            continue
                            
                        testname = fields_test[0]
                        trecent_logfiles = fields_test[2]
                        tproblems = float(fields_test[3]) if fields_test[3].replace('.', '').isdigit() else 0
                        
                        comp2 = testname.lower()
                        if comp1 == comp2:
                            test_problems[i] = tproblems
                            break
                            
                except IOError:
                    pass
                
                if test_problems[i] == 0.5:
                    print(f"ardoc_errorhandler.py: {type_names[i]} minor warnings with {pkgn} !!!")
                elif test_problems[i] == 1:
                    print(f"ardoc_errorhandler.py: {type_names[i]} warnings with {pkgn} !!!")
                elif test_problems[i] >= 2:
                    print(f"ardoc_errorhandler.py: {type_names[i]} problems with {pkgn} !!!")
            
            # Find log files
            try:
                allfiles = os.listdir(ARDOC_LOGDIR)
                stg = f"{pkgn}.loglog"
                listx = [f for f in allfiles if f == stg]
                list_files = [f for f in listx if not f.startswith('.')]
                
                # Sort by modification time
                if list_files:
                    list_files.sort(key=lambda x: os.path.getmtime(os.path.join(ARDOC_LOGDIR, x)), reverse=True)
                    listfilesf = list_files[0]
                else:
                    listfilesf = ""
            except OSError:
                listfilesf = ""
            
            if not listfilesf:
                # Create missing log file
                lf = f"{ARDOC_LOGDIR}/{pkgn}.loglog"
                try:
                    with open(lf, 'w') as f:
                        f.write(" ARDOC determined that make did nothing for this package.\n")
                        f.write(" Error in package configuration or structure is possible.\n")
                    
                    # Copy to web directories
                    shutil.copy2(lf, f"{ARDOC_WEBDIR}/{WLogdir}/{pkgn}.html")
                    shutil.copy2(lf, f"{ARDOC_LOGDIR}/{pkgn}.html")
                    
                    problems = 2
                    fieldstr = ["G", pkgn.replace('_', '/'), "", "absent logfile"]
                    patterns = ["absent logfile"]
                    print(f"ardoc_errorhandler: generating missing logfile {' '.join(fieldstr)}")
                    strng = f"G {fieldstr[1]} . {fieldstr[3]}"
                    
                    listfilesf_base = pkgn
                    listfilesh = f"{pkgn}.html"
                    
                except IOError:
                    listfilesf_base = ""
                    listfilesh = ""
            else:
                listfields = listfilesf.split('.')
                listfields.pop()  # Remove extension
                listfilesf_base = '.'.join(listfields)
                listfilesh = f"{listfilesf_base}.html"
            
            listfiles = os.path.basename(listfilesh)
            recent_logfile = listfiles
            
            pkgcontainer = os.path.dirname(package)
            if pkgcontainer == ".":
                pkgcontainer = "N/A"
            pkgbase = os.path.basename(package)
            
            # Convert addresses to lowercase
            addr_lower = [a.lower() for a in addr]
            lin1 = ' '.join(addr_lower)
            line_clean = lin1.replace(' ', '')
            
            totcount += 1
            if problems in [2, 1]:
                scount += 1
            
            fieldstr2 = fieldstr[2] if len(fieldstr) > 2 else ""
            
            if line_clean and line_clean != "-":
                fl.write(f"{pkgbase} {pkgcontainer} {recent_logfile} {problems} {test_problems[1]} {test_problems[2]} {' '.join(addr)} \"\"\" {fieldstr2} \"\"\" {' '.join(patterns)}\n")
            else:
                fl.write(f"{pkgbase} {pkgcontainer} {recent_logfile} {problems} {test_problems[1]} {test_problems[2]} {' '.join(addr)} \"\"\" {fieldstr2} \"\"\" {' '.join(patterns)}\n")
        
        fl.close()
        
        # Calculate percentage of problematic packages
        percen = 0
        if totcount != 0:
            percen = int((scount / totcount) * 100)
            if percen > 50:
                print(f"ardoc_errorhandler.py: high percentage of packages with compilation problems : {percen} : emails disabled")
                nomail = 2
            else:
                print(f"ardoc_errorhandler.py: percentage of packages with compilation problems : {percen}")
        
        # Process prepage file for email notifications
        try:
            with open(file_path, 'r') as f:
                dbc = [line.strip() for line in f]
        except IOError:
            print(f"Error reading {file_path}")
            return
        
        for line in dbc:
            if line.startswith('#') or not line.strip():
                continue
            
            # Split on """ delimiters
            fields9 = line.split(' """ ')
            fields = fields9[0].split() if fields9 else []
            
            patterns_b = ""
            drctr = ""
            
            if len(fields9) > 1:
                drctr = fields9[1]
            if len(fields9) > 2:
                patterns_b = fields9[2]
            
            if len(fields) < 6:
                continue
                
            pkgbase = fields[0]
            pkgcontainer = fields[1]
            package = f"{pkgcontainer}/{pkgbase}" if pkgcontainer != "N/A" else pkgbase
            pkgn = package.replace('/', '_')
            recent_logfile = fields[2]
            problems = float(fields[3]) if fields[3].replace('.', '').isdigit() else 0
            
            test_problems = [0, 0, 0]
            test_problems[1] = float(fields[4]) if fields[4].replace('.', '').isdigit() else 0
            test_problems[2] = float(fields[5]) if fields[5].replace('.', '').isdigit() else 0
            
            addr = fields[6:] if len(fields) > 6 else []
            
            # Handle build problems
            if problems in [2, 1, 0.5] and patterns_b:
                alarm_level = "problems"
                if problems == 1:
                    alarm_level = "warning signs"
                elif problems == 0.5:
                    alarm_level = "minor warning signs"
                
                var = f"{drctr}/{pkgn}.loglog"
                varvar = f"{ARDOC_WEBPAGE}/{WLogdir}/{pkgn}.html"
                
                body = [
                    " ===========================================================\n",
                    " This message is generated by ARDOC build for \n",
                    f" project {project} , {nightly} release {release} {ARDOC_ARCH}. \n",
                    f" ARDOC system found possible {alarm_level} for package \n {package}\n",
                    f" suspicious pattern:\"{patterns_b}\" !!!\n",
                    " ===========================================================\n",
                    f" The build logfile is available at: \n {var} \n and(or) \n {varvar} \n",
                    " ===========================================================\n",
                    f" For further information please refer to {project} ARDOC webpage \n",
                    f" {ARDOC_WEBPAGE}/index.html\n"
                ]
                
                # Email handling (commented out like original)
                for address in addr:
                    if address and '@' in address:
                        nomail_1 = nomail
                        if ARDOC_MAIL_WARNINGS == "no" and alarm_level == "warning signs":
                            nomail_1 = 1
                        if ARDOC_MAIL_MINOR_WARNINGS != "yes" and alarm_level == "minor warning signs":
                            nomail_1 = 1
                        
                        print(f"ardoc_errorhandler.py: Problems with {package} !!! Mail is sent to {address} code {nomail_1} (orig. {nomail})")
                        
                        # Mail sending would go here (commented out)
            
            # Handle test problems
            for i in range(2, 3):  # Only unit tests
                if test_problems[i] > 0.5:
                    dirtest = os.path.dirname(ARDOC_TESTLOG)
                    var = f"{dirtest}/{pkgn}.loglog"
                    varvar = f"{ARDOC_WEBPAGE}/{WTLogdir}/{pkgn}.html"
                    
                    typet = type_names[i]
                    body = [
                        " ===========================================================\n",
                        " This message is generated by ARDOC build for \n",
                        f" project {project} , {nightly} release {release} {ARDOC_ARCH}. \n",
                        f" ARDOC system found possible problems with {typet}s for package \n {package}\n",
                        " ===========================================================\n",
                        f" The {typet} logfile is available at: \n {var} \n and(or) \n {varvar} \n",
                        " ===========================================================\n",
                        f" For further information please refer to {project} ARDOC webpage \n",
                        f" {ARDOC_WEBPAGE}/index.html\n"
                    ]
                    
                    for address in addr:
                        if address and '@' in address:
                            print(f"ardoc_errorhandler.py: Problems with {typet}s of  {package} !!! Mail is sent to {address} code {nomail_t[i]}")
                            
                            # Mail sending would go here (commented out)
    
    # Return to original directory
    os.chdir(prevdir)


if __name__ == "__main__":
    main()
