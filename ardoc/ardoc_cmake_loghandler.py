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
    parser = argparse.ArgumentParser(description='ARDOC CMake Log Handler')
    parser.add_argument('-f', '--file-suffix', default='', help='Suffix for log files')
    parser.add_argument('-l', '--infile', help='Input log file to override ARDOC_BUILDLOG')
    parser.add_argument('-t', '--testhandling', action='store_true', help='Enable test handling mode')
    args = parser.parse_args()

    # --- Environment Variables ---
    ardoc_work_area = os.environ.get("ARDOC_WORK_AREA")
    ardoc_project_relname = os.environ.get("ARDOC_PROJECT_RELNAME")
    ardoc_webpage = os.environ.get("ARDOC_WEBPAGE")
    ardoc_buildlog = os.environ.get("ARDOC_BUILDLOG")
    ardoc_testlog = os.environ.get("ARDOC_TESTLOG")
    ardoc_dbfile_path = os.environ.get("ARDOC_DBFILE")
    ardoc_test_dbfile_path = os.environ.get("ARDOC_TEST_DBFILE")
    ardoc_relhome = os.environ.get("ARDOC_RELHOME")
    ardoc_arch = os.environ.get("ARDOC_ARCH")
    ardoc_ninjalog = os.environ.get("ARDOC_NINJALOG")
    ardoc_project_name = os.environ.get("ARDOC_PROJECT_NAME")

    if args.testhandling:
        ardoc_log = ardoc_testlog
        dbfile_path = ardoc_test_dbfile_path + "_res" if ardoc_test_dbfile_path else None
        log_type = "Test"
    else:
        ardoc_log = ardoc_buildlog
        dbfile_path = ardoc_dbfile_path
        log_type = "Build"

    if not all([ardoc_work_area, ardoc_project_relname, ardoc_log, dbfile_path, ardoc_relhome, ardoc_arch]):
        print("Error: One or more required environment variables are not set.", file=sys.stderr)
        sys.exit(1)

    makelog = args.infile if args.infile else ardoc_buildlog
    logdir = Path(ardoc_log).parent
    dbfile_basename = Path(dbfile_path).name
    dbfilegen = Path(ardoc_work_area) / dbfile_basename

    print(f"ardoc_cmake_loghandler.py: TESTHANDLING KEY: {args.testhandling}")
    print(f"ardoc_cmake_loghandler: files/dirs {dbfilegen} {ardoc_log} {logdir}")

    try:
        with open(dbfilegen, 'r') as f:
            dbc = f.readlines()
        # Sort packages by the length of their name, descending
        dbc.sort(key=get_package_key, reverse=True)
    except FileNotFoundError:
        print(f"Error: DB file not found at {dbfilegen}", file=sys.stderr)
        sys.exit(1)

    for line in dbc:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        fields = line.split()
        pkg = fields[0]
        pkg_base = Path(pkg).name
                print(f"ardoc_cmake_loghandler.py: version file: {file_vers}")

        dirlog_path_str = f"{log_type}Logs"
        dirlog = Path(ardoc_relhome) / 'build' / ardoc_arch / dirlog_path_str
        if not dirlog.is_dir() and (Path(ardoc_relhome) / dirlog_path_str).is_dir():
            dirlog = Path(ardoc_relhome) / dirlog_path_str

        try:
            all_logs = [f for f in os.listdir(dirlog) if f.startswith(f"{pkg_base}.log")]
            # Sort logs by modification time, oldest first
            all_logs.sort(key=lambda f: (dirlog / f).stat().st_mtime)
            print(f"ardoc_cmake_loghandler.py: logs: {listlog}")
        except FileNotFoundError:
            all_logs = []
            print(f"ardoc_cmake_loghandler.py: warning: log directory not found: {dirlog}")


        pkgn = pkg.replace('/', '_')
        if args.testhandling:
            file_out_path = logdir / f"{pkgn}___{pkg_base}Conf__{pkg_base}Test__m.loglog"
        else:
            file_out_path = logdir / f"{pkgn}.loglog"

        with open(file_out_path, 'w') as out_f:
            if not all_logs:
                out_f.write("=" * 75 + "\n")
                out_f.write(f"[ATLAS ARDOC]: no {log_type.lower()} logfiles for {pkg_base} are found in {dirlog}\n")
                if not args.testhandling:
                    out_f.write(f"[ATLAS ARDOC]: absence of {log_type.lower()} logfile alone is not a problem sign\n")
                    out_f.write("[ATLAS ARDOC]: but it is a WARNING sign\n")
                out_f.write("=" * 75 + "\n")
            else:
                for log_file in all_logs:
                    try:
                        with open(dirlog / log_file, 'r') as in_f:
                            content = in_f.readlines()
                            out_f.writelines(content)
                            # Check the last line for success message
                            if not args.testhandling and content:
                                last_line = content[-1].strip()
                                if f"Package {log_type.lower()} succeeded" not in last_line and "pseudo package" not in last_line and ardoc_project_name != "GAUDI":
                                     out_f.write(f"\nWarning: the last line does not indicate that the package {log_type.lower()} is successful\n")
                                if ardoc_project_name == "GAUDI":
                                     out_f.write(f"\nInfo: CMake does not print messages 'Package {log_type.lower()} succeeded' for {ardoc_project_name} project \n")
                    except FileNotFoundError:
                        print(f"Warning: Could not open log file {dirlog / log_file}")


if __name__ == "__main__":
    main()
