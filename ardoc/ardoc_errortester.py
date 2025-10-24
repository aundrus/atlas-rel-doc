#!/usr/bin/env python3

import os
import sys
import re
import urllib.parse
from pathlib import Path

def header_print(file_handle, problem, test_name):
    """Print HTML header with appropriate style based on problem level"""
    comment = ""
    if problem == 0.5:
        comment = "M"
    elif problem == 1:
        comment = "W"
    elif problem == 2:
        comment = "E"
    
    html_header = f"""<html>
<!-- {comment} -->
<style>
body {{
  color: black;
  link: navy;
  vlink: maroon;
  alink: tomato;
  background: floralwhite;
  font-family: 'Lucida Console', 'Courier New', Courier, monospace;
  font-size: 10pt;
}}
td.aid {{
  background: #6600CC;
  color: orangered;
  text-align: center;
}}
td.ttl {{
  color: #6600CC;
  text-align: center;
}}
a.small {{
  color: navy;
  background: #FFCCFF;
  font-family: Verdana, Arial, Helvetica, sans-serif;
  font-size: 10pt;
}}
#prblm {{background-color: orange;}}
#hdr0 {{
  font-family: Verdana, Arial, Helvetica, sans-serif;
  font-size: 14pt;
}}
#hdr {{
background-color: #FFCCFF;
  font-family:'Times New Roman',Garamond, Georgia, serif;
  font-size: 14pt;
}}
#hdr1 {{
background-color: #CFECEC;
  font-family: Verdana, Arial, Helvetica, sans-serif;
  font-size: 10pt;
}}
</style>

<head><title>
{test_name} Logfile
</title>
</head>

<BODY class=body marginwidth="0" marginheight="0" topmargin="0" leftmargin="0">
"""
    file_handle.write(html_header)

def main():
    # Initialize command line options
    short = False
    specformat = False
    testtesting = False
    qatesting = False
    light = False
    
    # Parse command line arguments (handle the Perl-style combined flags)
    if len(sys.argv) >= 2 and sys.argv[1].startswith('-'):
        options = sys.argv[1]
        if re.match(r'^-[qstel]+$', options):
            if 's' in options:
                short = True
            if 'e' in options:
                specformat = True
            if 't' in options:
                testtesting = True
            if 'q' in options:
                qatesting = True
            if 'l' in options:
                light = True
            sys.argv.pop(1)  # Remove the options from argv
    
    # Get environment variables
    ARDOC_LOG = os.environ.get('ARDOC_LOG', '')
    ARDOC_TESTLOG = os.environ.get('ARDOC_TESTLOG', '')
    ARDOC_NINJALOG = os.environ.get('ARDOC_NINJALOG', '')
    ARDOC_HOME = os.environ.get('ARDOC_HOME', '')
    ARDOC_PROJECT_NAME = os.environ.get('ARDOC_PROJECT_NAME', '')
    ARDOC_PROJECT_RELNAME = os.environ.get('ARDOC_PROJECT_RELNAME', '')
    ARDOC_WEBPAGE = os.environ.get('ARDOC_WEBPAGE', '')
    ARDOC_WEBDIR = os.environ.get('ARDOC_WEBDIR', '')
    ARDOC_VERSION = os.environ.get('ARDOC_VERSION', '')
    
    # Determine type and validate arguments
    if not testtesting and not qatesting:
        type_name = "package"
        type_in_url = "c"
        type_in_html = "build"
        ARDOC_TESTLOGDIR = os.path.dirname(ARDOC_LOG)
        if len(sys.argv) != 5:  # script name + 4 args
            print("ardoc_errortester:")
            print("Four arguments required: directory_package, release, tags file, package name")
            sys.exit(2)
    else:
        type_in_url = "t"
        type_in_html = "test"
        type_name = "test"
        if qatesting:
            type_name = "qatest"
            ARDOC_TESTLOGDIR = os.path.dirname(os.environ.get('ARDOC_QALOG', ''))
        else:
            ARDOC_TESTLOGDIR = os.path.dirname(ARDOC_TESTLOG)
        
        ARDOC_TESTLOGDIR_TEMP = os.path.join(ARDOC_TESTLOGDIR, "temp")
        if len(sys.argv) != 3:  # script name + 2 args
            print("ardoc_errortester:")
            print(f"Two arguments required: names of test, release {sys.argv}")
            sys.exit(2)
    
    ARDOC_TESTLOGDIRBASE = os.path.basename(ARDOC_TESTLOGDIR)
    
    # Parse arguments
    compname = sys.argv[1]
    release = sys.argv[2]
    filename = sys.argv[3] if len(sys.argv) > 3 else ""
    pkgname_full = sys.argv[4] if len(sys.argv) > 4 else ""
    pkgname = os.path.basename(pkgname_full) if pkgname_full else ""
    
    # Calculate container name
    cnt1 = compname.count(f'_{pkgname}') if pkgname else 0
    if cnt1 == 0:
        contname = compname
    else:
        contname = compname
        cnt2 = 0
        pattern = f'(_)({re.escape(pkgname)})'
        def replacer(match):
            nonlocal cnt2
            cnt2 += 1
            return "" if cnt2 == cnt1 else match.group(0)
        contname = re.sub(pattern, replacer, contname)
    
    # Get test patterns from environment
    TEST_SUCCESS_PATTERN = os.environ.get('ARDOC_TEST_SUCCESS_PATTERN', '')
    TEST_FAILURE_PATTERN = os.environ.get('ARDOC_TEST_FAILURE_PATTERN', '')
    TEST_WARNING_PATTERN = os.environ.get('ARDOC_TEST_WARNING_PATTERN', '')
    BUILD_FAILURE_PATTERN = os.environ.get('ARDOC_BUILD_FAILURE_PATTERN', 'CVBFGG')
    
    if qatesting:
        TEST_SUCCESS_PATTERN = os.environ.get('ARDOC_QA_SUCCESS_PATTERN', '')
        TEST_FAILURE_PATTERN = os.environ.get('ARDOC_QA_FAILURE_PATTERN', '')
        TEST_WARNING_PATTERN = os.environ.get('ARDOC_QA_WARNING_PATTERN', '')
    
    # Define error patterns for compilation logs (@e_patterns)
    e_patterns = [": error:", "CMake Error", "runtime error:", "No rule to make target", 
                  "SyntaxError:", "raceback (most recent", "CVBFGG", "error: ld", 
                  "error: Failed to execute", "no build logfile"]
    e_ignore = ["CVBFGG"] * 9 + [f"for {ARDOC_PROJECT_NAME}Release are"]
    e_ignore_2 = ["CVBFGG"] * 9 + [f"for {ARDOC_PROJECT_NAME} are"]
    e_ignore_3 = ["CVBFGG"] * 9 + [f"for {ARDOC_PROJECT_NAME}RunTime are"]
    e_ignore_4 = ["CVBFGG"] * 10
    e_ignore_5 = ["CVBFGG"] * 10
    
    # Define warning patterns for compilation logs (@e_warning_patterns)
    e_warning_patterns = ["Errors/Problems found", "CMake Warning", "CMake Deprecation Warning",
                         "Error in", "control reaches end of non-void", "suggest explicit braces",
                         "> Warning:", "type qualifiers ignored on function return type",
                         "[-Wsequence-point]", "mission denied", "nvcc warning :", "Warning: Fortran",
                         r'library.*\sexposes\s+factory.*\sdeclared\s+in']
    e_warning_patterns_correlators = ["", "", "", "", "", "", "", pkgname, "", "", "", "", ""]
    e_warning_patterns_ignore = ["Errors/Problems found : 0", "CVBFGG", "CVBFGG", "msg", 
                                "/external", "/external", "> Warning: template", "/external", 
                                "/external", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"]
    e_warning_patterns_ignore_2 = ["CVBFGG"] * 13
    
    # Define minor warning patterns for compilation logs (@e_warning_patterns_minor)
    e_warning_patterns_minor = [": warning: ", "Warning: the last line", "Warning: Unused class rule",
                               r'Warning:\s.*rule', "#pragma message:", r'WARNING\s+.*GAUDI', "CVBFGG"]
    e_warning_patterns_minor_ignore = ["make[", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "ClassIDSvc", "CVBFGG"]
    e_warning_patterns_minor_ignore_2 = ["CVBFGG"] * 7
    e_warning_patterns_minor_ignore_3 = ["CVBFGG"] * 7
    e_warning_patterns_minor_ignore_4 = ["CVBFGG"] * 7
    
    e_success = ["CVBFGG"] * 10
    e_warning_success = ["CVBFGG", "Package build succeeded"] + ["CVBFGG"] * 6
    packages_to_bypass_success = [ARDOC_PROJECT_NAME, f"{ARDOC_PROJECT_NAME}Release", f"{ARDOC_PROJECT_NAME}RunTime"]
    
    # Define test patterns (@e_test*)
    e_test_global_ignore = "distcc"
    e_test_failure = []
    e_test_failure_ignore = []
    e_test_failure_ignore_1 = []
    e_test_failure_ignore_2 = []
    e_test_failure_ignore_3 = []
    e_test_failure_ignore_4 = []
    e_test_failure_ignore_5 = []
    e_test_warnings = []
    e_test_warnings_minor = []
    e_test_warnings_minor_ignore = []
    e_test_warnings_minor_ignore_1 = []
    e_test_warnings_minor_ignore_2 = []
    e_test_warnings_minor_ignore_3 = []
    e_test_warnings_minor_ignore_4 = []
    e_test_warnings_minor_ignore_5 = []
    e_test_warnings_minor_project_ignore = []
    e_test_success = []
    e_test_success_addtl = []
    
    if qatesting:
        # QA testing patterns
        e_test_failure = ["*Timeout", "time quota spent", "severity=FATAL", "Error: execution_error",
                         "command not found", "tests FAILED", "*Failed", "Errors while running CTest",
                         TEST_FAILURE_PATTERN] + ["CVBFGG"] * 5
        e_test_failure_ignore = ["CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "kvt: command not found",
                                "INFO"] + ["CVBFGG"] * 8
        e_test_failure_ignore_1 = ["CVBFGG"] * 14
        e_test_failure_ignore_2 = ["CVBFGG"] * 14
        e_test_failure_ignore_3 = ["CVBFGG"] * 14
        e_test_failure_ignore_4 = ["CVBFGG"] * 14
        e_test_failure_ignore_5 = ["CVBFGG"] * 14
        e_test_warnings = [TEST_WARNING_PATTERN, "raceback (most recent", "file not found"] + ["CVBFGG"] * 5
        e_test_warnings_minor = ["severity=ERROR", "  ERROR", "No such file or directory"] + ["CVBFGG"] * 5
        e_test_warnings_minor_ignore = ["CVBFGG", "ERROR (pool)"] + ["CVBFGG"] * 6
        e_test_warnings_minor_ignore_1 = ["CVBFGG", "ERROR IN"] + ["CVBFGG"] * 6
        e_test_warnings_minor_ignore_2 = ["CVBFGG", "ServiceLocatorHelper"] + ["CVBFGG"] * 6
        e_test_warnings_minor_ignore_3 = ["CVBFGG"] * 8
        e_test_warnings_minor_ignore_4 = ["CVBFGG"] * 8
        e_test_warnings_minor_ignore_5 = ["CVBFGG"] * 8
        e_test_warnings_minor_project_ignore = ["CVBFGG", "Athena"] + ["CVBFGG"] * 5
        e_test_success = ["CVBFGG", TEST_SUCCESS_PATTERN] + ["CVBFGG"] * 5
        e_test_success_addtl = []
    else:
        # Integration testing patterns (default when testtesting=1)
        e_test_failure = ["*Timeout", r"test status fail(?!.*\bTIMEOUT\b)", "TIMEOUT occurred", "*Failed",
                         "TEST FAILURE", TEST_FAILURE_PATTERN, "severity=FATAL", ": FAILURE ",
                         "Error: execution_error", "command not found", "ERROR_MESSAGE", " ERROR ",
                         "exit code: 143", "tests FAILED", "time quota spent"]
        e_test_failure_ignore = ["CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "ctest status notrun", "CVBFGG",
                                "CVBFGG", "check_log", "CVBFGG", "kvt: command not found", "CVBFGG",
                                "check_log", "CVBFGG", "CVBFGG", "CVBFGG"]
        e_test_failure_ignore_1 = ["CVBFGG"] * 10 + ["HelloWorld"] + ["CVBFGG"] * 4
        e_test_failure_ignore_2 = ["CVBFGG"] * 11 + ["Cannot interpolate outside histogram"] + ["CVBFGG"] * 3
        e_test_failure_ignore_3 = ["CVBFGG"] * 11 + ["INFO "] + ["CVBFGG"] * 3
        e_test_failure_ignore_4 = ["CVBFGG"] * 11 + ["ERROR Propa"] + ["CVBFGG"] * 3
        e_test_failure_ignore_5 = ["CVBFGG"] * 11 + ["Acts"] + ["CVBFGG"] * 3
        
        e_test_warnings = [TEST_WARNING_PATTERN, "raceback (most recent", "file not found",
                          "Logfile error", "Non-zero return", "TEST WARNING"] + ["CVBFGG"] * 2
        e_test_warnings_minor = ["severity=ERROR", "  ERROR", "No such file or directory"] + ["CVBFGG"] * 5
        e_test_warnings_minor_ignore = ["CVBFGG", "ERROR (pool)", "INFO"] + ["CVBFGG"] * 5
        e_test_warnings_minor_ignore_1 = ["CVBFGG", "ERROR IN"] + ["CVBFGG"] * 6
        e_test_warnings_minor_ignore_2 = ["CVBFGG", "ServiceLocatorHelper"] + ["CVBFGG"] * 6
        e_test_warnings_minor_ignore_3 = ["CVBFGG", "HelloWorld"] + ["CVBFGG"] * 6
        e_test_warnings_minor_ignore_4 = ["CVBFGG", "Cannot interpolate outside histogram"] + ["CVBFGG"] * 6
        e_test_warnings_minor_ignore_5 = ["CVBFGG", "Acts"] + ["CVBFGG"] * 6
        e_test_warnings_minor_project_ignore = ["CVBFGG", "Athena"] + ["CVBFGG"] * 6
        e_test_success = ["CVBFGG", TEST_SUCCESS_PATTERN] + ["CVBFGG"] * 5
        e_test_success_addtl = []
        
        # Light mode: invalidate most patterns for test log analysis
        if light:
            for i in range(len(e_test_failure)):
                e_test_failure[i] = "CVBFGG"
            for i in range(len(e_test_warnings)):
                e_test_warnings[i] = "CVBFGG"
            for i in range(len(e_test_warnings_minor)):
                e_test_warnings_minor[i] = "CVBFGG"
            
            e_test_failure[0] = r"test status fail(?!.*\bTIMEOUT\b)"
            e_test_failure[1] = "TIMEOUT occurred"
            e_test_failure[2] = "TEST FAILURE"
            e_test_failure_ignore[0] = "CVBFGG"
            e_test_failure_ignore[1] = "CVBFGG"
            e_test_failure_ignore[2] = "ctest status notrun"
            e_test_warnings_minor[0] = "ctest status notrun"
            e_test_warnings_minor[1] = "*Failed"
            e_test_warnings_minor[2] = "TEST FAILURE"
            e_test_warnings_minor[3] = "*Timeout"
            e_test_warnings_minor[4] = "time quota spent"
            print(f"===ardoc_errortester.py: limited error analysis for {compname}", file=sys.stderr)
    
    # Initialize counters and line tracking
    e_count = [0] * 15
    w_count = [0] * 13
    w_minor_count = [0] * 8
    s_count = [0] * 10
    s_w_count = [0, 1] + [0] * 6
    lineE = [0] * 15
    lineW = [0] * 13
    lineM = [0] * 8
    lineEValue = [""] * 15
    lineWValue = [""] * 13
    lineMValue = [""] * 8
    
    if testtesting or qatesting:
        s_count = [0, 1] + [0] * 8
        s_w_count = [0] * 8
    
    # Print header if not in special format mode
    if not specformat:
        print("=" * 68)
        print(f"=== CHECK logfiles related to {compname} in {release}")
        print("=" * 68)
        print(" ")
    
    # Read tags file for non-test mode
    if not testtesting and not qatesting and filename:
        try:
            with open(filename, 'r') as f:
                dbc = [line.strip() for line in f]
            
            # Find matching package
            list_matches = [line for line in dbc if re.match(f"^{re.escape(pkgname_full)}[^a-zA-Z0-9_]", line)]
            if list_matches:
                lll = ' '.join(list_matches[0].split())
                tag = lll.split()[1] if len(lll.split()) > 1 else ""
        except:
            pass
    
    # Find log files
    try:
        allfiles = os.listdir(ARDOC_TESTLOGDIR)
    except OSError:
        allfiles = []
    
    stg = f"{compname}.loglog"
    list_files = [f for f in allfiles if f == stg]
    
    if list_files:
        # Sort by modification time, newest first
        list_files.sort(key=lambda x: os.path.getmtime(os.path.join(ARDOC_TESTLOGDIR, x)), reverse=True)
        listfiles = list_files[0]
    else:
        listfiles = None
    
    if listfiles:
        lineT = 0
        file_path = os.path.join(ARDOC_TESTLOGDIR, listfiles)
        filebase1 = os.path.basename(file_path)
        filedir = os.path.dirname(file_path)
        filebase = filebase1
        
        # Remove extension for HTML filename
        filebase_parts = filebase.split('.')
        if len(filebase_parts) > 1:
            filebase_parts.pop()
            filebase = '.'.join(filebase_parts)
        filehtml = os.path.join(filedir, f"{filebase}.html")
        
        # Set up URLs for different log types
        if testtesting:
            textfile_http = f"{ARDOC_WEBPAGE}/ARDOC_TestLog_{ARDOC_PROJECT_RELNAME}/{filebase1}"
        elif qatesting:
            textfile_http = f"{ARDOC_WEBPAGE}/ARDOC_QALog_{ARDOC_PROJECT_RELNAME}/{filebase1}"
        else:
            textfile_http = f"{ARDOC_WEBPAGE}/ARDOC_Log_{ARDOC_PROJECT_RELNAME}/{filebase1}"
        
        # Parse container name for tests
        optn = f"{contname} {pkgname} build"
        if testtesting or qatesting:
            f_contname = contname.split("__")
            contname1 = f_contname[0]
            inddd = len(f_contname) - 1
            tname = ""
            if inddd > 0:
                tname = f_contname[inddd]
            
            f_tname = tname.split("_")
            ft1 = len(f_tname) - 1
            if ft1 > 0:
                if re.match(r'^\w\s*$', f_tname[ft1]):
                    f_tname.pop()
                    tname = "_".join(f_tname)
            
            f_contname1 = contname1.split("_")
            fcnt1 = len(f_contname1) - 1
            tnumber = ""
            if fcnt1 > 0:
                fcnt9 = f_contname1[fcnt1]
                if re.match(r'^\d\d$', fcnt9):
                    tnumber = f_contname1.pop()
                    tnumber = f"#{tnumber}"
                    contname1 = "_".join(f_contname1)
            
            fcnt1 = len(f_contname1) - 1
            if fcnt1 >= 0:
                fcnt9 = f_contname1[fcnt1]
                if fcnt9.lower() == tname.lower():
                    tname = ""
            
            optn = f"{contname1} {tnumber} {tname} test"
            if re.search(r'test$', tname, re.IGNORECASE):
                optn = f"{contname1} {tnumber} {tname}"
        
        # Process log file
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as fl:
                for line in fl:
                    line = line.rstrip('\n')
                    lineT += 1
                    
                    if not testtesting and not qatesting:
                        # Check compilation error patterns
                        for m, pattern in enumerate(e_patterns):
                            if (pattern and pattern != "CVBFGG" and 
                                pattern in line and 
                                e_ignore[m] not in line and 
                                e_ignore_2[m] not in line and 
                                e_ignore_3[m] not in line and 
                                e_ignore_4[m] not in line and 
                                e_ignore_5[m] not in line):
                                e_count[m] += 1
                                if lineE[m] == 0:
                                    lineE[m] = lineT
                                    lineEValue[m] = line
                        
                        # Check warning patterns
                        for m, pattern in enumerate(e_warning_patterns):
                            if pattern and pattern != "CVBFGG":
                                if '.*' in pattern:
                                    if (re.search(pattern, line) and 
                                        e_warning_patterns_ignore[m] not in line and 
                                        e_warning_patterns_ignore_2[m] not in line):
                                        if not e_warning_patterns_correlators[m] or e_warning_patterns_correlators[m] in line:
                                            w_count[m] += 1
                                            if lineW[m] == 0:
                                                lineW[m] = lineT
                                                lineWValue[m] = line
                                else:
                                    if (pattern in line and 
                                        e_warning_patterns_ignore[m] not in line and 
                                        e_warning_patterns_ignore_2[m] not in line):
                                        if not e_warning_patterns_correlators[m] or e_warning_patterns_correlators[m] in line:
                                            w_count[m] += 1
                                            if lineW[m] == 0:
                                                lineW[m] = lineT
                                                lineWValue[m] = line
                        
                        # Check minor warning patterns
                        for m, pattern in enumerate(e_warning_patterns_minor):
                            if pattern and pattern != "CVBFGG":
                                if '.*' in pattern:
                                    if (re.search(pattern, line) and 
                                        e_warning_patterns_minor_ignore[m] not in line and 
                                        e_warning_patterns_minor_ignore_2[m] not in line and 
                                        e_warning_patterns_minor_ignore_3[m] not in line and 
                                        e_warning_patterns_minor_ignore_4[m] not in line):
                                        w_minor_count[m] += 1
                                        if lineM[m] == 0:
                                            lineM[m] = lineT
                                            lineMValue[m] = line
                                else:
                                    if (pattern in line and 
                                        e_warning_patterns_minor_ignore[m] not in line and 
                                        e_warning_patterns_minor_ignore_2[m] not in line and 
                                        e_warning_patterns_minor_ignore_3[m] not in line and 
                                        e_warning_patterns_minor_ignore_4[m] not in line):
                                        w_minor_count[m] += 1
                                        if lineM[m] == 0:
                                            lineM[m] = lineT
                                            lineMValue[m] = line
                        
                        # Check success patterns
                        bypass_success = pkgname in packages_to_bypass_success
                        for m, pattern in enumerate(e_success):
                            if (pattern in line or bypass_success) and s_count[m] > -1:
                                s_count[m] -= 1
                        
                        for m, pattern in enumerate(e_warning_success):
                            if (pattern in line or bypass_success) and s_w_count[m] > -1:
                                s_w_count[m] -= 1
                    
                    else:  # Test mode
                        # Check test failure patterns
                        for m, pattern in enumerate(e_test_failure):
                            if pattern and pattern != "CVBFGG":
                                matched = False
                                if '.*' in pattern or '(' in pattern:  # Regex patterns
                                    try:
                                        if re.search(pattern, line):
                                            matched = True
                                    except re.error:
                                        if pattern in line:
                                            matched = True
                                else:
                                    if pattern in line:
                                        matched = True
                                
                                if (matched and 
                                    e_test_global_ignore not in line and 
                                    e_test_failure_ignore[m] not in line and 
                                    e_test_failure_ignore_1[m] not in line and 
                                    e_test_failure_ignore_2[m] not in line and 
                                    e_test_failure_ignore_3[m] not in line and 
                                    e_test_failure_ignore_4[m] not in line and 
                                    e_test_failure_ignore_5[m] not in line):
                                    ignr = False
                                    for pattern_addtl in e_test_success_addtl:
                                        if pattern_addtl and pattern_addtl != " " and pattern_addtl in line:
                                            ignr = True
                                            break
                                    if not ignr:
                                        e_count[m] += 1
                                        if lineE[m] == 0:
                                            lineE[m] = lineT
                                            lineEValue[m] = line
                        
                        # Check test warning patterns
                        for m, pattern in enumerate(e_test_warnings):
                            if pattern and pattern != "CVBFGG":
                                matched = False
                                if '.*' in pattern:
                                    try:
                                        if re.search(pattern, line):
                                            matched = True
                                    except re.error:
                                        if pattern in line:
                                            matched = True
                                else:
                                    if pattern in line:
                                        matched = True
                                
                                if matched and e_test_global_ignore not in line:
                                    w_count[m] += 1
                                    if lineW[m] == 0:
                                        lineW[m] = lineT
                                        lineWValue[m] = line
                        
                        # Check test minor warning patterns
                        for m, pattern in enumerate(e_test_warnings_minor):
                            if (pattern and pattern != "CVBFGG" and pattern in line and
                                ARDOC_PROJECT_NAME != e_test_warnings_minor_project_ignore[m] and
                                e_test_global_ignore not in line and
                                e_test_warnings_minor_ignore[m] not in line and
                                e_test_warnings_minor_ignore_1[m] not in line and
                                e_test_warnings_minor_ignore_2[m] not in line and
                                e_test_warnings_minor_ignore_3[m] not in line and
                                e_test_warnings_minor_ignore_4[m] not in line and
                                e_test_warnings_minor_ignore_5[m] not in line):
                                w_minor_count[m] += 1
                                if lineM[m] == 0:
                                    lineM[m] = lineT
                                    lineMValue[m] = line
                        
                        # Check test success patterns
                        for m, pattern in enumerate(e_test_success):
                            if pattern in line and s_count[m] > -1:
                                s_count[m] -= 1
        
        except IOError:
            if not short:
                print(f"ardoc_errortester.py found problem/warning, logfile(s) : {file_path}")
            return
        
        # Determine results
        eeee = ""
        lineEE = 0
        lineEEValue = ""
        
        if not testtesting and not qatesting:
            for m, count in enumerate(e_count):
                if count > 0 and m < len(e_patterns) and e_patterns[m] != "CVBFGG":
                    eeee = e_patterns[m]
                    lineEE = lineE[m]
                    lineEEValue = lineEValue[m]
                    break
        else:
            for m, count in enumerate(e_count):
                if count > 0 and m < len(e_test_failure) and e_test_failure[m] != "CVBFGG":
                    eeee = e_test_failure[m]
                    lineEE = lineE[m]
                    lineEEValue = lineEValue[m]
                    break
        
        # Check for missing success patterns
        ssss = ""
        n_ele = len(e_success) - 1 if not (testtesting or qatesting) else len(e_test_success) - 1
        for m in range(n_ele + 1):
            if m < len(s_count):
                count = s_count[m]
                if count > 0:
                    if testtesting or qatesting:
                        if m < len(e_test_success):
                            ssss = f"{e_test_success[m]}(ABSENCE OF)"
                    else:
                        if m < len(e_success):
                            ssss = f"{e_success[m]}(ABSENCE OF)"
                    break
        
        # Check for missing warning success patterns
        ssww = ""
        n_ele = len(e_warning_success) - 1
        for m in range(n_ele + 1):
            if m < len(s_w_count):
                count = s_w_count[m]
                if count > 0:
                    if not (testtesting or qatesting) and m < len(e_warning_success):
                        ssww = f"{e_warning_success[m]}(ABSENCE OF)"
                    break
        
        # Check warning patterns
        wwww = ""
        lineWW = 0
        lineWWValue = ""
        
        if not testtesting and not qatesting:
            for m, count in enumerate(w_count):
                if count > 0 and m < len(e_warning_patterns) and e_warning_patterns[m] != "CVBFGG":
                    wwww = e_warning_patterns[m]
                    lineWW = lineW[m]
                    lineWWValue = lineWValue[m]
                    if m < len(e_warning_patterns_correlators) and e_warning_patterns_correlators[m]:
                        wwww += f" AND {e_warning_patterns_correlators[m]}"
                    break
        else:
            for m, count in enumerate(w_count):
                if count > 0 and m < len(e_test_warnings) and e_test_warnings[m] != "CVBFGG":
                    wwww = e_test_warnings[m]
                    lineWW = lineW[m]
                    lineWWValue = lineWValue[m]
                    break
        
        # Check minor warning patterns
        wwww_minor = ""
        lineMM = 0
        lineMMValue = ""
        
        if not testtesting and not qatesting:
            for m, count in enumerate(w_minor_count):
                if count > 0 and m < len(e_warning_patterns_minor) and e_warning_patterns_minor[m] != "CVBFGG":
                    wwww_minor = e_warning_patterns_minor[m]
                    lineMM = lineM[m]
                    lineMMValue = lineMValue[m]
                    break
        else:
            for m, count in enumerate(w_minor_count):
                if count > 0 and m < len(e_test_warnings_minor) and e_test_warnings_minor[m] != "CVBFGG":
                    wwww_minor = e_test_warnings_minor[m]
                    lineMM = lineM[m]
                    lineMMValue = lineMValue[m]
                    break
        
        # Generate output based on findings
        mess = "No problems found"
        if light:
            mess = "Test succeeded, based on the exit code (error highlighting off)"
        
        linkline = 0
        linkvalue = ""
        problems = 0
        
        if eeee:
            linkline = lineEE
            linkvalue = lineEEValue
            mess = f"Error pattern found: {eeee}"
            problems = 2
            if not specformat:
                print("=" * 68)
                print(f" {type_name} {compname} has problem. See ")
                print(f" {file_path} ")
                print(f" for pattern(s)  ------ {eeee} -----")
                print("=" * 68)
            else:
                # When option "e" is specified: output in format "G|W|M name directory"
                print(f"G {compname} {ARDOC_TESTLOGDIR} {eeee}")
            if not short:
                sys.exit(2)
        elif ssss:
            linkline = 0
            ssss1 = ssss.replace("(ABSENCE OF)", "")
            mess = f"Required success pattern not found: {ssss1}"
            problems = 2
            if not specformat:
                print("=" * 68)
                print(f" {type_name} {compname} has problem. See ")
                print(f" {file_path} ")
                print(f" for pattern(s)  ------ {ssss} -----")
                print("=" * 68)
            else:
                print(f"G {compname} {ARDOC_TESTLOGDIR} {ssss}")
            if not short:
                sys.exit(2)
        elif wwww:
            linkline = lineWW
            linkvalue = lineWWValue
            mess = f"Serious warning pattern found: {wwww}"
            problems = 1
            if not specformat:
                print("=" * 68)
                print(f" {type_name} {compname} has warning. See ")
                print(f" {file_path} ")
                print(f" for pattern(s)  ------ {wwww} -----")
                print("=" * 68)
            else:
                print(f"W {compname} {ARDOC_TESTLOGDIR} {wwww}")
            if not short:
                sys.exit(2)
        elif ssww:
            linkline = 0
            ssww1 = ssww.replace("(ABSENCE OF)", "")
            mess = f"Essential pattern not found: {ssww1} , this triggers serious warning"
            problems = 2
            if not specformat:
                print("=" * 68)
                print(f" {type_name} {compname} has warning. See ")
                print(f" {file_path} ")
                print(f" for pattern(s)  ------ {ssww} -----")
                print("=" * 68)
            else:
                print(f"W {compname} {ARDOC_TESTLOGDIR} {ssww}")
            if not short:
                sys.exit(2)
        elif wwww_minor:
            linkline = lineMM
            linkvalue = lineMMValue
            mess = f"Minor warning pattern found: {wwww_minor}"
            problems = 0.5
            if not specformat:
                print("=" * 68)
                print(f" {type_name} {compname} has minor warning. See ")
                print(f" {file_path} ")
                print(f" for pattern(s)  ------ {wwww_minor}-----")
                print("=" * 68)
            else:
                print(f"M {compname} {ARDOC_TESTLOGDIR} {wwww_minor}")
            if not short:
                sys.exit(2)
        
        # Generate HTML log when 's' option is specified (note: corrected interpretation)
        if short:
            # HTML generation logic 
            mess2 = ""
            if linkline != 0:
                mess2 = f"&nbsp;<BR>&nbsp;&nbsp;&nbsp;&nbsp;problematic line: </B><BR> &nbsp;&nbsp;&nbsp; <A class=small href=\"#prblm\">{linkvalue}</A><BR><B>"
            
            aid_message_html = f"""<DIV id=hdr0>
<table bordercolor="#6600CC" border=10 cellpadding=5 cellspacing=0 width="100%">
<tr><td class=aid width=20% align=center valign=baseline>
<H1>ARDOC</H1>
</td>
<td class=ttl>
<EM><B><BIG>{optn} logfile</BIG></EM></B>
</td></tr>
<tr><td class=aid>
    version  {ARDOC_VERSION}
</td>
<td class=ttl><EM><B>{mess}</B></EM>
</td>
</tr>
</table>
</DIV>
<DIV id=hdr>
<B>
    {mess2}
    &nbsp;&nbsp;&nbsp;&nbsp;<A href="#end">Link to the last line</A> <BR>
    &nbsp;<BR>
</B></DIV>"""
            
            if filehtml:
                try:
                    with open(filehtml, 'w') as fg:
                        header_print(fg, problems, optn)
                        fg.write(aid_message_html)
                        fg.write('<div id=hdr1>\n')
                        
                        # Add ninja log link if available
                        if not testtesting and not qatesting and ARDOC_NINJALOG and os.path.isfile(ARDOC_NINJALOG):
                            try:
                                with open(ARDOC_NINJALOG, 'r') as ninja_file:
                                    nninja = len(ninja_file.readlines())
                                if nninja > 1:
                                    ARDOC_NINJALOGBASE = os.path.basename(ARDOC_NINJALOG)
                                    ARDOC_NINJAURL = f"{ARDOC_WEBPAGE}/ARDOC_Log_{ARDOC_PROJECT_RELNAME}/{ARDOC_NINJALOGBASE}"
                                    fg.write(f'<b>Ninja logfile</b> can be accessed at <a href="{ARDOC_NINJAURL}">this address</a><BR>\n')
                            except:
                                pass
                        
                        fg.write(f'<b>Original log file:</b><CODE> {file_path} </CODE><BR>\n')
                        fg.write('</div>\n <P><PRE>\n')
                        
                        # Process and write log content with HTML formatting
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as fb:
                                ncount_line = 0
                                for line in fb:
                                    ncount_line += 1
                                    
                                    # HTML escape special characters
                                    line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                                    
                                    if ncount_line == linkline:
                                        fg.write(f'<div id="prblm">{line}</div>')
                                    else:
                                        fg.write(line)
                                    
                                    if ncount_line == lineT:
                                        fg.write('  </PRE>\n')
                                        fg.write('  <div id="end">END OF LOGFILE</div>')
                        except:
                            fg.write("Error reading log file content\n")
                        
                        fg.write('\n  </body>\n  </html>\n')
                        
                    # Copy HTML to web directory
                    filehtml_base = os.path.basename(filehtml)
                    if testtesting:
                        copy_html = os.path.join(ARDOC_WEBDIR, f"ARDOC_TestLog_{ARDOC_PROJECT_RELNAME}", filehtml_base)
                    elif qatesting:
                        copy_html = os.path.join(ARDOC_WEBDIR, f"ARDOC_QALog_{ARDOC_PROJECT_RELNAME}", filehtml_base)
                    else:
                        copy_html = os.path.join(ARDOC_WEBDIR, f"ARDOC_Log_{ARDOC_PROJECT_RELNAME}", filehtml_base)
                    
                    os.system(f"cp -Rp {filehtml} {copy_html}")
                    
                except IOError:
                    pass
        
        # Output success message when no problems found
        if not short and not eeee and not ssss and not wwww and not ssww and not wwww_minor:
            print("(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(.)")
            print(f"         Logfiles of {type_name} {compname} looks OK")
            print("(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(.)")
    
    else:
        if not short:
            print(f"ardoc_errortester.py found problem/warning, logfile(s) : {file_path if 'file_path' in locals() else 'NOT FOUND'}")

if __name__ == "__main__":
    main()
