#!/usr/bin/env python3

#
# ARDOC - NIghtly COntrol System
# Author Alex Undrus <undrus@bnl.gov>
#
# ----------------------------------------------------------
# ardoc_cmake_loghandler_new_2ndloop.py - Python migration of ardoc_cmake_loghandler_new_2ndloop.pl
# ----------------------------------------------------------
import os
import sys
import argparse
from pathlib import Path

def compar(line):
    """
    Comparison function to sort packages by length.
    Longer package names are processed first to avoid substring conflicts.
    """
    stripped_line = line.strip()
    if not stripped_line:
        return 0
    package = stripped_line.split()[0]
    return len(package)

def main():
    """
    Main function to handle cmake log processing.
    """
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="ARDOC CMake Log Handler - Second Loop")
    parser.add_argument("-f", "--file-suffix", default="", help="Suffix for log files.")
    parser.add_argument("-l", "--infile", help="Input log file (overrides ARDOC_BUILDLOG).")
    
    args = parser.parse_args()

    # --- Environment Variable Setup ---
    ARDOC_PROJECT_NAME = os.environ.get("ARDOC_PROJECT_NAME", "UnknownProject")
    ARDOC_WORK_AREA = os.environ.get("ARDOC_WORK_AREA", ".")
    ARDOC_BUILDLOG = os.environ.get("ARDOC_BUILDLOG")
    ARDOC_DBFILE_GEN = os.environ.get("ARDOC_DBFILE_GEN")

    if not ARDOC_BUILDLOG and not args.infile:
        sys.stderr.write("Error: ARDOC_BUILDLOG is not set and -l/--infile was not provided.\n")
        sys.exit(1)
        
    if not ARDOC_DBFILE_GEN:
        sys.stderr.write("Error: ARDOC_DBFILE_GEN environment variable is not set.\n")
        sys.exit(1)

    # --- File and Path Setup ---
    makelog_path = Path(args.infile if args.infile else ARDOC_BUILDLOG)
    logdir = makelog_path.parent
    
    report_file = Path(ARDOC_WORK_AREA) / "ardoc_loghandler_2ndloop_report"
    remnants_file = logdir / f"REMNANTS_2ndloop.log{args.file_suffix}"
    
    # Clean up remnants file
    if remnants_file.exists():
        remnants_file.unlink()
    remnants_file.touch()

    dbfile_gen_path = Path(ARDOC_WORK_AREA) / f"{Path(ARDOC_DBFILE_GEN).name}_res"

    # --- Read and Sort Package Database ---
    try:
        with open(dbfile_gen_path, 'r') as dbf:
            dbc = [line for line in dbf if line.strip() and not line.strip().startswith('#')]
        
        # Sort by package name length (descending)
        dbc.sort(key=compar, reverse=True)
    except FileNotFoundError:
        sys.stderr.write(f"Error: Database file not found at {dbfile_gen_path}\n")
        sys.exit(1)

    # --- Main Log Processing Loop ---
    file_occurrence = set()
    current_pkg_file = None
    
    try:
        with open(report_file, 'w') as rep, \
             open(remnants_file, 'w') as rmnt, \
             open(makelog_path, 'r') as infile:
            
            rmnt.write("=" * 75 + "\n")
            rmnt.write("[ATLAS Nightly System]: cmake build output that can not be assigned to a specific package\n")
            rmnt.write("=" * 75 + "\n")

            for line_num, line in enumerate(infile, 1):
                line = line.rstrip()
                
                # Find the best matching package for the line
                best_match_pkg = ""
                for pkg_line in dbc:
                    package_name = pkg_line.split()[0]
                    if package_name in line:
                        best_match_pkg = package_name
                        break # Since dbc is sorted by length, first match is the best
                
                if best_match_pkg:
                    pkg_normalized = best_match_pkg.replace('/', '_')
                    log_file_path = logdir / f"{pkg_normalized}.loglog{args.file_suffix}"
                    current_pkg_file = log_file_path
                    
                    print(f"ardoc_cmake_loghandler_new_2ndloop: found separator for package {best_match_pkg}")
                    rep.write(f"{best_match_pkg}\n")
                    
                    if pkg_normalized not in file_occurrence:
                        with open(log_file_path, 'a') as out:
                            out.write("=" * 75 + "\n")
                            out.write(f"[ATLAS Nightly System]: build output for package {best_match_pkg} extracted from cmake logfile\n")
                            out.write("=" * 75 + "\n")
                        file_occurrence.add(pkg_normalized)

                # Write line to the appropriate file
                if current_pkg_file:
                    with open(current_pkg_file, 'a') as out:
                        out.write(f"{line_num} -- {line}\n")
                else:
                    rmnt.write(f"{line_num} -- {line}\n")

    except IOError as e:
        sys.stderr.write(f"Error processing files: {e}\n")
        sys.exit(1)

    # --- Append Remnants to Project Log ---
    project_log_file = logdir / f"{ARDOC_PROJECT_NAME}Release.loglog{args.file_suffix}"
    print(f"ardoc_cmake_loghandler_new_2ndloop: adding unassigned output lines to {project_log_file}")
    
    try:
        with open(project_log_file, 'a') as out, open(remnants_file, 'r') as rmnt:
            out.write(rmnt.read())
        print(f"ardoc_cmake_loghandler_new_2ndloop: completed addition of unassigned output lines to {project_log_file}")
    except IOError as e:
        sys.stderr.write(f"Error appending remnants: {e}\n")

if __name__ == "__main__":
    main()
