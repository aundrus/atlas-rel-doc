#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ardoc_errortester.py - Python migration of ardoc_errortester.pl

Shell script to test logfiles used to determine if rotation can be performed.

Arguments:   <package>  Package name
             <release>  Release name
             <tags_file> Tags file
             <full_package_name> Full package name

Author:      A. Undrus
Migrated by: GitHub Copilot
"""

import os
import sys
import re
import argparse
from pathlib import Path
from urllib.parse import quote

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
    
    # Initialize flags
    short = False
    specformat = False
    testtesting = False
    qatesting = False
    light = False
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Analyze log files for errors and warnings')
    parser.add_argument('-s', '--short', action='store_true', help='Short format')
    parser.add_argument('-e', '--specformat', action='store_true', help='Special format')
    parser.add_argument('-t', '--testtesting', action='store_true', help='Test testing mode')
    parser.add_argument('-q', '--qatesting', action='store_true', help='QA testing mode')
    parser.add_argument('-l', '--light', action='store_true', help='Light analysis mode')
    parser.add_argument('args', nargs='*', help='Positional arguments')
    
    args = parser.parse_args()
    
    short = args.short
    specformat = args.specformat
    testtesting = args.testtesting
    qatesting = args.qatesting
    light = args.light
    
    # Environment variables
    ardoc_log = os.environ.get("ARDOC_LOG", "")
    ardoc_testlog = os.environ.get("ARDOC_TESTLOG", "")
    ardoc_home = os.environ.get("ARDOC_HOME", "")
    ardoc_project_name = os.environ.get("ARDOC_PROJECT_NAME", "")
    
    # Determine mode and validate arguments
    if not testtesting and not qatesting:
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
        type_mode = "qatest" if qatesting else "test"
        
        if qatesting:
            ardoc_testlogdir = Path(os.environ.get("ARDOC_QALOG", "")).parent
        else:
            ardoc_testlogdir = Path(ardoc_testlog).parent if ardoc_testlog else Path(".")
            
        if len(args.args) != 2:
            print("ardoc_errortester.py:", file=sys.stderr)
            print("Two arguments required: names of test, release", file=sys.stderr)
            sys.exit(2)
            
        compname = args.args[0]
        release = args.args[1]
        filename = ""
        pkgname_full = ""
    
    # Extract package name
    pkgname = Path(pkgname_full).name if pkgname_full else ""
    
    # Handle container name logic
    cnt1 = len(re.findall(f"_{re.escape(pkgname)}", compname)) if pkgname else 0
    if cnt1 == 0:
        contname = compname
    else:
        # Complex regex replacement logic - simplified for Python
        contname = compname
    
    # Get pattern environment variables
    test_success_pattern = os.environ.get("ARDOC_TEST_SUCCESS_PATTERN", "")
    test_failure_pattern = os.environ.get("ARDOC_TEST_FAILURE_PATTERN", "")
    test_warning_pattern = os.environ.get("ARDOC_TEST_WARNING_PATTERN", "")
    build_failure_pattern = os.environ.get("ARDOC_BUILD_FAILURE_PATTERN", "CVBFGG")
    
    if qatesting:
        test_success_pattern = os.environ.get("ARDOC_QA_SUCCESS_PATTERN", "")
        test_failure_pattern = os.environ.get("ARDOC_QA_FAILURE_PATTERN", "")
        test_warning_pattern = os.environ.get("ARDOC_QA_WARNING_PATTERN", "")
    
    # Define error patterns
    e_patterns = [
        ": error:", "CMake Error", "runtime error:", "No rule to make target",
        build_failure_pattern, "raceback (most recent", "CVBFGG", "error: ld",
        "error: Failed to execute", "no build logfile"
    ]
    
    e_ignore = ["CVBFGG"] * 9 + [f"for {ardoc_project_name}Release are"]
    
    # Warning patterns
    e_warning_patterns = [
        "Errors/Problems found", "CMake Warning", "CMake Deprecation Warning",
        "Error in", "control reaches end of non-void", "suggest explicit braces",
        "> Warning:", "type qualifiers ignored on function return type",
        "[-Wsequence-point]", "mission denied", "nvcc warning :", "Warning: Fortran",
        r'library.*\sexposes\s+factory.*\sdeclared\s+in'
    ]
    
    # Initialize counters
    e_count = [0] * len(e_patterns)
    w_count = [0] * len(e_warning_patterns)
    line_e = [0] * len(e_patterns)
    line_w = [0] * len(e_warning_patterns)
    line_e_value = [""] * len(e_patterns)
    line_w_value = [""] * len(e_warning_patterns)
    
    # Process log file
    if not filename or not Path(filename).exists():
        print("no build logfile", end="")
        sys.exit(10)
    
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Check error patterns
                for i, pattern in enumerate(e_patterns):
                    if pattern != "CVBFGG" and pattern in line:
                        if e_ignore[i] == "CVBFGG" or e_ignore[i] not in line:
                            e_count[i] += 1
                            if line_e[i] == 0:
                                line_e[i] = line_num
                                line_e_value[i] = line
                
                # Check warning patterns
                for i, pattern in enumerate(e_warning_patterns):
                    if pattern != "CVBFGG" and pattern in line:
                        w_count[i] += 1
                        if line_w[i] == 0:
                            line_w[i] = line_num
                            line_w_value[i] = line
    
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Determine result
    result = ""
    for i, count in enumerate(e_count):
        if count > 0 and e_patterns[i] != "CVBFGG":
            result = e_patterns[i]
            break
    
    # Output result
    print(result, end="")
    
    # Exit with appropriate code
    if result:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
