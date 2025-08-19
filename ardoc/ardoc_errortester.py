#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ardoc_errortester.py - Python migration of ardoc_errortester.pl

Shell script to test logfiles used to determine if rotation can be performed.

Arguments:   
  For build mode (default): <package> <release> <tags_file> <full_package_name>
  For test mode (-t/-q): <test_name> <release>

Author:      A. Undrus
Migrated by: GitHub Copilot
"""

import os
import sys
import re
import argparse
from pathlib import Path
from urllib.parse import quote
import html
import shutil

def header_print(file_handle, problem_level, test_name):
    """Print HTML header with appropriate styling based on problem level."""
    comment = ""
    if problem_level == 0.5:
        comment = "M"
    elif problem_level == 1:
        comment = "W"
    elif problem_level == 2:
        comment = "E"
    
    html_content = f"""<html>
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
    file_handle.write(html_content)

def main():
    """Main function to analyze log files for errors and warnings."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Analyze log files for errors and warnings', add_help=False)
    parser.add_argument('-s', '--short', action='store_true', help='Short format and HTML generation')
    parser.add_argument('-e', '--specformat', action='store_true', help='Special format (G|W|M output)')
    parser.add_argument('-t', '--testtesting', action='store_true', help='Test testing mode')
    parser.add_argument('-q', '--qatesting', action='store_true', help='QA testing mode')
    parser.add_argument('-l', '--light', action='store_true', help='Light analysis mode')
    parser.add_argument('args', nargs='*', help='Positional arguments')
    
    args = parser.parse_args()
    
    # Environment variables
    ardoc_log = os.environ.get("ARDOC_LOG", "")
    ardoc_testlog = os.environ.get("ARDOC_TESTLOG", "")
    ardoc_qalog = os.environ.get("ARDOC_QALOG", "")
    ardoc_home = os.environ.get("ARDOC_HOME", "")
    ardoc_project_name = os.environ.get("ARDOC_PROJECT_NAME", "")
    ardoc_copy_home = os.environ.get("ARDOC_COPY_HOME", "")
    ardoc_work_area = os.environ.get("ARDOC_WORK_AREA", "")
    ardoc_project_relname_copy = os.environ.get("ARDOC_PROJECT_RELNAME_COPY", "")
    ardoc_webdir = os.environ.get("ARDOC_WEBDIR", "")
    ardoc_web_home = os.environ.get("ARDOC_WEB_HOME", "")
    ardoc_webpage = os.environ.get("ARDOC_WEBPAGE", "")
    
    # Determine mode and validate arguments
    if not args.testtesting and not args.qatesting:
        # Build mode
        type_mode = "package"
        type_in_url = "c"
        type_in_html = "build"
        ardoc_testlogdir = Path(ardoc_log).parent if ardoc_log else Path(".")
        
        if len(args.args) != 4:
            print("ardoc_errortester.py:", file=sys.stderr)
            print("Four arguments required: directory_package, release, tags file, package name", file=sys.stderr)
            sys.exit(2)
            
        compname = args.args[0]
        release = args.args[1]
        filename = args.args[2]
        pkgname_full = args.args[3]
    else:
        # Test mode
        type_in_url = "t"
        type_in_html = "test"
        type_mode = "qatest" if args.qatesting else "test"
        
        if args.qatesting:
            ardoc_testlogdir = Path(ardoc_qalog).parent if ardoc_qalog else Path(".")
        else:
            ardoc_testlogdir = Path(ardoc_testlog).parent if ardoc_testlog else Path(".")
            
        if len(args.args) != 2:
            print("ardoc_errortester.py:", file=sys.stderr)
            print("Two arguments required: names of test, release", file=sys.stderr)
            sys.exit(2)
            
        compname = args.args[0]
        release = args.args[1]
        filename = compname  # For test mode, filename is the test name
        pkgname_full = ""
    
    # Extract package name
    pkgname = Path(pkgname_full).name if pkgname_full else ""
    
    # Handle container name logic
    cnt1 = len(re.findall(f"_{re.escape(pkgname)}", compname)) if pkgname else 0
    if cnt1 == 0:
        contname = compname
    else:
        # Simplified container name logic
        contname = re.sub(f"_{re.escape(pkgname)}$", "", compname)
    
    # Get pattern environment variables
    test_success_pattern = os.environ.get("ARDOC_TEST_SUCCESS_PATTERN", "")
    test_failure_pattern = os.environ.get("ARDOC_TEST_FAILURE_PATTERN", "")
    test_warning_pattern = os.environ.get("ARDOC_TEST_WARNING_PATTERN", "")
    build_failure_pattern = os.environ.get("ARDOC_BUILD_FAILURE_PATTERN", "CVBFGG")
    
    if args.qatesting:
        test_success_pattern = os.environ.get("ARDOC_QA_SUCCESS_PATTERN", "")
        test_failure_pattern = os.environ.get("ARDOC_QA_FAILURE_PATTERN", "")
        test_warning_pattern = os.environ.get("ARDOC_QA_WARNING_PATTERN", "")
    
    # Define error patterns for compilation logs
    e_patterns = [
        ": error:", "CMake Error", "runtime error:", "No rule to make target",
        build_failure_pattern, "raceback (most recent", "CVBFGG", "error: ld",
        "error: Failed to execute", "no build logfile"
    ]
    
    e_ignore = ["CVBFGG"] * 9 + [f"for {ardoc_project_name}Release are"]
    e_ignore_2 = ["CVBFGG"] * 9 + [f"for {ardoc_project_name} are"]
    e_ignore_3 = ["CVBFGG"] * 9 + [f"for {ardoc_project_name}RunTime are"]
    
    # Warning patterns for compilation logs
    e_warning_patterns = [
        "Errors/Problems found", "CMake Warning", "CMake Deprecation Warning",
        "Error in", "control reaches end of non-void", "suggest explicit braces",
        "> Warning:", "type qualifiers ignored on function return type",
        "[-Wsequence-point]", "mission denied", "nvcc warning :", "Warning: Fortran",
        r'library.*\sexposes\s+factory.*\sdeclared\s+in'
    ]
    
    e_warning_patterns_correlators = ["", "", "", "", "", "", "", pkgname, "", "", "", "", ""]
    e_warning_patterns_ignore = [
        "Errors/Problems found : 0", "CVBFGG", "CVBFGG", "CVBFGG", "/external", 
        "/external", "> Warning: template", "/external", "/external", "CVBFGG", 
        "CVBFGG", "CVBFGG", "CVBFGG"
    ]
    
    # Minor warning patterns for compilation logs
    e_warning_patterns_minor = [
        ": warning: ", "Warning: the last line", "Warning: Unused class rule",
        r'Warning:\s.*rule', "#pragma message:", r'WARNING\s+.*GAUDI', "CVBFGG", "CVBFGG"
    ]
    
    e_warning_patterns_minor_ignore = [
        "make[", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "ClassIDSvc", "CVBFGG", "CVBFGG"
    ]
    
    # Success patterns
    e_success = ["CVBFGG"] * 10
    e_warning_success = ["CVBFGG", "Package build succeeded"] + ["CVBFGG"] * 6
    packages_to_bypass_success = [ardoc_project_name, f"{ardoc_project_name}Release", f"{ardoc_project_name}RunTime"]
    
    # Test patterns
    e_test_global_ignore = "distcc"
    
    if args.qatesting:
        # QA test patterns
        e_test_failure = [
            "*Timeout", "time quota spent", "*Failed", "ERROR_MESSAGE", "severity=FATAL",
            "Error: execution_error", "command not found", "tests FAILED", "tester: Error",
            "Errors while running CTest"
        ]
        e_test_failure_ignore = [
            "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG",
            "kvt: command not found", "CVBFGG", "CVBFGG", "CVBFGG"
        ]
        e_test_warnings = [test_warning_pattern, "raceback (most recent", "file not found"] + ["CVBFGG"] * 5
        e_test_warnings_minor = ["severity=ERROR", "  ERROR", "No such file or directory"] + ["CVBFGG"] * 5
        e_test_success = ["CVBFGG"] * 10
    else:
        # Integration test patterns
        e_test_failure = [
            "test issue message: Timeout", "test status fail", "*Failed", "TEST FAILURE",
            "severity=FATAL", ": FAILURE ", "command not found", "ERROR_MESSAGE",
            " ERROR ", "exit code: 143", "time quota spent"
        ]
        e_test_failure_ignore = [
            "CVBFGG", "CVBFGG", "CVBFGG", "ctest status notrun", "CVBFGG", "check_log",
            "CVBFGG", "CVBFGG", "check_log", "CVBFGG", "CVBFGG"
        ]
        e_test_failure_ignore_1 = [
            "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG",
            "CVBFGG", "HelloWorld", "CVBFGG", "CVBFGG"
        ]
        e_test_failure_ignore_2 = [
            "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG",
            "CVBFGG", "Cannot interpolate outside histogram", "CVBFGG", "CVBFGG"
        ]
        e_test_failure_ignore_3 = [
            "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG",
            "CVBFGG", "INFO ", "CVBFGG", "CVBFGG"
        ]
        e_test_failure_ignore_4 = [
            "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG",
            "CVBFGG", "ERROR Propa", "CVBFGG", "CVBFGG"
        ]
        e_test_failure_ignore_5 = [
            "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG",
            "CVBFGG", "Acts", "CVBFGG", "CVBFGG"
        ]
        e_test_warnings = [
            test_warning_pattern, "raceback (most recent", "file not found",
            "Logfile error", "Non-zero return", "TEST WARNING", "*Timeout", "CVBFGG"
        ]
        e_test_warnings_minor = [
            "severity=ERROR", "  ERROR", "No such file or directory", "CVBFGG", 
            "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"
        ]
        e_test_warnings_minor_ignore = [
            "CVBFGG", "ERROR (pool)", "INFO", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"
        ]
        e_test_warnings_minor_ignore_1 = [
            "CVBFGG", "ERROR IN", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"
        ]
        e_test_warnings_minor_ignore_2 = [
            "CVBFGG", "ServiceLocatorHelper", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"
        ]
        e_test_warnings_minor_ignore_3 = [
            "CVBFGG", "HelloWorld", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"
        ]
        e_test_warnings_minor_ignore_4 = [
            "CVBFGG", "Cannot interpolate outside histogram", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"
        ]
        e_test_warnings_minor_ignore_5 = [
            "CVBFGG", "Acts", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"
        ]
        e_test_warnings_minor_project_ignore = [
            "CVBFGG", "Athena", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"
        ]
        e_test_success = [
            "Info: test completed", test_success_pattern, "CVBFGG", "CVBFGG",
            "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"
        ]
    
    # Apply light mode restrictions
    if args.light and (args.testtesting or args.qatesting):
        # Disable most patterns for light mode
        e_test_failure = ["CVBFGG"] * len(e_test_failure)
        e_test_warnings = ["CVBFGG"] * len(e_test_warnings)
        e_test_warnings_minor = ["CVBFGG"] * len(e_test_warnings_minor)
        
        # Keep only essential patterns
        e_test_failure[0] = "test issue message: Timeout"
        e_test_failure[1] = "test status fail"
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
    
    # Initialize counters
    e_count = [0] * len(e_patterns)
    w_count = [0] * len(e_warning_patterns)
    w_minor_count = [0] * len(e_warning_patterns_minor)
    s_count = [1] * len(e_success)  # Start with 1 for success patterns
    s_w_count = [1] + [0] * (len(e_warning_success) - 1)
    
    line_e = [0] * len(e_patterns)
    line_w = [0] * len(e_warning_patterns)
    line_m = [0] * len(e_warning_patterns_minor)
    line_e_value = [""] * len(e_patterns)
    line_w_value = [""] * len(e_warning_patterns)
    line_m_value = [""] * len(e_warning_patterns_minor)
    
    # For test modes, use test patterns
    if args.testtesting or args.qatesting:
        s_count = [1] + [0] * (len(e_test_success) - 1)
        s_w_count = [0] * 8
    
    # Process log file
    if not Path(filename).exists():
        if args.specformat:
            print(f"G {compname} {ardoc_testlogdir} logfile not found: {filename}", end="")
        else:
            print(f"no build logfile: {filename}")
        sys.exit(10)
    
    line_t = 0
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line_t = line_num
                line = line.strip()
                
                if args.testtesting or args.qatesting:
                    # Test mode pattern matching
                    for i, pattern in enumerate(e_test_failure):
                        if (pattern != "CVBFGG" and pattern in line and 
                            e_test_global_ignore not in line and
                            e_test_failure_ignore[i] not in line):
                            # Additional ignore checks for integration tests
                            if not args.qatesting:
                                if (e_test_failure_ignore_1[i] in line or
                                    e_test_failure_ignore_2[i] in line or
                                    e_test_failure_ignore_3[i] in line or
                                    e_test_failure_ignore_4[i] in line or
                                    e_test_failure_ignore_5[i] in line):
                                    continue
                            e_count[i] += 1
                            if line_e[i] == 0:
                                line_e[i] = line_num
                                line_e_value[i] = line
                    
                    # Test warnings
                    for i, pattern in enumerate(e_test_warnings):
                        if pattern != "CVBFGG" and pattern in line and e_test_global_ignore not in line:
                            w_count[i] += 1
                            if line_w[i] == 0:
                                line_w[i] = line_num
                                line_w_value[i] = line
                    
                    # Test minor warnings
                    for i, pattern in enumerate(e_test_warnings_minor):
                        if pattern != "CVBFGG" and pattern in line:
                            # Check project ignore and other ignore patterns
                            skip = False
                            if not args.qatesting:
                                if (ardoc_project_name == e_test_warnings_minor_project_ignore[i] or
                                    e_test_global_ignore in line or
                                    e_test_warnings_minor_ignore[i] in line or
                                    e_test_warnings_minor_ignore_1[i] in line or
                                    e_test_warnings_minor_ignore_2[i] in line or
                                    e_test_warnings_minor_ignore_3[i] in line or
                                    e_test_warnings_minor_ignore_4[i] in line or
                                    e_test_warnings_minor_ignore_5[i] in line):
                                    skip = True
                            else:
                                if (e_test_global_ignore in line or
                                    e_test_warnings_minor_ignore[i] in line or
                                    e_test_warnings_minor_ignore_1[i] in line or
                                    e_test_warnings_minor_ignore_2[i] in line):
                                    skip = True
                            
                            if not skip:
                                w_minor_count[i] += 1
                                if line_m[i] == 0:
                                    line_m[i] = line_num
                                    line_m_value[i] = line
                    
                    # Test success patterns
                    for i, pattern in enumerate(e_test_success):
                        if pattern != "CVBFGG" and pattern in line and s_count[i] > -1:
                            s_count[i] -= 1
                
                else:
                    # Build mode pattern matching
                    for i, pattern in enumerate(e_patterns):
                        if (pattern != "CVBFGG" and pattern in line and
                            e_ignore[i] not in line and
                            e_ignore_2[i] not in line and
                            e_ignore_3[i] not in line):
                            e_count[i] += 1
                            if line_e[i] == 0:
                                line_e[i] = line_num
                                line_e_value[i] = line
                    
                    # Warning patterns
                    for i, pattern in enumerate(e_warning_patterns):
                        if pattern != "CVBFGG" and pattern in line:
                            # Check correlator requirement
                            correlator = e_warning_patterns_correlators[i]
                            if correlator and correlator not in line:
                                continue
                            # Check ignore patterns
                            if e_warning_patterns_ignore[i] not in line:
                                w_count[i] += 1
                                if line_w[i] == 0:
                                    line_w[i] = line_num
                                    line_w_value[i] = line
                    
                    # Minor warning patterns
                    for i, pattern in enumerate(e_warning_patterns_minor):
                        if pattern != "CVBFGG" and pattern in line:
                            if e_warning_patterns_minor_ignore[i] not in line:
                                w_minor_count[i] += 1
                                if line_m[i] == 0:
                                    line_m[i] = line_num
                                    line_m_value[i] = line
                    
                    # Success patterns
                    bypass_success = pkgname in packages_to_bypass_success
                    for i, pattern in enumerate(e_success):
                        if (pattern in line or bypass_success) and s_count[i] > -1:
                            s_count[i] -= 1
                    
                    for i, pattern in enumerate(e_warning_success):
                        if (pattern in line or bypass_success) and s_w_count[i] > -1:
                            s_w_count[i] -= 1
    
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Determine results
    eeee = ""
    line_ee = 0
    line_ee_value = ""
    
    wwww = ""
    line_ww = 0
    line_ww_value = ""
    
    wwww_minor = ""
    line_mm = 0
    line_mm_value = ""
    
    ssss = ""
    ssww = ""
    
    # Check for errors
    if args.testtesting or args.qatesting:
        for i, count in enumerate(e_count):
            if count > 0 and e_test_failure[i] != "CVBFGG":
                eeee = e_test_failure[i]
                line_ee = line_e[i]
                line_ee_value = line_e_value[i]
                break
    else:
        for i, count in enumerate(e_count):
            if count > 0 and e_patterns[i] != "CVBFGG":
                eeee = e_patterns[i]
                line_ee = line_e[i]
                line_ee_value = line_e_value[i]
                break
    
    # Check for missing success patterns
    if not eeee:
        if args.testtesting or args.qatesting:
            for i, count in enumerate(s_count):
                if count > 0 and e_test_success[i] != "CVBFGG":
                    ssss = f"(ABSENSE OF) {e_test_success[i]}"
                    break
        else:
            for i, count in enumerate(s_count):
                if count > 0 and e_success[i] != "CVBFGG":
                    ssss = f"(ABSENSE OF) {e_success[i]}"
                    break
    
    # Check for warnings
    if not eeee and not ssss:
        if args.testtesting or args.qatesting:
            for i, count in enumerate(w_count):
                if count > 0 and e_test_warnings[i] != "CVBFGG":
                    wwww = e_test_warnings[i]
                    line_ww = line_w[i]
                    line_ww_value = line_w_value[i]
                    break
        else:
            for i, count in enumerate(w_count):
                if count > 0 and e_warning_patterns[i] != "CVBFGG":
                    wwww = e_warning_patterns[i]
                    line_ww = line_w[i]
                    line_ww_value = line_w_value[i]
                    break
    
    # Check for missing warning success patterns
    if not eeee and not ssss and not wwww:
        if not (args.testtesting or args.qatesting):
            for i, count in enumerate(s_w_count):
                if count > 0 and e_warning_success[i] != "CVBFGG":
                    ssww = f"(ABSENSE OF) {e_warning_success[i]}"
                    break
    
    # Check for minor warnings
    if not eeee and not ssss and not wwww and not ssww:
        if args.testtesting or args.qatesting:
            for i, count in enumerate(w_minor_count):
                if count > 0 and e_test_warnings_minor[i] != "CVBFGG":
                    wwww_minor = e_test_warnings_minor[i]
                    line_mm = line_m[i]
                    line_mm_value = line_m_value[i]
                    break
        else:
            for i, count in enumerate(w_minor_count):
                if count > 0 and e_warning_patterns_minor[i] != "CVBFGG":
                    wwww_minor = e_warning_patterns_minor[i]
                    line_mm = line_m[i]
                    line_mm_value = line_m_value[i]
                    break
    
    # Output results
    problems = 0
    mess = ""
    linkline = 0
    linkvalue = ""
    
    if eeee:
        # Error found
        problems = 2
        mess = f"Error pattern found: {eeee}"
        linkline = line_ee
        linkvalue = line_ee_value
        
        if args.specformat:
            print(f"G {compname} {ardoc_testlogdir} {eeee}", end="")
        else:
            print("=" * 68)
            print(f" {type_mode} {compname} has problem. See")
            print(f" {filename}")
            print(f" for pattern(s)  ------ {eeee} -----")
            print("=" * 68)
        
        if not args.short:
            sys.exit(2)
    
    elif ssss:
        # Missing success pattern
        problems = 2
        ssss1 = ssss.replace("(ABSENSE OF)", "")
        mess = f"Required success pattern not found: {ssss1}"
        linkline = 0
        
        if args.specformat:
            print(f"G {compname} {ardoc_testlogdir} {ssss}", end="")
        else:
            print("=" * 68)
            print(f" {type_mode} {compname} has problem. See")
            print(f" {filename}")
            print(f" for pattern(s)  ------ {ssss} -----")
            print("=" * 68)
        
        if not args.short:
            sys.exit(2)
    
    elif wwww:
        # Warning found
        problems = 1
        mess = f"Serious warning pattern found: {wwww}"
        linkline = line_ww
        linkvalue = line_ww_value
        
        if args.specformat:
            print(f"W {compname} {ardoc_testlogdir} {wwww}", end="")
        else:
            print("=" * 68)
            print(f" {type_mode} {compname} has warning. See")
            print(f" {filename}")
            print(f" for pattern(s)  ------ {wwww} -----")
            print("=" * 68)
        
        if not args.short:
            sys.exit(2)
    
    elif ssww:
        # Missing warning success pattern
        problems = 1
        ssww1 = ssww.replace("(ABSENSE OF)", "")
        mess = f"Essential pattern not found: {ssww1}, this triggers serious warning"
        linkline = 0
        
        if args.specformat:
            print(f"W {compname} {ardoc_testlogdir} {ssww}", end="")
        else:
            print("=" * 68)
            print(f" {type_mode} {compname} has warning. See")
            print(f" {filename}")
            print(f" for pattern(s)  ------ {ssww} -----")
            print("=" * 68)
        
        if not args.short:
            sys.exit(2)
    
    elif wwww_minor:
        # Minor warning found
        problems = 0.5
        mess = f"Minor warning pattern found: {wwww_minor}"
        linkline = line_mm
        linkvalue = line_mm_value
        
        if args.specformat:
            print(f"M {compname} {ardoc_testlogdir} {wwww_minor}", end="")
        else:
            print("=" * 68)
            print(f" {type_mode} {compname} has minor warning. See")
            print(f" {filename}")
            print(f" for pattern(s)  ------ {wwww_minor} -----")
            print("=" * 68)
        
        if not args.short:
            sys.exit(2)
    
    else:
        # No problems found
        if not args.short:
            print("(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)") 
            print(f"         Logfiles of {type_mode} {compname} looks OK")
            print("(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)") 
    
    # HTML Generation
    if args.short:
        # Generate HTML file
        ardoc_testlogdirbase = ardoc_testlogdir.name
        filebase1 = Path(filename).name
        filehtml = ardoc_testlogdir / f"{compname}.html"
        
        # Prepare message for HTML
        mess2 = ""
        if linkline != 0:
            mess2 = f'&nbsp;<BR>&nbsp;&nbsp;&nbsp;&nbsp;problematic line: </B><BR> &nbsp;&nbsp;&nbsp; <A class=small href="#prblm">{html.escape(linkvalue)}</A><BR><B>'
        
        aid_message_html = f"""
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
</B></DIV>
"""
        
        try:
            with open(filehtml, 'w', encoding='utf-8') as fg:
                # Write HTML header
                header_print(fg, problems, f"{type_mode} {compname}")
                
                # Write message HTML
                fg.write(aid_message_html)
                fg.write('<div id=hdr1>\n')
                
                if not args.testtesting and not args.qatesting:
                    fg.write('<b><i>Placeholder for a link to GitLab</i></b><BR>\n')
                
                fg.write(f'<b>Original log file:</b><CODE> {filename} </CODE><BR>\n')
                
                # Web links (if configured)
                if ardoc_web_home:
                    webloc = f"{ardoc_web_home}/{ardoc_project_relname_copy}/ARDOC_area/{ardoc_testlogdirbase}/{filebase1}"
                
                if ardoc_webpage:
                    ardoc_nightly_name = os.environ.get("ARDOC_NIGHTLY_NAME", "")
                    ardoc_arch = os.environ.get("ARDOC_ARCH", "")
                    ardoc_project_relnumb_copy = os.environ.get("ARDOC_PROJECT_RELNUMB_COPY", "")
                    
                    websum_d = f"http://atlas-nightlies-browser.cern.ch/~platinum/nightlies/info?tp={type_in_url}&nightly={ardoc_nightly_name}&rel={ardoc_project_relname_copy}&ar={ardoc_arch}&proj={ardoc_project_name}"
                    websum = f"{ardoc_webpage}/ardoc_{type_in_html}summary_{ardoc_project_relnumb_copy}.html"
                
                fg.write('</div>\n <P><PRE>\n')
                
                # Set up line limits for different log types
                total_ln = 5000
                first_part = 3000
                middle_part1 = 25
                middle_part2 = 25
                last_part = 2000
                
                if args.testtesting:
                    mr_training_domain = os.environ.get("MR_TRAINING_DOMAIN", "")
                    mr_current_git_branch = os.environ.get("MR_CURRENT_GIT_BRANCH", "")
                    
                    if mr_training_domain:
                        fg.write(f"Note: this MR training job probes domain {mr_training_domain}, git branch {mr_current_git_branch}\n")
                    
                    if "unit-tests" in filename:
                        fg.write("Note: there is limit of 75000 lines for this logfile. Excess lines (if any) are truncated.\n")
                        total_ln = 75000
                        first_part = 40000
                        middle_part1 = 250
                        middle_part2 = 250
                        last_part = 35000
                    else:
                        fg.write("Note: there is limit of 20000 lines for this logfile. Excess lines (if any) are truncated.\n")
                        total_ln = 20000
                        first_part = 12000
                        middle_part1 = 100
                        middle_part2 = 100
                        last_part = 8000
                
                # Calculate allowed line ranges
                allowed_ranges = []
                if line_t <= total_ln:
                    allowed_ranges.append((0, total_ln))
                else:
                    allowed_ranges.append((0, first_part))
                    brd = line_t - last_part + 1
                    allowed_ranges.append((brd, line_t))
                    
                    if linkline != 0:
                        brd_e1 = max(0, linkline - middle_part1)
                        brd_e2 = min(line_t, linkline + middle_part2)
                        allowed_ranges.append((brd_e1, brd_e2))
                
                # Process log file for HTML output
                ncount_line = 0
                first_line = "ExecTest.stdout:"
                first_line_ok = True
                first_arr = []
                last_line = "qmtest.target:"
                last_line_sea = line_t - 5
                first_line_sea = 3
                
                if first_line_sea >= line_t - 1:
                    first_line_sea = line_t - 1
                
                line_ok_2 = True
                ncount_s = 0
                
                try:
                    with open(filename, 'r', encoding='utf-8', errors='ignore') as fb:
                        for line_content in fb:
                            ncount_line += 1
                            line_ok_1 = True
                            line_ok = False
                            
                            # Handle special time stamps
                            if "qmtest.end_time" in line_content or "qmtest.start_time" in line_content:
                                line_content = line_content.rstrip() + " (GMT time)\n"
                            
                            # Handle first line detection
                            if ncount_line < first_line_sea and first_line_ok:
                                line_ok_1 = False
                                line_nosp = line_content.replace(" ", "").strip()
                                if line_nosp == first_line:
                                    first_line_ok = False
                                first_arr.append(line_content)
                            
                            if ncount_line == first_line_sea and first_line_ok:
                                first_line_ok = False
                                for f_line in first_arr:
                                    if ("CI_TEST" not in f_line or "href" not in f_line) and ("test" not in f_line or "tailoring" not in f_line or "href" not in f_line):
                                        encode_line = html.escape(f_line)
                                    else:
                                        encode_line = f_line
                                    fg.write(encode_line)
                            
                            # Handle last line detection
                            if ncount_line > last_line_sea:
                                line_nosp = line_content.replace(" ", "").strip()
                                if line_nosp == last_line:
                                    line_ok_2 = False
                            
                            # Check if line should be included
                            for start, end in allowed_ranges:
                                if start <= ncount_line <= end:
                                    line_ok = True
                                    break
                            
                            if not line_ok:
                                ncount_s = 0
                            
                            if line_ok:
                                if ncount_line != linkline:
                                    ncount_s += 1
                                    if ncount_s == 1 and ncount_line > 1:
                                        fg.write("""<DIV ID=hdr>................................................................<BR>
.....LINES TRUNCATED <BR>
.....first """ + str(first_part) + """ lines, bottom """ + str(last_part) + """ lines <BR>
.....as well as lines around error messsage are displayed <BR>
................................................................
</DIV>
""")
                                    
                                    if line_ok_1 and line_ok_2:
                                        if ("CI_TEST" not in line_content or "href" not in line_content) and ("test" not in line_content or "tailoring" not in line_content or "href" not in line_content):
                                            escp = html.escape(line_content)
                                        else:
                                            escp = line_content
                                        fg.write(escp)
                                else:
                                    # This is the problematic line
                                    if ("CI_TEST" not in line_content or "href" not in line_content) and ("test" not in line_content or "tailoring" not in line_content or "href" not in line_content):
                                        escp = html.escape(line_content)
                                    else:
                                        escp = line_content
                                    fg.write(f'<div id="prblm">{escp}</div>')
                                    ncount_s += 1
                                
                                if ncount_line == line_t:
                                    fg.write("  </PRE>\n")
                                    fg.write('  <div id="end">END OF LOGFILE</div>')
                
                except Exception as e:
                    fg.write(f"Error processing log file: {e}\n")
                
                # Close HTML
                fg.write("\n  </body>\n  </html>\n")
        
        except Exception as e:
            print(f"Error generating HTML file: {e}", file=sys.stderr)
        
        # Copy HTML file to web directory
        if ardoc_webdir and filehtml.exists():
            filehtml_base = filehtml.name
            
            if args.testtesting:
                copy_html = Path(ardoc_webdir) / f"ARDOC_TestLog_{ardoc_project_relname_copy}" / filehtml_base
            elif args.qatesting:
                copy_html = Path(ardoc_webdir) / f"ARDOC_QALog_{ardoc_project_relname_copy}" / filehtml_base
            else:
                copy_html = Path(ardoc_webdir) / f"ARDOC_Log_{ardoc_project_relname_copy}" / filehtml_base
            
            try:
                copy_html.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(filehtml, copy_html)
            except Exception as e:
                print(f"Warning: Could not copy HTML to web directory: {e}", file=sys.stderr)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
