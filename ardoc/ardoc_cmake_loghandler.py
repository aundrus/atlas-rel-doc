#!/usr/bin/env python3
"""
ARDOC - ARtifact DOcumentation Control System
Author: Alex Undrus <undrus@bnl.gov>

----------------------------------------------------------
ardoc_cmake_loghandler.py
----------------------------------------------------------

Python migration of ardoc_cmake_loghandler.pl
Processes CMake build logs and generates individual package log files
"""

import os
import sys
import argparse
import time
from pathlib import Path


def compar(strg):
    """Compare function to get package name length"""
    lin1 = strg.replace(' ', '')
    if len(lin1) != 0:
        # Remove trailing leading stretches whitespaces
        lll = ' '.join(strg.split())
        fields = lll.split()
        package1 = fields[0] if fields else ""
        return len(package1)
    else:
        return 0


def compar9(filepath):
    """Get modification time of file"""
    try:
        mtm = os.path.getmtime(filepath)
        return mtm
    except OSError:
        return 0


def maxstring(lst):
    """Find longest string in list"""
    lengthmax = 0
    pick = 0
    for i, item in enumerate(lst):
        if len(item) > lengthmax:
            lengthmax = len(item)
            pick = i
    return pick


def main():
    prevdir = os.getcwd()
    file_suffix = ""
    infile = ""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file-suffix', type=str, default="", help='File suffix')
    parser.add_argument('-l', '--logfile', type=str, default="", help='Input log file')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode')
    parser.add_argument('-u', '--update', action='store_true', help='Update mode')
    
    args = parser.parse_args()
    
    if args.file_suffix:
        file_suffix = args.file_suffix
    if args.logfile:
        infile = args.logfile
    
    # Environment variables
    ARDOC_WORK_AREA = os.environ.get('ARDOC_WORK_AREA', '')
    ARDOC_PROJECT_NAME = os.environ.get('ARDOC_PROJECT_NAME', '')
    ARDOC_BUILDLOG = os.environ.get('ARDOC_BUILDLOG', '')
    ARDOC_DBFILE = os.environ.get('ARDOC_DBFILE', '')
    ARDOC_DBFILE_GEN = os.environ.get('ARDOC_DBFILE_GEN', '')
    ARDOC_HOSTNAME = os.environ.get('ARDOC_HOSTNAME', '')
    ARDOC_RELHOME = os.environ.get('ARDOC_RELHOME', '')
    ARDOC_DOCHOME = os.environ.get('ARDOC_DOCHOME', '')
    ARDOC_ARCH = os.environ.get('ARDOC_ARCH', '')
    ARDOC_LOG = os.environ.get('ARDOC_LOG', '')
    ARDOC_LOGDIR = os.path.dirname(ARDOC_LOG) if ARDOC_LOG else ""
    
    MAKELOG = ARDOC_BUILDLOG
    if infile:
        MAKELOG = infile
    
    LOGDIR = os.path.dirname(MAKELOG) if MAKELOG else ""
    LOGHANDLER_REPORT = f"{ARDOC_WORK_AREA}/ardoc_loghandler_report"
    file_unassigned_lines = f"{LOGDIR}/REMNANTS.log{file_suffix}"
    
    # Clean up remnants file
    if os.path.exists(file_unassigned_lines):
        os.remove(file_unassigned_lines)
    Path(file_unassigned_lines).touch()
    
    cntr = 0
    cntr_abs = 0
    stat = 0
    dbfile = os.path.basename(ARDOC_DBFILE_GEN) if ARDOC_DBFILE_GEN else ""
    dbfilegen = f"{ARDOC_WORK_AREA}/{dbfile}_res"
    separator = ""
    pkg = ""
    went_to_file = 0
    
    # Read and process database file
    try:
        with open(dbfilegen, 'r') as f:
            dbc1 = [line.strip() for line in f.readlines()]
    except IOError:
        print(f"Error: Cannot open {dbfilegen}")
        return 1
    
    # Sort by package name length
    dbc2 = sorted(dbc1, key=compar)
    dbc = list(reversed(dbc2))
    
    # Clear intermediate lists
    dbc1 = []
    dbc2 = []
    
    # Process each package
    for entry in dbc:
        # Ignore comments
        if entry.startswith('#'):
            continue
            
        # Remove trailing leading stretches whitespaces
        lll = ' '.join(entry.split())
        fields = lll.split()
        if not fields:
            continue
            
        pkg = fields[0]
        pkg_base = os.path.basename(pkg)
        
        print(f"ardoc_cmake_loghandler.py: package: {pkg}, base {pkg_base}", file=sys.stderr)
        
        # Determine log directory
        dirlog = f"{ARDOC_RELHOME}/build.{ARDOC_ARCH}/BuildLogs"
        if not os.path.isdir(dirlog) and os.path.isdir(f"{ARDOC_RELHOME}/BuildLogs"):
            dirlog = f"{ARDOC_RELHOME}/BuildLogs"
            
        print(f"ardoc_cmake_loghandler.py: dirlog: {dirlog}", file=sys.stderr)
        
        # Find log files
        listlog = []
        if os.path.isdir(dirlog):
            try:
                for filename in os.listdir(dirlog):
                    if filename == f"{pkg_base}.log":
                        listlog.append(filename)
            except OSError:
                pass
                
        print(f"ardoc_cmake_loghandler.py: logs: {listlog}", file=sys.stderr)
        
        # Read version file
        file_vers = f"{ARDOC_RELHOME}/{pkg}/version.cmake"
        print(f"ardoc_cmake_loghandler.py: version file: {file_vers}", file=sys.stderr)
        
        linev = "N/A"
        if os.path.exists(file_vers):
            try:
                with open(file_vers, 'r') as f:
                    linev = f.readline().strip()
            except IOError:
                pass
        
        # Create output filename
        pkgn = pkg.replace('/', '_')
        if not pkgn:
            pkgn = pkg
        output_file = f"{ARDOC_LOGDIR}/{pkgn}.loglog"
        
        # Process log files
        if not listlog:
            # No log files found
            with open(output_file, 'w') as f:
                f.write("=" * 75 + "\n")
                f.write(f"[ATLAS Nightly System]: no build logfiles for {pkg_base} are found in build.{ARDOC_ARCH}/BuildLogs\n")
                f.write("=" * 75 + "\n")
                f.write("[ATLAS Nightly System]: absence of build logfile alone is not a problem sign\n")
                f.write("[ATLAS Nightly System]: but it is a WARNING sign\n")
        else:
            # Sort by modification time
            listordered = sorted(listlog, key=lambda x: compar9(f"{dirlog}/{x}"))
            
            with open(output_file, 'w') as f:
                f.write("=" * 75 + "\n")
                f.write(f"[ATLAS Nightly System]: logfile build.{ARDOC_ARCH}/BuildLogs/{pkg_base}.log\n")
                f.write("=" * 75 + "\n")
                f.write(f"# Version: {linev}\n")
                
                for ff in listordered:
                    ffbase = ff.split('.')[0]
                    infile_path = f"{dirlog}/{ff}"
                    line_cnt = 0
                    
                    try:
                        with open(infile_path, 'r') as inf:
                            lines = inf.readlines()
                            count = len(lines)
                            
                            for line in lines:
                                line = line.rstrip('\n')
                                line_cnt += 1
                                f.write(f"{line}\n")
                                
                                # Check last line for success message
                                if (line_cnt == count and 
                                    "Package build succeeded" not in line and 
                                    ARDOC_PROJECT_NAME != "GAUDI"):
                                    f.write("Warning: the last line does not indicate that the package build is successful\n")
                                    
                                if (line_cnt == count and ARDOC_PROJECT_NAME == "GAUDI"):
                                    f.write(f"Info: CMake does not print messages 'Package build succeeded' for {ARDOC_PROJECT_NAME} project\n")
                                    
                    except IOError as e:
                        f.write(f"Error reading {ff}: {e}\n")
    
    # Return to previous directory
    try:
        os.chdir(prevdir)
    except OSError as e:
        print(f"Cannot cd to {prevdir}: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())