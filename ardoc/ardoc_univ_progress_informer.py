#!/usr/bin/env python3
"""
ARDOC - Nightly Control System
Author: Alex Undrus <undrus@bnl.gov>

----------------------------------------------------------
ardoc_univ_progress_informer.py
----------------------------------------------------------

Python migration of ardoc_univ_progress_informer
Universal progress informer with database updates and web status generation
"""

import os
import sys
import subprocess
import time
import argparse
from pathlib import Path


def main():
    # Environment variables
    ARDOC_HOME = os.environ.get('ARDOC_HOME', '')
    ARDOC_WEBDIR = os.environ.get('ARDOC_WEBDIR', '')
    ARDOC_COMMON_WEBDIR = os.environ.get('ARDOC_COMMON_WEBDIR', '')
    ARDOC_WEBDIR_MAIN = os.environ.get('ARDOC_WEBDIR_MAIN', '')
    ARDOC_PROJECT_HOME = os.environ.get('ARDOC_PROJECT_HOME', '')
    ARDOC_PROJECT_NAME = os.environ.get('ARDOC_PROJECT_NAME', '')
    ARDOC_PROJECT_RELNAME = os.environ.get('ARDOC_PROJECT_RELNAME', '')
    ARDOC_PROJECT_RELNAME_COPY = os.environ.get('ARDOC_PROJECT_RELNAME_COPY', '')
    ARDOC_CONFBUILDLOG = os.environ.get('ARDOC_CONFBUILDLOG', '')
    ARDOC_INSTBUILDLOG = os.environ.get('ARDOC_INSTBUILDLOG', '')
    ARDOC_CHECKOUTLOG = os.environ.get('ARDOC_CHECKOUTLOG', '')
    ARDOC_LOG = os.environ.get('ARDOC_LOG', '')
    ARDOC_WORK_AREA = os.environ.get('ARDOC_WORK_AREA', '')
    ARDOC_WEBPAGE = os.environ.get('ARDOC_WEBPAGE', '')
    CI_RESULTS_DICT = os.environ.get('CI_RESULTS_DICT', '')
    gitlabMergeRequestId = os.environ.get('gitlabMergeRequestId', '99999')
    
    # Default values
    phase = 1
    step = ""
    error = ""
    ciresults_dir = ""
    
    if CI_RESULTS_DICT:
        ciresults_dir = os.path.dirname(CI_RESULTS_DICT)
        if not os.path.exists(ciresults_dir):
            os.makedirs(ciresults_dir, exist_ok=True)
    
    if not gitlabMergeRequestId:
        gitlabMergeRequestId = "99999"
    
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--step', type=str, help='Step to process (conf, inst, checkout)')
    parser.add_argument('--check', type=str, help='Error status')
    parser.add_argument('--phase', type=int, default=1, help='Phase number')
    
    args = parser.parse_args()
    
    if args.step:
        step = args.step
    if args.check:
        error = args.check
    if args.phase:
        phase = args.phase
    
    # Handle step aliases
    if step == "co":
        step = "checkout"
    
    if step not in ["conf", "inst", "checkout"]:
        print(f"ardoc_univ_progress_informer: Error: step is {step}, must be \"conf\", \"inst\", or \"checkout\"")
        return 1
    
    # Determine base log file
    base_log = "undefined"
    if step == "conf":
        base_log = os.path.basename(ARDOC_CONFBUILDLOG) if ARDOC_CONFBUILDLOG else "undefined"
    elif step == "inst":
        base_log = os.path.basename(ARDOC_INSTBUILDLOG) if ARDOC_INSTBUILDLOG else "undefined"
    elif step == "checkout":
        base_log = os.path.basename(ARDOC_CHECKOUTLOG) if ARDOC_CHECKOUTLOG else "undefined"
    
    # Create HTML base name
    base_html = base_log
    if '.' in base_html:
        filebase_parts = base_html.split('.')
        if len(filebase_parts) > 1:
            filebase_parts.pop()
            base_html = '.'.join(filebase_parts) + ".html"
    
    WLogdir = f"ARDOC_Log_{ARDOC_PROJECT_RELNAME_COPY}"
    
    # Set option names
    if step in ["conf", "inst"]:
        option = step + "build"
        OPTION = step.upper() + "BUILD"
    else:
        option = step.lower()
        OPTION = step.upper()
    
    # Remove logfiles at initialization (phase 0)
    if phase == 0:
        log_var = f"ARDOC_{OPTION}_LOG"
        log_file = os.environ.get(log_var, '')
        if log_file and os.path.exists(log_file):
            os.unlink(log_file)
    
    # Process error codes
    error_statement = ""
    db_code = 0
    error_orig = error
    error_orig_parts = error_orig.split(' ')
    error_orig_1 = error_orig_parts[0] if error_orig_parts else ""
    
    if error_orig_1 == "G":
        error_orig = error_orig.replace("G ", "", 1)
        db_code = 1
    elif error_orig_1 == "W":
        error_orig = error_orig.replace("W ", "", 1)
        db_code = 2
    elif error_orig_1 == "M":
        error_orig = error_orig.replace("M ", "", 1)
        db_code = 4
    
    error = error.replace(" ", "")
    image = '<IMG SRC="tick.gif" HEIGHT=15 WIDTH=15>'
    
    if error and error != "0":
        error_statement = "error"
        image = '<IMG SRC="cross_red.gif" HEIGHT=16 WIDTH=20>'
        if error_orig_1 == "W":
            error_statement = "warning"
            image = '<IMG src=rad18x16.gif width=18 height=16>'
        elif error_orig_1 == "M":
            error_statement = "warning"
            image = '<IMG src=yl_ball.gif width=20 height=20>'
    
    # Progress file handling
    progress_file = f"{ARDOC_WORK_AREA}/ardoc_{option}_progress_status"
    if phase == 0 and os.path.exists(progress_file):
        os.unlink(progress_file)
    
    # Read existing progress file
    prfl = []
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            prfl = [line.strip() for line in f.readlines()]
    
    # Get current time
    current_time = time.localtime()
    month = current_time.tm_mon
    tstr = f"{month}/{current_time.tm_mday} {current_time.tm_hour}:{current_time.tm_min:02d}"
    
    print(f"ardoc_univ_progress_informer: filling {progress_file}, phase {phase}")
    
    # Write progress file
    with open(progress_file, 'w') as f:
        f.write(f"{phase}\n")
        
        if phase == 0:
            f.write('<IMG SRC=pur_sq.gif HEIGHT=12 WIDTH=12>\n')
            f.write('N/A\n')
        elif phase == 1:
            basebase = f"base_{option}.html"
            f.write(f'<a href="{ARDOC_WEBPAGE}/ARDOC_Log_{ARDOC_PROJECT_RELNAME_COPY}/{basebase}">{image}</a>\n')
            f.write(f"{tstr}\n")
            
            # Copy files to web directory
            copytarget = f"{ARDOC_WEBDIR}/{WLogdir}"
            if not os.path.exists(copytarget):
                os.makedirs(copytarget, exist_ok=True)
            
            # Get the appropriate log file
            log_var = f"ARDOC_{OPTION}_LOG"
            log_file = os.environ.get(log_var, '')
            
            if log_file and os.path.exists(log_file):
                subprocess.run(['cp', '-pf', log_file, f"{copytarget}/."], check=False)
                
                # Create HTML version
                filebase1 = os.path.basename(log_file)
                filedir = os.path.dirname(log_file)
                filebase = filebase1
                
                if '.' in filebase:
                    filebase_parts = filebase.split('.')
                    if len(filebase_parts) > 1:
                        filebase_parts.pop()
                        filebase = '.'.join(filebase_parts)
                        filehtml = f"{filedir}/{filebase}.html"
                        
                        if os.path.exists(filehtml):
                            subprocess.run(['cp', '-pf', filehtml, f"{copytarget}/."], check=False)
            
            # Database operations
            if step == "conf":
                genlogdir = os.path.dirname(ARDOC_LOG) if ARDOC_LOG else ""
                if genlogdir:
                    cmd = f'genlogdir="{genlogdir}";{ARDOC_HOME}/ardoc_db_access -e -s "CB" -c {db_code} >> $genlogdir/ardoc_confbuild.logora'
                    subprocess.run(['bash', '-c', cmd], check=False)
                
                if ciresults_dir:
                    filecmkproblems = f"{ciresults_dir}/cmkproblems{ARDOC_PROJECT_NAME}_{gitlabMergeRequestId}"
                    print(f"ardoc_univ_progress_informer: writing cmake conf status {db_code} to {filecmkproblems}")
                    with open(filecmkproblems, 'w') as cmk_f:
                        cmk_f.write(f"{db_code}\n")
            
            elif step == "inst":
                genlogdir = os.path.dirname(ARDOC_LOG) if ARDOC_LOG else ""
                if genlogdir:
                    cmd = f'genlogdir="{genlogdir}";{ARDOC_HOME}/ardoc_db_access -e -s "IB" -c {db_code} >> $genlogdir/ardoc_instbuild.logora'
                    subprocess.run(['bash', '-c', cmd], check=False)
                
                if ciresults_dir:
                    fileinstproblems = f"{ciresults_dir}/instproblems{ARDOC_PROJECT_NAME}_{gitlabMergeRequestId}"
                    print(f"ardoc_univ_progress_informer: writing inst status {db_code} to {fileinstproblems}")
                    with open(fileinstproblems, 'w') as inst_f:
                        inst_f.write(f"{db_code}\n")
            
            elif step == "checkout":
                genlogdir = os.path.dirname(ARDOC_LOG) if ARDOC_LOG else ""
                if genlogdir:
                    cmd = f'genlogdir="{genlogdir}";{ARDOC_HOME}/ardoc_db_access -e -s "CO" -c {db_code} >> $genlogdir/ardoc_checkout.logora'
                    subprocess.run(['bash', '-c', cmd], check=False)
        else:
            f.write("'UNAVAILABLE'}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
