#!/usr/bin/env python3
import os
import sys
import argparse
import re
from pathlib import Path

def get_package_key(line):
    """Sort key function to sort by length of first word, descending."""
    parts = line.strip().split()
    if not parts:
        return 0
    return len(parts[0])

def main():
    parser = argparse.ArgumentParser(description='ARDOC CMake Log Handler - 2nd Loop')
    parser.add_argument('-f', '--file-suffix', default='', help='Suffix for log files')
    parser.add_argument('-l', '--infile', help='Input log file to override ARDOC_BUILDLOG')
    args = parser.parse_args()

    # --- Environment Variables ---
    ardoc_work_area = os.environ.get("ARDOC_WORK_AREA")
    ardoc_buildlog = os.environ.get("ARDOC_BUILDLOG")
    ardoc_dbfile_path = os.environ.get("ARDOC_DBFILE")
    ardoc_project_name = os.environ.get("ARDOC_PROJECT_NAME")

    if not all([ardoc_work_area, ardoc_buildlog, ardoc_dbfile_path, ardoc_project_name]):
        print("Error: One or more required environment variables are not set.", file=sys.stderr)
        sys.exit(1)

    makelog_path = Path(args.infile if args.infile else ardoc_buildlog)
    logdir = makelog_path.parent
    dbfile_basename = Path(ardoc_dbfile_path).name
    dbfilegen = Path(ardoc_work_area) / dbfile_basename
    
    remnants_file = logdir / f"REMNANTS_2ndloop.log{args.file_suffix}"
    remnants_file.write_text("=" * 75 + "\n")
    remnants_file.open('a').write("[ATLAS ARDOC]: cmake build output that can not be assigned to a specific package\n")
    remnants_file.open('a').write("=" * 75 + "\n")

    try:
        with open(dbfilegen, 'r') as f:
            dbc = f.readlines()
        dbc.sort(key=get_package_key, reverse=True)
    except FileNotFoundError:
        print(f"Error: DB file not found at {dbfilegen}", file=sys.stderr)
        sys.exit(1)

    package_files = {}
    
    try:
        with open(makelog_path, 'r') as in_f, open(remnants_file, 'a') as remnants_f:
            for i, line in enumerate(in_f, 1):
                line_stripped = line.strip()
                if not line_stripped or not re.search(r'[A-Za-z0-9_]', line_stripped):
                    remnants_f.write(f"{i} -- {line}")
                    continue

                found_pkg = None
                for pkg_line in dbc:
                    pkg_line = pkg_line.strip()
                    if not pkg_line or pkg_line.startswith('#'):
                        continue
                    
                    package_name = pkg_line.split()[0]
                    if package_name in line:
                        found_pkg = package_name
                        break
                
                if found_pkg:
                    pkgn = found_pkg.replace('/', '_')
                    file_out_path = logdir / f"{pkgn}.loglog{args.file_suffix}"

                    if file_out_path not in package_files:
                        package_files[file_out_path] = True
                        with open(file_out_path, 'a') as pkg_f:
                            pkg_f.write("=" * 75 + "\n")
                            pkg_f.write(f"[ATLAS ARDOC]: build output for package {found_pkg} extracted from cmake logfile\n")
                            pkg_f.write("=" * 75 + "\n")
                    
                    with open(file_out_path, 'a') as pkg_f:
                        pkg_f.write(f"{i} -- {line}")
                else:
                    remnants_f.write(f"{i} -- {line}")

    except FileNotFoundError:
        print(f"Error: Make log file not found at {makelog_path}", file=sys.stderr)
        sys.exit(1)

    # Append remnants to the main project log
    project_log_path = logdir / f"{ardoc_project_name}Release.loglog{args.file_suffix}"
    print(f"ardoc_cmake_loghandler_2ndloop: adding unassigned output lines to {project_log_path}")
    with open(project_log_path, 'a') as out_f, open(remnants_file, 'r') as remnants_f:
        out_f.write(remnants_f.read())
    print(f"ardoc_cmake_loghandler_2ndloop: completed addition of unassigned output lines to {project_log_path}")


if __name__ == "__main__":
    main()
