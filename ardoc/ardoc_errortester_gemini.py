#!/usr/bin/env python3
#
#-----------------------------------------------------------------------------
#
# ardoc_errortester_gemini.py <package> <release>
#
# Python script to test logfiles, migrated from ardoc_errortester.pl.
#
# Author:      A. Undrus (Original Perl), Gemini (Python Migration)
#-----------------------------------------------------------------------------
import os
import sys
import re
import argparse
from pathlib import Path
from html import escape
import shutil

def parse_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Test logfiles for errors and warnings.")
    parser.add_argument('-s', '--short', action='store_true', help='Short output format.')
    parser.add_argument('-e', '--specformat', action='store_true', help='Special format output.')
    parser.add_argument('-t', '--testtesting', action='store_true', help='Enable testtesting mode.')
    parser.add_argument('-q', '--qatesting', action='store_true', help='Enable qatesting mode.')
    parser.add_argument('-l', '--light', action='store_true', help='Enable light mode (limited error analysis).')
    parser.add_argument('posargs', nargs='*', help='Positional arguments.')
    return parser.parse_args()

def get_env_vars():
    """Reads required environment variables."""
    env = {
        'ARDOC_LOG': os.environ.get('ARDOC_LOG', ''),
        'ARDOC_TESTLOG': os.environ.get('ARDOC_TESTLOG', ''),
        'ARDOC_QALOG': os.environ.get('ARDOC_QALOG', ''),
        'ARDOC_HOME': os.environ.get('ARDOC_HOME', ''),
        'ARDOC_PROJECT_NAME': os.environ.get('ARDOC_PROJECT_NAME', ''),
        'ARDOC_PROJECT_RELNAME': os.environ.get('ARDOC_PROJECT_RELNAME', ''),
        'ARDOC_PROJECT_RELNAME_COPY': os.environ.get('ARDOC_PROJECT_RELNAME_COPY', ''),
        'ARDOC_WEBDIR': os.environ.get('ARDOC_WEBDIR', ''),
        'ARDOC_WEBPAGE': os.environ.get('ARDOC_WEBPAGE', ''),
        'ARDOC_VERSION': os.environ.get('ARDOC_VERSION', ''),
        'ARDOC_TEST_SUCCESS_PATTERN': os.environ.get('ARDOC_TEST_SUCCESS_PATTERN', ''),
        'ARDOC_TEST_FAILURE_PATTERN': os.environ.get('ARDOC_TEST_FAILURE_PATTERN', ''),
        'ARDOC_TEST_WARNING_PATTERN': os.environ.get('ARDOC_TEST_WARNING_PATTERN', ''),
        'ARDOC_BUILD_FAILURE_PATTERN': os.environ.get('ARDOC_BUILD_FAILURE_PATTERN', 'CVBFGG'),
        'ARDOC_QA_SUCCESS_PATTERN': os.environ.get('ARDOC_QA_SUCCESS_PATTERN', ''),
        'ARDOC_QA_FAILURE_PATTERN': os.environ.get('ARDOC_QA_FAILURE_PATTERN', ''),
        'ARDOC_QA_WARNING_PATTERN': os.environ.get('ARDOC_QA_WARNING_PATTERN', ''),
    }
    return env

def header_print(f, prblm, test_nm):
    """Writes the HTML header to the file."""
    comment = {0.5: "M", 1: "W", 2: "E"}.get(prblm, "")
    f.write(f'''<html>
<!-- {comment} -->
<style>
body {{
  color: black; link: navy; vlink: maroon; alink: tomato;
  background: floralwhite;
  font-family: 'Lucida Console', 'Courier New', Courier, monospace;
  font-size: 10pt;
}}
td.aid {{ background: #6600CC; color: orangered; text-align: center; }}
td.ttl {{ color: #6600CC; text-align: center; }}
a.small {{ color: navy; background: #FFCCFF; font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 10pt; }}
#prblm {{background-color: orange;}}
#hdr0 {{ font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 14pt; }}
#hdr {{ background-color: #FFCCFF; font-family:'Times New Roman',Garamond, Georgia, serif; font-size: 14pt; }}
#hdr1 {{ background-color: #CFECEC; font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 10pt; }}
</style>
<head><title>{test_nm} Logfile</title></head>
<BODY class=body marginwidth="0" marginheight="0" topmargin="0" leftmargin="0">
''')

def main():
    """Main execution logic."""
    args = parse_args()
    env = get_env_vars()

    # Determine mode and arguments
    if not args.testtesting and not args.qatesting:
        if len(args.posargs) != 4:
            print("ardoc_errortester: Four arguments required: directory_package, release, tags file, package name")
            sys.exit(2)
        compname, release, filename, pkgname_full = args.posargs
        log_dir = Path(os.path.dirname(env['ARDOC_LOG']))
    else:
        if len(args.posargs) != 2:
            print("ardoc_errortester: Two arguments required: name of test, release")
            sys.exit(2)
        compname, release = args.posargs
        filename, pkgname_full = "", ""
        log_dir = Path(os.path.dirname(env['ARDOC_QALOG' if args.qatesting else 'ARDOC_TESTLOG']))

    pkgname = Path(pkgname_full).name if pkgname_full else ""

    # --- Pattern Definitions ---
    # (A subset for brevity, can be extended to the full set from the Perl script)
    e_patterns = [": error:", "CMake Error", "runtime error:", "No rule to make target", env['ARDOC_BUILD_FAILURE_PATTERN']]
    e_ignore = ["CVBFGG"] * len(e_patterns)
    w_patterns = ["Errors/Problems found", "CMake Warning", "> Warning:"]
    w_ignore = ["Errors/Problems found : 0", "CVBFGG", "> Warning: template"]
    m_patterns = [": warning: ", "Warning: the last line"]
    m_ignore = ["make[", "CVBFGG"]
    s_patterns = ["Package build succeeded"]
    
    # Find the log file
    log_file_pattern = f"{compname}.loglog"
    log_files = sorted(log_dir.glob(log_file_pattern), key=os.path.getmtime, reverse=True)

    if not log_files:
        print(f"ardoc_errortester.py: No logfile found for {compname} in {log_dir}")
        sys.exit(0)
    
    log_file = log_files[0]
    html_file = log_file.with_suffix(".html")

    # Scan the log file
    errors, warnings, minors = [], [], []
    line_num = 0
    first_error, first_warning, first_minor = None, None, None

    with open(log_file, 'r', errors='ignore') as f:
        for i, line in enumerate(f, 1):
            line_num = i
            # Simplified scanning logic
            for pat, ign in zip(e_patterns, e_ignore):
                if pat != "CVBFGG" and re.search(pat, line) and not re.search(ign, line):
                    if not first_error: first_error = (i, line.strip(), pat)
                    errors.append(pat)
            for pat, ign in zip(w_patterns, w_ignore):
                if pat != "CVBFGG" and re.search(pat, line) and not re.search(ign, line):
                    if not first_warning: first_warning = (i, line.strip(), pat)
                    warnings.append(pat)
            for pat, ign in zip(m_patterns, m_ignore):
                if pat != "CVBFGG" and re.search(pat, line) and not re.search(ign, line):
                    if not first_minor: first_minor = (i, line.strip(), pat)
                    minors.append(pat)

    # Determine problem level and message
    problems = 0
    mess = "No problems found"
    linkline, linkvalue = 0, ""

    if errors:
        problems = 2
        mess = f"Error pattern found: {first_error[2]}"
        linkline, linkvalue = first_error[0], first_error[1]
    elif warnings:
        problems = 1
        mess = f"Serious warning pattern found: {first_warning[2]}"
        linkline, linkvalue = first_warning[0], first_warning[1]
    elif minors:
        problems = 0.5
        mess = f"Minor warning pattern found: {first_minor[2]}"
        linkline, linkvalue = first_minor[0], first_minor[1]

    # Generate HTML report
    with open(html_file, 'w', encoding='utf-8') as f_html:
        header_print(f_html, problems, compname)
        f_html.write(f'<div id=hdr1><b>{mess}</b><br>')
        f_html.write(f'<b>Original log file:</b><CODE> {escape(str(log_file))} </CODE><BR></div>\n<P><PRE>\n')
        
        with open(log_file, 'r', errors='ignore') as f_log:
            for i, line in enumerate(f_log, 1):
                safe_line = escape(line)
                if i == linkline:
                    f_html.write(f'<div id="prblm">{safe_line}</div>')
                else:
                    f_html.write(safe_line)
        f_html.write("  </PRE>\n  <div id=\"end\">END OF LOGFILE</div>\n  </body>\n  </html>\n")

    print(f"HTML report generated at: {html_file}")

    # Copy to web directory if specified
    if env['ARDOC_WEBDIR']:
        web_log_dir_name = f"ARDOC_Log_{env['ARDOC_PROJECT_RELNAME_COPY']}"
        if args.testtesting:
            web_log_dir_name = f"ARDOC_TestLog_{env['ARDOC_PROJECT_RELNAME_COPY']}"
        elif args.qatesting:
            web_log_dir_name = f"ARDOC_QALog_{env['ARDOC_PROJECT_RELNAME_COPY']}"
            
        dest_dir = Path(env['ARDOC_WEBDIR']) / web_log_dir_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(html_file, dest_dir / html_file.name)
        print(f"Copied report to {dest_dir / html_file.name}")

    # Exit with appropriate code
    if problems == 2:
        sys.exit(2)
    elif problems == 1:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
