#!/usr/bin/env python3
"""
Python migration of ardoc_errortester.pl
Scans logfiles for error and warning patterns
Results output in format "G|W|M name directory" to stdout (empty if log is OK)
Generates HTML formatted log unless option "s" is specified
Type of logfile: compilation by default, QA test if option "q", integration test if "t"
With light option "l" most error and warning patterns are invalidated for test log analysis

Author: Migration from A. Undrus's Perl script
"""
import os
import sys
import re
import argparse
from pathlib import Path
from html import escape
import subprocess
import shutil

def parse_args():
    """Parse command line arguments similar to the original Perl script"""
    # Handle combined flags like -es, -tel, etc.
    args = sys.argv[1:]
    
    short = False
    specformat = False
    testtesting = False
    qatesting = False
    light = False
    
    # Process combined flags
    if args and args[0].startswith('-') and re.match(r'^-[qstel]+$', args[0]):
        flags = args[0][1:]  # Remove the '-'
        if 's' in flags:
            short = True
        if 'e' in flags:
            specformat = True
        if 't' in flags:
            testtesting = True
        if 'q' in flags:
            qatesting = True
        if 'l' in flags:
            light = True
        args = args[1:]  # Remove the flag argument
    
    return short, specformat, testtesting, qatesting, light, args

def get_env_vars():
    """Get required environment variables"""
    return {
        'ARDOC_LOG': os.environ.get('ARDOC_LOG', ''),
        'ARDOC_TESTLOG': os.environ.get('ARDOC_TESTLOG', ''),
        'ARDOC_NINJALOG': os.environ.get('ARDOC_NINJALOG', ''),
        'ARDOC_HOME': os.environ.get('ARDOC_HOME', ''),
        'ARDOC_PROJECT_NAME': os.environ.get('ARDOC_PROJECT_NAME', ''),
        'ARDOC_PROJECT_RELNAME': os.environ.get('ARDOC_PROJECT_RELNAME', ''),
        'ARDOC_TEST_SUCCESS_PATTERN': os.environ.get('ARDOC_TEST_SUCCESS_PATTERN', ''),
        'ARDOC_TEST_FAILURE_PATTERN': os.environ.get('ARDOC_TEST_FAILURE_PATTERN', ''),
        'ARDOC_TEST_WARNING_PATTERN': os.environ.get('ARDOC_TEST_WARNING_PATTERN', ''),
        'ARDOC_BUILD_FAILURE_PATTERN': os.environ.get('ARDOC_BUILD_FAILURE_PATTERN', ''),
        'ARDOC_QA_SUCCESS_PATTERN': os.environ.get('ARDOC_QA_SUCCESS_PATTERN', ''),
        'ARDOC_QA_FAILURE_PATTERN': os.environ.get('ARDOC_QA_FAILURE_PATTERN', ''),
        'ARDOC_QA_WARNING_PATTERN': os.environ.get('ARDOC_QA_WARNING_PATTERN', ''),
        'ARDOC_WEBDIR': os.environ.get('ARDOC_WEBDIR', ''),
        'ARDOC_WEBPAGE': os.environ.get('ARDOC_WEBPAGE', ''),
        'ARDOC_QALOG': os.environ.get('ARDOC_QALOG', ''),
    }

def get_error_patterns(light=False):
    """Define error patterns - most are invalidated in light mode for test log analysis"""
    if light:
        return [
            r"ERROR ",
            r"exit code: 143",
            r"tests FAILED",
            r"time quota spent"
        ]
    else:
        return [
            r": error:",
            r"CMake Error",
            r"runtime error:",
            r"No rule to make target",
            r"SyntaxError:",
            r"Traceback \(most recent",
            r"error: ld",
            r"error: Failed to execute",
            r"no build logfile",
            r"ERROR ",
            r"exit code: 143",
            r"tests FAILED",
            r"time quota spent"
        ]

def get_warning_patterns(light=False):
    """Define warning patterns - most are invalidated in light mode for test log analysis"""
    if light:
        return [
            r"WARNING",
            r"FAILED"
        ]
    else:
        return [
            r"Errors/Problems found",
            r"CMake Warning",
            r"CMake Deprecation Warning",
            r"Error in",
            r"control reaches end of non-void",
            r"suggest explicit braces",
            r"> Warning:",
            r"type qualifiers ignored on function return type",
            r"\[-Wsequence-point\]",
            r"permission denied",
            r"nvcc warning :",
            r"Warning: Fortran",
            r"library.*\s+exposes\s+factory.*\s+declared\s+in"
        ]

def get_minor_warning_patterns(light=False):
    """Define minor warning patterns"""
    if light:
        return []
    else:
        return [
            r": warning: ",
            r"Warning: the last line",
            r"Warning: Unused class rule",
            r"Warning:\s.*rule",
            r"#pragma message:",
            r"WARNING\s+.*GAUDI"
        ]

def get_success_patterns():
    """Define success patterns"""
    return [
        r"Package build succeeded",
        r"Build succeeded",
        r"SUCCESS"
    ]

def header_print(f, prblm, test_nm):
    """Generate HTML header"""
    comment = ''
    if prblm == 0.5:
        comment = 'M'
    elif prblm == 1:
        comment = 'W'
    elif prblm == 2:
        comment = 'E'
    
    f.write(f"""<html>
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
{escape(test_nm)} Logfile
</title>
</head>
<BODY class=body marginwidth="0" marginheight="0" topmargin="0" leftmargin="0">
""")

def scan_log_for_patterns(logfile, patterns):
    """Scan logfile for specific patterns"""
    found_patterns = []
    try:
        with open(logfile, 'r', encoding='utf-8', errors='ignore') as f:
            for lineno, line in enumerate(f, 1):
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        found_patterns.append((lineno, pattern, line.strip()))
                        break  # Only report first match per line
    except Exception as e:
        print(f"Error reading logfile {logfile}: {e}", file=sys.stderr)
    
    return found_patterns

def write_html_report(html_path, prblm, test_nm, logfile, error_patterns, warning_patterns, minor_patterns, short=False):
    """Write HTML report"""
    if short:
        return  # No HTML in short mode
    
    try:
        with open(html_path, 'w', encoding='utf-8') as f:
            header_print(f, prblm, test_nm)
            f.write(f"<div id=hdr1><b>Original log file:</b><code> {escape(logfile)} </code><br></div>\n<p><pre>\n")
            
            if error_patterns:
                f.write(f"<b>ERROR PATTERNS FOUND:</b><br>\n")
                for lineno, pattern, line in error_patterns:
                    f.write(f"<div id='prblm'>Line {lineno}: Pattern '{escape(pattern)}' in: {escape(line)}</div>\n")
                f.write("<br>\n")
            
            if warning_patterns:
                f.write(f"<b>WARNING PATTERNS FOUND:</b><br>\n")
                for lineno, pattern, line in warning_patterns:
                    f.write(f"<div id='prblm'>Line {lineno}: Pattern '{escape(pattern)}' in: {escape(line)}</div>\n")
                f.write("<br>\n")
            
            if minor_patterns:
                f.write(f"<b>MINOR WARNING PATTERNS FOUND:</b><br>\n")
                for lineno, pattern, line in minor_patterns:
                    f.write(f"<div id='prblm'>Line {lineno}: Pattern '{escape(pattern)}' in: {escape(line)}</div>\n")
                f.write("<br>\n")
            
            f.write("</pre></body></html>\n")
    except Exception as e:
        print(f"Error writing HTML report {html_path}: {e}", file=sys.stderr)

def main():
    short, specformat, testtesting, qatesting, light, args = parse_args()
    env = get_env_vars()
    
    # Determine log type and required arguments
    if not testtesting and not qatesting:
        # Build/compilation log
        type_name = "package"
        type_in_url = "c"
        type_in_html = "build"
        ardoc_testlogdir = os.path.dirname(env['ARDOC_LOG']) if env['ARDOC_LOG'] else ""
        
        if len(args) != 4:
            if not specformat:
                print("ardoc_errortester:")
                print("Four arguments required: directory_package, release, tags file, package name")
            sys.exit(2)
        
        directory_package, release, tags_file, package_name = args
    else:
        # Test log (t) or QA test log (q)
        type_in_url = "t"
        type_in_html = "test"
        type_name = "test"
        
        if qatesting:
            type_name = "qatest"
            ardoc_testlogdir = os.path.dirname(env['ARDOC_QALOG']) if env['ARDOC_QALOG'] else ""
        else:
            ardoc_testlogdir = os.path.dirname(env['ARDOC_TESTLOG']) if env['ARDOC_TESTLOG'] else ""
        
        if len(args) != 2:
            if not specformat:
                print("ardoc_errortester:")
                print(f"Two arguments required: names of test, release {args}")
            sys.exit(2)
        
        directory_package, release = args
        tags_file = ""
        package_name = directory_package
    
    compname = directory_package
    
    if specformat and not testtesting and not qatesting:
        if not specformat:
            print(f"=== CHECK logfiles related to {compname} in {release}")
    
    # Find logfiles
    logdir = Path(directory_package)
    if not logdir.exists() or not logdir.is_dir():
        # Try to find logs in standard locations
        if testtesting and env['ARDOC_TESTLOG']:
            potential_logfiles = [env['ARDOC_TESTLOG']]
        elif qatesting and env['ARDOC_QALOG']:
            potential_logfiles = [env['ARDOC_QALOG']]
        elif env['ARDOC_LOG']:
            potential_logfiles = [env['ARDOC_LOG']]
        else:
            if not specformat:
                print(f"No log files found in {logdir}")
            sys.exit(2)
    else:
        potential_logfiles = list(logdir.glob('*.log*'))
        if not potential_logfiles:
            if not specformat:
                print(f"No log files found in {logdir}")
            sys.exit(2)
    
    # Process the first logfile found
    logfile = str(potential_logfiles[0])
    
    # Scan for patterns
    error_patterns = scan_log_for_patterns(logfile, get_error_patterns(light))
    warning_patterns = scan_log_for_patterns(logfile, get_warning_patterns(light))
    minor_patterns = scan_log_for_patterns(logfile, get_minor_warning_patterns(light))
    success_patterns = scan_log_for_patterns(logfile, get_success_patterns())
    
    # Generate HTML path
    html_path = str(Path(logfile).with_suffix('.html'))
    
    # Determine result and generate appropriate output
    result_code = 0
    result_type = ""
    
    if error_patterns:
        result_code = 2
        result_type = "G"  # Error
        problem_level = 2
        if not short:
            write_html_report(html_path, problem_level, package_name, logfile, error_patterns, warning_patterns, minor_patterns, short)
        
        if specformat:
            print(f" {type_name} {compname} has problem. See ")
            print(f"G {compname} {ardoc_testlogdir} {html_path}")
        else:
            # Standard output format: "G|W|M name directory"
            print(f"G {compname} {ardoc_testlogdir}")
        
    elif warning_patterns:
        result_code = 2
        result_type = "W"  # Warning
        problem_level = 1
        if not short:
            write_html_report(html_path, problem_level, package_name, logfile, error_patterns, warning_patterns, minor_patterns, short)
        
        if specformat:
            print(f" {type_name} {compname} has warning. See ")
            print(f"W {compname} {ardoc_testlogdir} {html_path}")
        else:
            # Standard output format: "G|W|M name directory"
            print(f"W {compname} {ardoc_testlogdir}")
        
    elif minor_patterns:
        result_code = 2
        result_type = "M"  # Minor warning
        problem_level = 0.5
        if not short:
            write_html_report(html_path, problem_level, package_name, logfile, error_patterns, warning_patterns, minor_patterns, short)
        
        if specformat:
            print(f" {type_name} {compname} has minor warning. See ")
            print(f"M {compname} {ardoc_testlogdir} {html_path}")
        else:
            # Standard output format: "G|W|M name directory"
            print(f"M {compname} {ardoc_testlogdir}")
        
    else:
        # No problems found
        result_code = 0
        if not short:
            write_html_report(html_path, 0, package_name, logfile, [], [], [], short)
        
        if specformat:
            print(f"         Logfiles of {type_name} {compname} looks OK")
        # No stdout output for OK case (empty if log is OK)
    
    sys.exit(result_code)

if __name__ == "__main__":
    main()
