#!/usr/bin/env python3
import os
import sys
import re
from pathlib import Path
import argparse

def get_relnum_suffix(rel_name):
    if not rel_name:
        return ""
    arr = rel_name.split('_')
    if len(arr) <= 1:
        return ""
    relnum = arr[-1]
    if relnum == "RELEASE":
        return ""
    return f"_{relnum}"

def print_header(order, proj_name, rel_name, rel_loc, dir_name):
    ARDOC_WEBDIR = os.environ.get("ARDOC_WEBDIR", "")
    ARDOC_WEBPAGE = os.environ.get("ARDOC_WEBPAGE", "")
    ARDOC_PROJECT_NAME = os.environ.get("ARDOC_PROJECT_NAME", "")
    ARDOC_BUILD_FROM_SCRATCH = os.environ.get("ARDOC_BUILD_FROM_SCRATCH", "")
    ARDOC_HOSTNAME = os.environ.get("ARDOC_HOSTNAME", "")
    ARDOC_TITLE_COMMENT = os.environ.get("ARDOC_TITLE_COMMENT", "")
    ARDOC_INC_BUILD = os.environ.get("ARDOC_INC_BUILD", "")
    ARDOC_COMMON_WEBPAGE = os.environ.get("ARDOC_COMMON_WEBPAGE", "")

    arr = rel_name.split('_')
    relnum = arr[-1] if len(arr) > 1 else ""
    relbase = "_".join(arr[:-1]) if len(arr) > 1 else arr[0]
    relnum_suffix = get_relnum_suffix(rel_name)

    cont_word = "test" if order == 22 else "build"
    item_word = "tests" if order == 22 else "packages"

    wwwlis = []
    if ARDOC_WEBDIR and Path(ARDOC_WEBDIR).is_dir():
        pattern = re.compile(f"^ardoc_{cont_word}summary_\\d*\\.html$")
        wwwli = sorted([f for f in os.listdir(ARDOC_WEBDIR) if pattern.match(f)])
        for f in wwwli:
            relnum1 = f.split('_')[-1]
            relnum2 = relnum1.split('.')[0]
            if relnum2 != relnum:
                nnnn = f'<a href="{ARDOC_WEBPAGE}/{f}">{relbase}_{relnum2}</a>'
                wwwlis.append(nnnn)

    other_releases = " ".join(wwwlis)

    build_type_info = f"Release: {rel_name} &nbsp; -- &nbsp; Built from scratch on: {ARDOC_HOSTNAME}" if ARDOC_BUILD_FROM_SCRATCH == "yes" else f"Release: {rel_name} &nbsp; -- &nbsp; Built on: {ARDOC_HOSTNAME}"
    location_info = f"Work area for incrementals: {rel_loc}" if ARDOC_INC_BUILD == "yes" else f"Location: {rel_loc}"
    title_comment_html = f"{ARDOC_TITLE_COMMENT} <br>" if ARDOC_TITLE_COMMENT else ""

    m_image = ""
    filem = Path(ARDOC_WEBDIR) / f"status_email{relnum_suffix}"
    if filem.is_file():
        if filem.read_text().strip() == "1":
            m_image = 'E-MAILS SENT &nbsp; <IMG align=center SRC="post-worldletter.gif" HEIGHT=17 WIDTH=17>,'

    tm_image = ""
    filetm = Path(ARDOC_WEBDIR) / f"status_test_email{relnum_suffix}"
    if filetm.is_file():
        if filetm.read_text().strip() == "1":
            tm_image = '(E-MAILS SENT &nbsp; <IMG align=center SRC="post-worldletter.gif" HEIGHT=17 WIDTH=17>)'
    
    close_button_html = ""
    if cont_word == "test":
        close_button_html = """
        <tr><td colspan="2" bgcolor="#CCCFFF" align=right>
        <form>
        <input type=button value="Close Window" onClick="window.close();" style="background: red; font-weight:bold">
        </form>
        </td></tr>
        """

    testing_comment_html = ""
    ARDOC_COMMENT_TESTING_FILE = Path(ARDOC_WEBDIR) / "ardoc_comment_testing"
    if ARDOC_COMMENT_TESTING_FILE.is_file():
        comment_content = ARDOC_COMMENT_TESTING_FILE.read_text().strip()
        testing_comment_html = f"""
        <tr bgcolor="99CCCC">
        <th colspan=8 align=center>{comment_content}</th>
        </tr>
        """
    
    test_details_link = f"details</a> or <a href=\"{ARDOC_COMMON_WEBPAGE}/ATNSummary.html\" target=\"cumulative test list\">cumulative results" if cont_word != "test" else "details"


    html = f"""
<html>
<head>
<title>ardoc webpage with {cont_word} results</title>
<style>
table.header {{ background: #99CCFF; color: #CC0000; }}
body {{ color: black; background: cornsilk; font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 10pt; }}
a:link{{color: navy}} a:hover{{color: green}} a:visited{{color: mediumblue}} a:active{{color:chartreuse}}
#cellrose {{ background-color: #FFCCCC; }}
#cellsalad {{ background-color: #00FF33; }}
#cellsilk {{ background-color: cornsilk; }}
</style>
<SCRIPT SRC="status_test_pass{relnum_suffix}.js" language="JavaScript"></SCRIPT>
<SCRIPT SRC="status_test_fail{relnum_suffix}.js" language="JavaScript"></SCRIPT>
<SCRIPT SRC="status_unit_pass{relnum_suffix}.js" language="JavaScript"></SCRIPT>
<SCRIPT SRC="status_unit_fail{relnum_suffix}.js" language="JavaScript"></SCRIPT>
<SCRIPT SRC="test_completed{relnum_suffix}.js" language="JavaScript"></SCRIPT>
<SCRIPT SRC="test_total{relnum_suffix}.js" language="JavaScript"></SCRIPT>
</head>
<BODY class=body>
<table class=header border=0 cellpadding=5 cellspacing=0 width="100%">
{close_button_html}
<tr><td colspan="2" bgcolor="#CCCFFF" align=center>
<br><EM><B><BIG>ARDOC (NIghtly COntrol System) {cont_word} results<br><br></EM></B></BIG></td>
<tr><td colspan="2" align=center>
<br><BIG><B>Project: {ARDOC_PROJECT_NAME}<br>
{build_type_info}
<br></BIG><font size="-1">
other releases available: {other_releases} <br>
{title_comment_html}
{location_info} <br>
Highlighted {item_word} have problems, {m_image}
click on names to see <a href="{dir_name}">logfiles</a></font></B><br>
</td></tr>
<tr><td colspan="2" align=right><font size="-1"> &nbsp; </font></td></tr>
<tr class=light>
<td bgcolor="#CCCFFF" align=left><font size="-1">
<a href="{ARDOC_WEBPAGE}/ardoc_content{relnum_suffix}.html">list of tags</a>
</td>
<td bgcolor="#CCCFFF" align=right colspan=1><font size="-1">
<script language="JavaScript">
    document.write("Last modified "+ document.lastModified)
</script>
</font></td></tr></table><BR>
<table border=0 cellpadding=5 cellspacing=0 align=center width="90%">
<tbody>
<tr bgcolor="99CCCC"><TH colspan=8 align=center >
ATN Integration+Unit tests results
(click for <a href="ardoc_testsummary{relnum_suffix}.html">{test_details_link}</a>)
</th>
</tr>
<tr bgcolor="99CCCC">
<th align=center>number of tests:</th><th ID=cellsilk><SCRIPT>document.write(t_total{relnum_suffix}())</SCRIPT></th>
<th align=center>completed:</th><th ID=cellsilk><SCRIPT>document.write(t_completed{relnum_suffix}())</SCRIPT></th>
<th align=center>passed:</th><th ID=cellsalad><SCRIPT>document.write(status_tp{relnum_suffix}())</SCRIPT>+<SCRIPT>document.write(status_up{relnum_suffix}())</SCRIPT></th>
<th align=center>failed {tm_image} :</th><th ID=cellrose><SCRIPT>document.write(status_tf{relnum_suffix}())</SCRIPT>+<SCRIPT>document.write(status_uf{relnum_suffix}())</SCRIPT></th>
</tr>
{testing_comment_html}
</tbody>
</table>
<BR><BR>
<table border=0 cellpadding=5 cellspacing=0 align=center width="90%">
<tbody>
    """
    print(html)
    if cont_word == "test":
        cols = "<td><B>Package with Int. Test</B></td><td><B>Test File#Name</B></td><td><B>Test Suite</B></td><td><B>Result, E.Code</B></td>"
        if os.environ.get("ARDOC_WEB_HOME"):
            cols += "<td><B>Work Dir.</B></td>"
        cols += "<td><B>Manager(s)</B></td>"
        print(f"<tr>{cols}</tr>")

def print_interim_test_header():
    cols = "<td><B>Package with Unit Test</B></td><td><B>Test File#Name</B></td><td><B>Test Suite</B></td><td><B>Result, E.Code</B></td>"
    if os.environ.get("ARDOC_WEB_HOME"):
        cols += "<td><B>Work Dir</B></td>"
    cols += "<td><B>Manager(s)</B></td>"
    print(f"""
    <tr><td bgcolor="#99CCCC" colspan="{cols.count('<td>')}">&nbsp;</td></tr>
    <tr>{cols}</tr>
    """)

def print_interim(order, rel_name, dir_name):
    relnum_suffix = get_relnum_suffix(rel_name)
    
    order_links = {
        0: ('<th bgcolor="99CCCC">packages names, failures in b/order first</th>',
            f'<th bgcolor="CCCCFF"><A href="ardoc_buildsummary1{relnum_suffix}.html">build order</A></th>',
            f'<th bgcolor="CCCCFF"><A href="ardoc_buildsummary2{relnum_suffix}.html">containers names</A></th>'),
        1: (f'<th bgcolor="CCCCFF"><A href="ardoc_buildsummary{relnum_suffix}.html">packages names, failures in b/order first</A></th>',
            '<th bgcolor="99CCCC">build order</th>',
            f'<th bgcolor="CCCCFF"><A href="ardoc_buildsummary2{relnum_suffix}.html">containers names</A></th>'),
        2: (f'<th bgcolor="CCCCFF"><A href="ardoc_buildsummary{relnum_suffix}.html">packages names, failures in b/order first</A></th>',
            f'<th bgcolor="CCCCFF"><A href="ardoc_buildsummary1{relnum_suffix}.html">build order</A></th>',
            '<th bgcolor="99CCCC">containers names</th>')
    }
    links = "".join(order_links.get(order, order_links[0]))

    ARDOC_TITLE_TESTS = os.environ.get("ARDOC_TITLE_TESTS", "Test")
    ARDOC_TITLE_QA = os.environ.get("ARDOC_TITLE_QA", "QA Test")

    html = f"""
</table><BR>
<table border=0 cellpadding=5 cellspacing=0 align=center width="90%">
<tbody>
<tr bgcolor="99CCCC"><th colspan=3 align=center>Build results for individual packages. Sorted by:</th></tr>
<tr>{links}</tr>
</table>
<BR>
<table class=header border=10 cellpadding=5 cellspacing=0 align=center>
</table>
<table cellspacing=10%>
<TR><TD><B>Package Name</B></TD> <TD><B>Container</B></TD> <TD><B>Build</B></TD> 
<TD><B>{ARDOC_TITLE_QA}</B></TD> <TD><B>{ARDOC_TITLE_TESTS}</B></TD> <TD><B>Manager(s)</B></TD></TR>
    """
    print(html)

def print_final():
    print("</table>\n</body>\n</html>")

def print_package_row(package_name, container_name, dir_log, rec_log, prob, qrec_log, qprob, trec_log, tprob, a_names):
    prob, qprob, tprob = float(prob), float(qprob), float(tprob)
    
    hilight = ""
    if prob >= 2: hilight = 'bgcolor="#F5623D"'
    elif prob == 1: hilight = 'bgcolor="#F0A675"'
    elif prob == 0.5: hilight = 'bgcolor="#FFCA59"'
    elif tprob >= 2: hilight = 'bgcolor="#E87DA8"'
    elif tprob == 1: hilight = 'bgcolor="#FA9EB0"'
    elif tprob == 0.5: hilight = 'bgcolor="#FFE0E0"'
    elif qprob >= 2: hilight = 'bgcolor="#BA55D3"'
    elif qprob == 1: hilight = 'bgcolor="#CC9EFA"'
    elif qprob == 0.5: hilight = 'bgcolor="#EOE1EB"'

    image = '<IMG SRC="tick.gif" HEIGHT=15 WIDTH=15>'
    if prob >= 2: image = '<IMG SRC="cross_red.gif" HEIGHT=16 WIDTH=20>'
    elif prob == 1: image = '<IMG src=rad18x16.gif width=18 height=16>'
    elif prob == 0.5: image = '<IMG src=yl_ball.gif width=20 height=20>'

    def get_status_link(prob, rec_log, dir_log, status_map):
        if rec_log in ("0", "N/A"): return "N/A"
        status = status_map.get(prob, "PASS")
        return f'<a href="{dir_log}/{rec_log}">{status}</a>'

    qa_status = get_status_link(qprob, qrec_log, dir_log, {2: "FAIL", 1: "WARN", 0.5: "NOTE"})
    test_status = get_status_link(tprob, trec_log, dir_log, {2: "FAIL", 1: "WARN", 0.5: "NOTE"})
    
    managers = "N/A" if not a_names else " ".join(a_names).replace('@', '&nbsp;at&nbsp;')

    print(f'<tr {hilight}>'
          f'<td><a href="{dir_log}/{rec_log}">{package_name}</a></td>'
          f'<td>{container_name}</td>'
          f'<td>{image}</td>'
          f'<td>{qa_status}</td>'
          f'<td>{test_status}</td>'
          f'<td>{managers}</td></tr>')

def print_test_row(test_dir, test_name_full, test_name, test_suite, dir_log, rec_log, prob, tecode, a_names):
    prob = float(prob)
    hilight = ""
    if prob >= 2: hilight = 'bgcolor="#E87DA8"'
    elif prob == 1: hilight = 'bgcolor="#FA9EB0"'
    elif prob == 0.5: hilight = 'bgcolor="#FFE0E0"'

    image = '<IMG SRC="tick.gif" HEIGHT=15 WIDTH=15>'
    if prob >= 2: image = '<IMG SRC="cross_red.gif" HEIGHT=16 WIDTH=20>'
    elif prob == 1: image = '<IMG src=rad18x16.gif width=18 height=16>'
    elif prob == 0.5: image = '<IMG src=yl_ball.gif width=20 height=20>'

    managers = "N/A" if not a_names else " ".join(a_names).replace('@', '&nbsp;at&nbsp;')
    
    work_dir_link = ""
    if os.environ.get("ARDOC_WEB_HOME"):
        work_dir = ""
        test_name_low = test_name.lower()
        test_suite_low = test_suite.lower()
        if os.environ.get("ATN_WORKDIR") == "new":
            work_dir = f"{test_suite_low}_work/{test_name_low}_work"
        elif test_name_low.startswith("trig") or not test_suite_low:
            work_dir = f"{test_name_low}_work"
        else:
            work_dir = f"{test_name_low}_{test_suite_low}_work"
        
        work_dir_link = f'<td><a href="{os.environ["ARDOC_WEB_HOME"]}/{os.environ["ARDOC_PROJECT_RELNAME"]}/{os.environ["ARDOC_INTTESTS_DIR"]}/{work_dir}">link</a></td>'

    print(f'<tr {hilight}>'
          f'<td>{test_dir}</td>'
          f'<td><a href="{dir_log}/{rec_log}">{test_name_full}</a></td>'
          f'<td>{test_suite}</td>'
          f'<td>{image} {tecode}</td>'
          f'{work_dir_link}'
          f'<td>{managers}</td></tr>')


def main():
    parser = argparse.ArgumentParser(description="ARDOC Webpage Generator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-h', '--header', nargs=5, metavar=('ORDER', 'PROJ_NAME', 'REL_NAME', 'REL_LOC', 'DIR_NAME'))
    group.add_argument('-i', '--interim', nargs=3, metavar=('ORDER', 'REL_NAME', 'DIR_NAME'))
    group.add_argument('-u', '--interim_test', action='store_true')
    group.add_argument('-f', '--final', action='store_true')
    group.add_argument('-g', '--package_row', nargs='+', metavar='ARG')
    group.add_argument('-a', '--test_row', nargs='+', metavar='ARG')

    args = parser.parse_args()

    if args.header:
        print_header(int(args.header[0]), args.header[1], args.header[2], args.header[3], args.header[4])
    elif args.interim:
        print_interim(int(args.interim[0]), args.interim[1], args.interim[2])
    elif args.interim_test:
        print_interim_test_header()
    elif args.final:
        print_final()
    elif args.package_row:
        g_args = args.package_row
        print_package_row(g_args[0], g_args[1], g_args[2], g_args[3], g_args[4], g_args[6], g_args[7], g_args[9], g_args[10], g_args[12:])
    elif args.test_row:
        a_args = args.test_row
        print_test_row(a_args[0], a_args[1], a_args[2], a_args[3], a_args[4], a_args[5], a_args[6], a_args[7], a_args[8:])

if __name__ == "__main__":
    main()
