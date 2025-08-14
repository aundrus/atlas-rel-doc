#!/usr/bin/env python3
"""
ARDOC - Nightly Control System
Author: Alex Undrus <undrus@bnl.gov>

----------------------------------------------------------
ardoc_progress_informer.py
----------------------------------------------------------

Python migration of ardoc_progress_informer
Updates progress status and triggers database operations
"""

import os
import sys
import subprocess


def main():
    # Get environment variables
    ARDOC_HOME = os.environ.get('ARDOC_HOME', '')
    ARDOC_WEBDIR = os.environ.get('ARDOC_WEBDIR', '')
    ARDOC_PROJECT_HOME = os.environ.get('ARDOC_PROJECT_HOME', '')
    ARDOC_PROJECT_NAME = os.environ.get('ARDOC_PROJECT_NAME', '')
    ARDOC_PROJECT_RELNAME = os.environ.get('ARDOC_PROJECT_RELNAME_COPY', '')
    ARDOC_PROJECT_RELNUMB = os.environ.get('ARDOC_PROJECT_RELNUMB_COPY', '')
    ARDOC_WORK_AREA = os.environ.get('ARDOC_WORK_AREA', '')
    ARDOC_LOG = os.environ.get('ARDOC_LOG', '')
    ARDOC_TESTLOG = os.environ.get('ARDOC_TESTLOG', '')
    
    step = 0
    param = 0
    suffix = f"_{ARDOC_PROJECT_RELNUMB}" if ARDOC_PROJECT_RELNUMB else ""
    
    # Parse command line arguments
    if len(sys.argv) >= 2:
        step = int(sys.argv[1])
    if len(sys.argv) >= 3:
        param = sys.argv[2]
    
    # Write progress status
    progress_file = f"{ARDOC_WORK_AREA}/ardoc_progress_status"
    try:
        with open(progress_file, 'w') as f:
            f.write(str(step))
    except IOError:
        print(f"Error writing to {progress_file}")
        return 1
    
    # Prepare output files
    outfile_status = f"{ARDOC_WEBDIR}/status_rel{suffix}.js"
    outfile_date = f"{ARDOC_WEBDIR}/date_rel{suffix}.js"
    
    # Get log directory
    genlogdir = os.path.dirname(ARDOC_LOG) if ARDOC_LOG else ""
    testlogdir = os.path.dirname(ARDOC_TESTLOG) if ARDOC_TESTLOG else ""
    
    try:
        with open(outfile_status, 'w') as f:
            f.write(f"function status{suffix}(){{return ")
            
            # Handle different step values
            if step == 0:
                f.write("'nightly started'}")
                # Execute database operations
                if genlogdir:
                    subprocess.run([
                        'bash', '-c',
                        f'genlogdir="{genlogdir}";{ARDOC_HOME}/ardoc_oracle_wrapper.sh 3 python3 {ARDOC_HOME}/ardoc_oracle_reljobs.py >> $genlogdir/ardoc_general.logora 2>&1'
                    ], check=False)
                    subprocess.run([
                        'bash', '-c', 
                        f'genlogdir="{genlogdir}";{ARDOC_HOME}/ardoc_db_access -b -s "CONFIG" -p "{param}" >> $genlogdir/ardoc_general.logora 2>&1'
                    ], check=False)
                    subprocess.run([
                        'bash', '-c',
                        f'genlogdir="{genlogdir}";{ARDOC_HOME}/ardoc_db_access -e -s "CONFIG" >> $genlogdir/ardoc_general.logora 2>&1'
                    ], check=False)
                    
            elif step == 1:
                f.write("'configuration in progress'}")
                if genlogdir:
                    subprocess.run([
                        'bash', '-c',
                        f'genlogdir="{genlogdir}";{ARDOC_HOME}/ardoc_db_access -e -s "TOOLINIT" --nochange >> $genlogdir/ardoc_general.logora 2>&1'
                    ], check=False)
                    
            elif step == 2:
                f.write("'checkout done'}")
                if genlogdir:
                    subprocess.run([
                        'bash', '-c',
                        f'genlogdir="{genlogdir}";{ARDOC_HOME}/ardoc_oracle_wrapper.sh 3 python3 {ARDOC_HOME}/ardoc_oracle_tags.py >> $genlogdir/ardoc_general.logora 2>&1'
                    ], check=False)
                    
            elif step == 3:
                f.write("'make started'}")
                if genlogdir:
                    subprocess.run([
                        'bash', '-c',
                        f'genlogdir="{genlogdir}";{ARDOC_HOME}/ardoc_db_access -e -s "PROJECTCONF" >> $genlogdir/ardoc_general.logora 2>&1'
                    ], check=False)
                    
            elif step == 4:
                f.write("'make done, tests started'}")
                if genlogdir:
                    subprocess.run([
                        'bash', '-c',
                        f'genlogdir="{genlogdir}";{ARDOC_HOME}/ardoc_db_access_test -e -s "BUILD" >> $genlogdir/ardoc_general.logora 2>&1'
                    ], check=False)
                    
            elif step == 44:
                # No status message, just execute command
                if genlogdir:
                    subprocess.run([
                        'bash', '-c',
                        f'genlogdir="{genlogdir}";{ARDOC_HOME}/ardoc_oracle_wrapper.sh 3 python3 {ARDOC_HOME}/ardoc_oracle_build_results.py --complete >> $genlogdir/ardoc_build.logora 2>&1'
                    ], check=False)
                return 0
                
            elif step == 5:
                f.write("'kit build in progress'}")
                
            elif step == 6:
                f.write("'rpm build in progress'}")
                
            elif step == 7:
                f.write("'qa tests done'}")
                
            elif step == 8:
                f.write("'integrated tests done'}")
                if genlogdir:
                    subprocess.run([
                        'bash', '-c',
                        f'genlogdir="{genlogdir}";{ARDOC_HOME}/ardoc_db_access -e -s "INT" >> $genlogdir/ardoc_general.logora 2>&1'
                    ], check=False)
                    
            elif step == 9:
                f.write("'kv done'}")
                
            elif step == 10:
                f.write("'done'}")
                if genlogdir:
                    subprocess.run([
                        'bash', '-c',
                        f'genlogdir="{genlogdir}";{ARDOC_HOME}/ardoc_db_access -e -s "ERR" >> $genlogdir/ardoc_general.logora 2>&1'
                    ], check=False)
                if testlogdir:
                    subprocess.run([
                        'bash', '-c',
                        f'genlogdir="{testlogdir}";{ARDOC_HOME}/ardoc_oracle_wrapper.sh 3 python3 {ARDOC_HOME}/ardoc_oracle_results.py -c >> $genlogdir/ardoc_test_final.logora 2>&1'
                    ], check=False)
                    
            else:
                f.write("'UNAVAILABLE'}")
                
    except IOError:
        print(f"Error writing to {outfile_status}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
