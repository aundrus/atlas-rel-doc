#!/usr/bin/env python3
"""
Python migration of ardoc_errortester.pl
Author: Migration by GitHub Copilot (original: A. Undrus)
"""
import os
import sys
import re
import argparse
from pathlib import Path
from html import escape

# --- Argument parsing ---
def parse_args():
    parser = argparse.ArgumentParser(description='Test logfiles for errors/warnings and generate HTML report.')
    parser.add_argument('-s', action='store_true', help='Short output')
    parser.add_argument('-e', action='store_true', help='Special format output')
    parser.add_argument('-t', action='store_true', help='Testtesting mode')
    parser.add_argument('-q', action='store_true', help='QAtesting mode')
    parser.add_argument('-l', action='store_true', help='Light mode (limited error analysis)')
    parser.add_argument('args', nargs='*', help='Arguments as in the Perl script')
    return parser.parse_args()

# --- Environment variable reading ---
def get_env_vars():
    env = {}
    keys = [
        'ARDOC_LOG', 'ARDOC_TESTLOG', 'ARDOC_NINJALOG', 'ARDOC_HOME',
        'ARDOC_PROJECT_NAME', 'ARDOC_PROJECT_RELNAME',
        'ARDOC_TEST_SUCCESS_PATTERN', 'ARDOC_TEST_FAILURE_PATTERN', 'ARDOC_TEST_WARNING_PATTERN', 'ARDOC_BUILD_FAILURE_PATTERN',
        'ARDOC_QA_SUCCESS_PATTERN', 'ARDOC_QA_FAILURE_PATTERN', 'ARDOC_QA_WARNING_PATTERN',
        'ARDOC_WEBDIR', 'ARDOC_WEBPAGE', 'ARDOC_QALOG'
    ]
    for k in keys:
        env[k] = os.environ.get(k, '')
    return env

# --- Pattern setup (partial, for demonstration) ---
E_PATTERNS = [
    r": error:", r"CMake Error", r"runtime error:", r"No rule to make target", r"SyntaxError:",
    r"raceback (most recent", r"CVBFGG", r"error: ld", r"error: Failed to execute", r"no build logfile"
]
E_IGNORE = [
    r"CVBFGG", r"CVBFGG", r"CVBFGG", r"CVBFGG", r"CVBFGG", r"CVBFGG", r"CVBFGG", r"CVBFGG", r"CVBFGG", r"for NICOS_PROJECT_NAMERelease are"
]

# --- Additional patterns (warnings, minor warnings, success) ---
W_PATTERNS = [
    r"Errors/Problems found", r"CMake Warning", r"CMake Deprecation Warning", r"Error in", r"control reaches end of non-void",
    r"suggest explicit braces", r"> Warning:", r"type qualifiers ignored on function return type", r"\[-Wsequence-point\]", r"mission denied",
    r"nvcc warning :", r"Warning: Fortran", r"library.*\\sexposes\\s+factory.*\\sdeclared\\s+in"
]
W_IGNORE = [
    r"Errors/Problems found : 0", r"CVBFGG", r"CVBFGG", r"msg", r"/external", r"/external", r"> Warning: template", r"/external", r"/external", r"CVBFGG", r"CVBFGG", r"CVBFGG", r"CVBFGG"
]
M_PATTERNS = [
    r": warning: ", r"Warning: the last line", r"Warning: Unused class rule", r"Warning:\\s.*rule", r"#pragma message:", r"WARNING\\s+.*GAUDI", r"CVBFGG"
]
M_IGNORE = [
    r"make[", r"CVBFGG", r"CVBFGG", r"CVBFGG", r"CVBFGG", r"ClassIDSvc", r"CVBFGG"
]
S_PATTERNS = [
    r"CVBFGG", r"Package build succeeded", r"CVBFGG", r"CVBFGG", r"CVBFGG", r"CVBFGG", r"CVBFGG", r"CVBFGG"
]

# --- HTML header ---
def header_print(f, prblm, test_nm):
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
{test_nm} Logfile
</title>
</head>
<BODY class=body marginwidth=\"0\" marginheight=\"0\" topmargin=\"0\" leftmargin=\"0\">
""")

# --- Generalized log scanning ---
def scan_log(logfile, patterns, ignores):
    found = []
    with open(logfile, 'r', errors='ignore') as f:
        for lineno, line in enumerate(f, 1):
            for i, pat in enumerate(patterns):
                if pat and re.search(pat, line) and not re.search(ignores[i], line):
                    found.append((lineno, pat, line.strip()))
    return found

# --- HTML report writing ---
def write_html_report(html_path, prblm, test_nm, summary, findings, logfile):
    with open(html_path, 'w') as f:
        header_print(f, prblm, test_nm)
        f.write(f"<div id=hdr1><b>Original log file:</b><code> {escape(logfile)} </code><br></div>\n<p><pre>\n")
        f.write(f"<b>{escape(summary)}</b><br>\n")
        for lineno, pat, line in findings:
            f.write(f"<div id='prblm'>Line {lineno}: Pattern '{escape(pat)}' in: {escape(line)}</div>\n")
        f.write("</pre></body></html>\n")

# --- Main logic (expanded with warnings and success) ---
def main():
    args = parse_args()
    env = get_env_vars()
    argv = args.args
    # Parse flags
    short = args.s
    specformat = args.e
    testtesting = args.t
    qatesting = args.q
    light = args.l
    if len(argv) < 4:
        print("ardoc_errortester.py: Four arguments required: directory_package, release, tags file, package name")
        sys.exit(2)
    directory_package, release, tags_file, package_name = argv[:4]
    logdir = Path(directory_package)
    logfiles = list(logdir.glob('*.log*'))
    if not logfiles:
        print(f"No log files found in {logdir}")
        sys.exit(1)
    logfile = str(logfiles[0])
    print(f"Scanning {logfile} for error, warning, and success patterns...")
    errors = scan_log(logfile, E_PATTERNS, E_IGNORE)
    warnings = scan_log(logfile, W_PATTERNS, W_IGNORE)
    minors = scan_log(logfile, M_PATTERNS, M_IGNORE)
    successes = scan_log(logfile, S_PATTERNS, ["CVBFGG"]*len(S_PATTERNS))
    html_path = str(Path(logfile).with_suffix('.html'))
    if testtesting or qatesting:
        # Adjust logic for test/QA modes (stub, expand as needed)
        print("Test/QA mode enabled. (Further logic to be implemented as in Perl script)")
    if light:
        print("Light mode enabled. (Limited error analysis)")
    if errors:
        summary = "Error pattern(s) found."
        write_html_report(html_path, 2, package_name, summary, errors, logfile)
        print(f"Found error patterns. HTML report written to {html_path}")
        sys.exit(2)
    elif warnings:
        summary = "Warning pattern(s) found."
        write_html_report(html_path, 1, package_name, summary, warnings, logfile)
        print(f"Found warning patterns. HTML report written to {html_path}")
        sys.exit(1)
    elif minors:
        summary = "Minor warning pattern(s) found."
        write_html_report(html_path, 0.5, package_name, summary, minors, logfile)
        print(f"Found minor warning patterns. HTML report written to {html_path}")
        sys.exit(0)
    elif not successes:
        summary = "No success pattern found. This may indicate a problem."
        write_html_report(html_path, 2, package_name, summary, [], logfile)
        print(f"No success pattern found. HTML report written to {html_path}")
        sys.exit(2)
    else:
        summary = "No problems found. Logfile looks OK."
        write_html_report(html_path, 0, package_name, summary, [], logfile)
        print(f"No problems found. HTML report written to {html_path}")
        sys.exit(0)

if __name__ == "__main__":
    main()
