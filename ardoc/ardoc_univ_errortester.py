#!/usr/bin/env python3

import os
import sys
import re
import html
from pathlib import Path

def header_print(file_handle, problem_level, test_name):
    """Generate HTML header for the log file."""
    comment = ""
    if problem_level == 0.5:
        comment = "M"
    elif problem_level == 1:
        comment = "W"
    elif problem_level == 2:
        comment = "E"
    
    header_html = f"""<html>
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
    file_handle.write(header_html)

def main():
    """
    Universal error tester for different types of log files.
    This is a Python migration of ardoc_univ_errortester.pl.
    """
    
    # Get environment variables
    ARDOC_HOME = os.environ.get("ARDOC_HOME", "")
    ARDOC_COPY_HOME = os.environ.get("ARDOC_COPY_HOME", "")
    ARDOC_WORK_AREA = os.environ.get("ARDOC_WORK_AREA", "")
    ARDOC_PROJECT_RELNAME_COPY = os.environ.get("ARDOC_PROJECT_RELNAME_COPY", "")
    ARDOC_LOGDIR = os.environ.get("ARDOC_LOGDIR", "")
    ARDOC_WEBDIR = os.environ.get("ARDOC_WEBDIR", "")
    ARDOC_WEBPAGE = os.environ.get("ARDOC_WEBPAGE", "")
    ARDOC_WEB_HOME = os.environ.get("ARDOC_WEB_HOME", "")
    ARDOC_LOG = os.environ.get("ARDOC_LOG", "")
    ARDOC_VERSION = os.environ.get("ARDOC_VERSION", "")
    
    if ARDOC_LOG:
        ARDOC_LOGDIR = str(Path(ARDOC_LOG).parent)
        ARDOC_LOGDIRBASE = Path(ARDOC_LOGDIR).name
    
    # Check arguments
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("ardoc_errortester:", file=sys.stderr)
        print("One or two arguments required: name of logfile and --conf or --inst option", file=sys.stderr)
        sys.exit(2)
    
    filename = ""
    option = "copy"
    
    # Parse arguments
    args = sys.argv[1:]
    while args:
        arg = args[0]
        if arg.startswith('--'):
            if arg == '--conf':
                option = "conf"
            elif arg == '--inst':
                option = "inst"
            elif arg in ['--checkout', '--co']:
                option = "checkout"
            args = args[1:]
        else:
            filename = arg
            args = args[1:]
    
    if not filename:
        print("Error: logfile name required", file=sys.stderr)
        sys.exit(2)
    
    # Define patterns based on option
    e_success = [" ", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"]
    e_warning = ["package not found", "CMake Warning", "CMake Deprecation Warning", "> Warning:", 
                 r"Warning:.*logfile.*not\s+available", "logfile not found", "CVBFGG"]
    e_warning_ignore = ["CVBFGG"] * 7
    e_warning_ignore_1 = ["CVBFGG"] * 7
    e_warning_ignore_2 = ["CVBFGG"] * 7
    e_warning_ignore_3 = ["CVBFGG"] * 7
    
    e_warning_patterns_minor = ["CVBFGG", r"Could.*NOT.*find", "Warning: the last line", 
                               "Warning: Unused class rule", r'Warning:\s.*rule', "CVBFGG", "CVBFGG"]
    
    e_patterns = ["can not", "permission denied", "Disk quota exceeded", "CMake Error", 
                  "not remade because of errors", "connection problem", "cmake: command not found"]
    e_ignore = ["ERRORS: 0", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"]
    e_ignore_2 = ["CVBFGG"] * 7
    e_ignore_3 = ["CVBFGG"] * 7
    e_patterns_correlators = [" "] * 7
    
    # Modify patterns for checkout option
    if option == "checkout":
        e_warning = ["package not found", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"]
        e_patterns = ["can not", "permission denied", "Disk quota exceeded", "Timeout after", 
                     "ERROR:", "pb occured", "connection problem"]
        e_ignore = ["ERRORS: 0", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"]
    
    # Initialize counters
    e_count = [0] * 7
    w_count = [0] * 7
    w_minor_count = [0] * 7
    s_count = [1, 0, 0, 0, 0, 0, 0]
    
    lineE = [0] * 7
    lineW = [0] * 7
    lineM = [0] * 7
    
    lineEValue = [""] * 7
    lineWValue = [""] * 7
    lineMValue = [""] * 7
    
    lineT = 0
    
    # Process the log file
    if Path(filename).is_file():
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.rstrip('\n')
                    lineT += 1
                    
                    # Check error patterns
                    for m, pattern in enumerate(e_patterns):
                        if (pattern and pattern != "CVBFGG" and pattern in line and
                            e_ignore[m] not in line and e_ignore_2[m] not in line and
                            e_ignore_3[m] not in line):
                            
                            correlator = e_patterns_correlators[m]
                            if not correlator or correlator == " ":
                                e_count[m] += 1
                                if lineE[m] == 0:
                                    lineE[m] = lineT
                                    lineEValue[m] = line
                            else:
                                if correlator in line:
                                    e_count[m] += 1
                                    if lineE[m] == 0:
                                        lineE[m] = lineT
                                        lineEValue[m] = line
                    
                    # Check warning patterns
                    for m, pattern in enumerate(e_warning):
                        if pattern and pattern != "CVBFGG":
                            if r'\.' in pattern:  # Regex pattern
                                if (re.search(pattern, line) and
                                    e_warning_ignore[m] not in line and
                                    e_warning_ignore_1[m] not in line and
                                    e_warning_ignore_2[m] not in line and
                                    e_warning_ignore_3[m] not in line):
                                    w_count[m] += 1
                                    if lineW[m] == 0:
                                        lineW[m] = lineT
                                        lineWValue[m] = line
                            else:  # Literal pattern
                                if (pattern in line and
                                    e_warning_ignore[m] not in line and
                                    e_warning_ignore_1[m] not in line and
                                    e_warning_ignore_2[m] not in line and
                                    e_warning_ignore_3[m] not in line):
                                    w_count[m] += 1
                                    if lineW[m] == 0:
                                        lineW[m] = lineT
                                        lineWValue[m] = line
                    
                    # Check minor warning patterns
                    for m, pattern in enumerate(e_warning_patterns_minor):
                        if pattern and pattern != "CVBFGG":
                            if r'\.' in pattern:  # Regex pattern
                                if re.search(pattern, line):
                                    w_minor_count[m] += 1
                                    if lineM[m] == 0:
                                        lineM[m] = lineT
                                        lineMValue[m] = line
                            else:  # Literal pattern
                                if pattern in line:
                                    w_minor_count[m] += 1
                                    if lineM[m] == 0:
                                        lineM[m] = lineT
                                        lineMValue[m] = line
                    
                    # Check success patterns
                    for m, pattern in enumerate(e_success):
                        if pattern in line and s_count[m] > -1:
                            s_count[m] -= 1
        
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # File not found
        eeee = f"logfile not found: {filename}"
        problems = 10
        print(f"G {eeee}")
        sys.exit(2)
    
    # Analyze results
    eeee = ""
    lineEE = 0
    lineEEValue = ""
    
    for m, pattern in enumerate(e_patterns):
        if e_count[m] > 0 and pattern != "CVBFGG":
            correlator = e_patterns_correlators[m]
            if not correlator or correlator == " ":
                eeee = pattern
                lineEE = lineE[m]
                lineEEValue = lineEValue[m]
            else:
                eeee = f"{pattern} AND {correlator}"
                lineEE = lineE[m]
                lineEEValue = lineEValue[m]
            break
    
    # Check for missing success patterns
    ssss = ""
    for m, count in enumerate(s_count):
        if count > 0:
            ssss = f"{e_success[m]}(ABSENSE OF)"
            break
    
    # Check warning patterns
    wwww = ""
    lineWW = 0
    lineWWValue = ""
    
    for m, pattern in enumerate(e_warning):
        if w_count[m] > 0 and pattern != "CVBFGG":
            wwww = pattern
            lineWW = lineW[m]
            lineWWValue = lineWValue[m]
            break
    
    # Check minor warning patterns
    wwww_minor = ""
    lineMM = 0
    lineMMValue = ""
    
    for m, pattern in enumerate(e_warning_patterns_minor):
        if w_minor_count[m] > 0 and pattern != "CVBFGG":
            wwww_minor = pattern
            lineMM = lineM[m]
            lineMMValue = lineMValue[m]
            break
    
    # Determine problem level and output
    mess = "No problems found"
    linkline = 0
    linkvalue = ""
    problems = 0
    
    if eeee:
        linkline = lineEE
        linkvalue = lineEEValue
        mess = f"Error pattern found: {eeee}"
        problems = 2
        print(f"G {eeee}")
    elif ssss:
        linkline = 0
        mess = f"Required success pattern not found: {ssss}"
        problems = 2
        print(f"G {mess}", end="")
    elif wwww:
        linkline = lineWW
        linkvalue = lineWWValue
        mess = f"Serious warning pattern found: {wwww}"
        problems = 1
        print(f"W {wwww}", end="")
    elif wwww_minor:
        linkline = lineMM
        linkvalue = lineMMValue
        mess = f"Minor warning pattern found: {wwww_minor}"
        problems = 0.5
        print(f"M {wwww_minor}", end="")
    
    # Generate HTML output
    filebase1 = Path(filename).name
    filedir = Path(filename).parent
    filebase = Path(filename).stem
    filehtml = filedir / f"{filebase}.html"
    
    # Create option description
    optn = option
    if optn == "down":
        optn = "kit installation"
    elif optn == "conf":
        optn = "cmake build configuration"
    elif optn == "inst":
        optn = "externals build"
    elif optn == "checkout":
        optn = "code checkout"
    
    aid_message_html = f"""<DIV id=hdr0>
<table bordercolor="#6600CC" border=10 cellpadding=5 cellspacing=0 width="100%">
<tr><td class=aid width=20% align=center valign=baseline>
<H1>ARDOC</H1>
</td>
<td class=ttl>
<EM><B><BIG>Converted {optn} logfile</BIG></EM></B>
</td></tr>
<tr><td class=aid>
version  {ARDOC_VERSION}
</td>
"""
    
    # Generate HTML based on problem level
    if problems == 2:
        mess2 = '&nbsp;<BR>&nbsp;&nbsp;&nbsp;&nbsp;<A href="#prblm">link to the problematic line</A><BR>'
        if linkline == 0:
            mess2 = ""
        
        aid_message_html1 = f"""<td class=ttl><EM><B>{mess}</B></EM>
</td>
</tr>
</table>
</DIV>
<DIV id=hdr>
<B>
    {mess2}
    &nbsp;&nbsp;&nbsp;&nbsp;<A href="#end">link to the last line</A> <BR>
    &nbsp;<BR>
</B></DIV>
"""
    
    elif problems == 1 or problems == 0.5:
        mess2 = '&nbsp;<BR>&nbsp;&nbsp;&nbsp;&nbsp;<A href="#prblm">link to the problematic line</A><BR>'
        if linkline == 0:
            mess2 = ""
        
        aid_message_html1 = f"""<td class=ttl><EM><B>{mess}</B></EM>
</td>
</tr>
</table>
</DIV>
<DIV id=hdr>
<B>
    {mess2}
&nbsp;&nbsp;&nbsp;&nbsp;<A href="#end">link to the last line</A> <BR>
    &nbsp;<BR>
</B></DIV>
"""
    
    elif problems == 10:
        mess = f'problem: "{eeee}"'
        aid_message_html1 = f"""<td class=ttl><EM><B>{mess}</B></EM>
</td>
</tr>
</table>
"""
    
    else:
        aid_message_html1 = """<td class=ttl><EM><B>No problems found</EM></B>
</td>
</tr>
</table>
<DIV id=hdr>
<B>
&nbsp;<BR>
&nbsp;&nbsp;&nbsp;&nbsp;<A href="#end">link to the last line</A> <BR>
&nbsp;<BR>
</B></DIV>
"""
    
    # Generate complete HTML file
    aid_message_html += aid_message_html1
    
    if filehtml:
        print(f"ardoc_univ_errortester.py: HTML: {filehtml}", file=sys.stderr)
        
        try:
            with open(filehtml, 'w', encoding='utf-8') as f:
                header_print(f, problems, option)
                f.write(aid_message_html)
                f.write('<div id=hdr1>\n')
                f.write(f'original log file: <CODE> {filename} </CODE><BR>\n')
                
                if ARDOC_WEBPAGE:
                    webloc = f"{ARDOC_WEBPAGE}/ARDOC_Log_{ARDOC_PROJECT_RELNAME_COPY}/{filebase1}"
                    f.write(f'<a href="{webloc}"><b>text logfile (full size)</b></a>\n')
                
                f.write('</div>\n <P>\n')
                
                # Write truncated log content
                total_ln = 5000
                first_part = 3000
                middle_part1 = 25
                middle_part2 = 25
                last_part = 2000
                
                # Determine line ranges to include
                allowed_ranges = []
                if lineT <= total_ln:
                    allowed_ranges.append((0, total_ln))
                else:
                    allowed_ranges.append((0, first_part))
                    allowed_ranges.append((lineT - last_part + 1, lineT))
                    if linkline > 0:
                        allowed_ranges.append((linkline - middle_part1, linkline + middle_part2))
                
                print(f"ardoc_univ_errortester.py: conversion info: {allowed_ranges}", file=sys.stderr)
                
                # Write log content
                ncount_line = 0
                ncount_s = 0
                
                with open(filename, 'r', encoding='utf-8', errors='ignore') as log_f:
                    for line in log_f:
                        ncount_line += 1
                        
                        # Check if this line should be included
                        line_ok = False
                        for start, end in allowed_ranges:
                            if start <= ncount_line <= end:
                                line_ok = True
                                break
                        
                        if not line_ok:
                            ncount_s = 0
                            continue
                        
                        if ncount_line != linkline:
                            ncount_s += 1
                            if ncount_s == 1 and ncount_line > 1:
                                f.write("""<DIV ID=hdr>................................................................<BR>
.....LINES TRUNCATED.....<BR>
................................................................
</DIV>
""")
                            escaped_line = html.escape(line.rstrip())
                            f.write(f"{escaped_line} <BR>\n")
                        else:
                            escaped_line = html.escape(line.rstrip())
                            f.write(f'<div id="prblm">{escaped_line}</div>\n')
                            ncount_s += 1
                        
                        if ncount_line == lineT:
                            f.write('<div id="end">END OF LOGFILE</div>\n')
                
                f.write("""
  </body>
  </html>
  """)
        
        except Exception as e:
            print(f"Error generating HTML: {e}", file=sys.stderr)
        
        # Copy HTML to web directory for certain options
        if option in ["kit", "down", "rpm", "pacball"]:
            if ARDOC_WEBDIR and ARDOC_PROJECT_RELNAME_COPY:
                filehtml_base = filehtml.name
                copy_html = f"{ARDOC_WEBDIR}/ARDOC_Log_{ARDOC_PROJECT_RELNAME_COPY}/{filehtml_base}"
                os.system(f"cp -Rp {filehtml} {copy_html}")

if __name__ == "__main__":
    main()
