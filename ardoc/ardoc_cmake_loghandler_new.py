#!/usr/bin/env python3

#
# ARDOC - NIghtly COntrol System
# Author Alex Undrus <undrus@bnl.gov>
#
# ----------------------------------------------------------
# ardoc_cmake_loghandler_new.py - Python migration of ardoc_cmake_loghandler_new.pl
# ----------------------------------------------------------
import os
import sys
import argparse
from pathlib import Path

def get_mtime(filepath):
    """Returns the modification time of a file."""
    try:
        return Path(filepath).stat().st_mtime
    except FileNotFoundError:
        return 0

def main():
    """
    Main function to handle cmake log processing.
    """
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="ARDOC CMake Log Handler")
    parser.add_argument("-f", "--file-suffix", default="", help="Suffix for log files.")
    # The -l/--infile argument from the perl script seems unused in the new logic, so it's omitted.
    
    args = parser.parse_args()

    # --- Environment Variable Setup ---
    ARDOC_WORK_AREA = os.environ.get("ARDOC_WORK_AREA")
    ARDOC_PROJECT_NAME = os.environ.get("ARDOC_PROJECT_NAME", "UnknownProject")
    ARDOC_DBFILE_GEN = os.environ.get("ARDOC_DBFILE_GEN")
    ARDOC_RELHOME = os.environ.get("ARDOC_RELHOME")
    ARDOC_ARCH = os.environ.get("ARDOC_ARCH")
    ARDOC_LOG = os.environ.get("ARDOC_LOG")

    # Validate necessary environment variables
    required_vars = {
        "ARDOC_WORK_AREA": ARDOC_WORK_AREA,
        "ARDOC_DBFILE_GEN": ARDOC_DBFILE_GEN,
        "ARDOC_RELHOME": ARDOC_RELHOME,
        "ARDOC_ARCH": ARDOC_ARCH,
        "ARDOC_LOG": ARDOC_LOG,
    }
    for var, value in required_vars.items():
        if not value:
            sys.stderr.write(f"Error: Environment variable {var} is not set.\n")
            sys.exit(1)

    # --- File and Path Setup ---
    ardoc_logdir = Path(ARDOC_LOG).parent
    dbfile_gen_base = Path(ARDOC_DBFILE_GEN).name
    dbfilegen_res = Path(ARDOC_WORK_AREA) / f"{dbfile_gen_base}_res"

    # --- Read Package Database ---
    try:
        with open(dbfilegen_res, 'r') as dbf:
            # Read, strip, and filter out commented/empty lines
            dbc = [line.strip() for line in dbf if line.strip() and not line.strip().startswith('#')]
    except FileNotFoundError:
        sys.stderr.write(f"Error: Database file not found at {dbfilegen_res}\n")
        sys.exit(1)

    # --- Process Each Package ---
    for line in dbc:
        fields = line.split()
        if not fields:
            continue
        
        pkg = fields[0]
        pkg_base = Path(pkg).name
        print(f"ardoc_cmake_loghandler_new.py: package: {pkg}, base: {pkg_base}")

        # Determine the directory for build logs
        build_logs_dir_primary = Path(ARDOC_RELHOME) / f"build.{ARDOC_ARCH}" / "BuildLogs"
        build_logs_dir_fallback = Path(ARDOC_RELHOME) / "BuildLogs"
        
        dirlog = build_logs_dir_primary if build_logs_dir_primary.is_dir() else build_logs_dir_fallback
        
        if not dirlog.is_dir():
            print(f"Warning: Could not find build log directory for {pkg}: {dirlog}")
            continue
            
        print(f"ardoc_cmake_loghandler_new.py: dirlog: {dirlog}")

        # Find log files for the package
        try:
            listlog = list(dirlog.glob(f"{pkg_base}.log"))
            print(f"ardoc_cmake_loghandler_new.py: logs: {listlog}")
        except Exception as e:
            print(f"Error searching for logs in {dirlog}: {e}")
            listlog = []

        # Get version info
        file_vers = Path(ARDOC_RELHOME) / pkg / "version.cmake"
        print(f"ardoc_cmake_loghandler_new.py: version file: {file_vers}")
        version_info = "N/A"
        if file_vers.is_file():
            try:
                version_info = file_vers.read_text().strip()
            except IOError as e:
                print(f"Warning: Could not read version file {file_vers}: {e}")

        # Prepare the output log file path
        pkgn = pkg.replace('/', '_')
        output_log_file = ardoc_logdir / f"{pkgn}.loglog{args.file_suffix}"

        # --- Aggregate Logs or Create Placeholder ---
        try:
            with open(output_log_file, 'w') as out:
                out.write("=" * 75 + "\n")
                
                if not listlog:
                    # No log files found
                    out.write(f"[ATLAS Nightly System]: no build logfiles for {pkg_base} are found in {dirlog.relative_to(ARDOC_RELHOME)}\n")
                    out.write("=" * 75 + "\n")
                    out.write("[ATLAS Nightly System]: absence of build logfile alone is not a problem sign\n")
                    out.write("[ATLAS Nightly System]: but it is a WARNING sign\n")
                else:
                    # Log files found, sort by modification time
                    listlog.sort(key=lambda f: get_mtime(f))
                    
                    out.write(f"[ATLAS Nightly System]: logfile {dirlog.relative_to(ARDOC_RELHOME)}/{pkg_base}.log\n")
                    out.write("=" * 75 + "\n")
                    out.write(f"# Version: {version_info}\n")
                    
                    for log_path in listlog:
                        try:
                            content = log_path.read_text().splitlines()
                            for line_content in content:
                                out.write(f"{line_content}\n")
                            
                            # Check the last line for success message
                            if content and "Package build succeeded" not in content[-1]:
                                if ARDOC_PROJECT_NAME == "GAUDI":
                                    out.write(f"Info: CMake does not print messages 'Package build succeeded' for {ARDOC_PROJECT_NAME} project\n")
                                else:
                                    out.write("Warning: the last line does not indicate that the package build is successful\n")
                        except IOError as e:
                            out.write(f"\nError reading log file {log_path}: {e}\n")
        except IOError as e:
            sys.stderr.write(f"Error writing to output log {output_log_file}: {e}\n")

if __name__ == "__main__":
    main()
