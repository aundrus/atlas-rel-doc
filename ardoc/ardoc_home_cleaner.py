#!/usr/bin/env python3
import os
import sys
import re
import shutil
import time
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("ardoc_home_cleaner.py: Error: one argument required:")
        print("-----maximum allowed age of files/directories (days)")
        sys.exit(1)

    try:
        days = int(sys.argv[1])
    except ValueError:
        print("ardoc_home_cleaner.py: Error: argument must be an integer.")
        sys.exit(1)

    now = time.time()
    age_in_seconds = days * 24 * 60 * 60

    ardoc_home = os.environ.get("ARDOC_HOME")
    if not ardoc_home:
        print("ardoc_home_cleaner.py: Error: variable $ARDOC_HOME is not defined")
        sys.exit(1)

    ardoc_home_dir = Path(ardoc_home).parent
    if not ardoc_home_dir.is_dir():
        print(f"ardoc_home_cleaner.py: Error: area {ardoc_home_dir} is not defined")
        sys.exit(1)

    def clean_directory(directory, pattern):
        print(f"ardoc_home_cleaner.py: INFO: cleaning files in {directory} matching '{pattern}'")
        for item in sorted(directory.iterdir(), key=lambda f: f.stat().st_mtime):
            if re.match(pattern, item.name):
                try:
                    item_age = now - item.stat().st_mtime
                    if item_age > age_in_seconds:
                        print(f"ardoc_home_cleaner: age > {days} day(s): {item.name}")
                        print(f"ardoc_home_cleaner: DELETED: {item}")
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()
                except FileNotFoundError:
                    # File might have been deleted by another process
                    continue


    clean_directory(ardoc_home_dir, r"^ardoc_local_gen_config.*$")

    ardoc_webdir = os.environ.get("ARDOC_WEBDIR")
    if ardoc_webdir and Path(ardoc_webdir).is_dir():
        clean_directory(Path(ardoc_webdir), r"^ARDOC.*Log.*$")

    ardoc_job_log = os.environ.get("ARDOC_JOB_LOG")
    if ardoc_job_log:
        ardoc_job_logdir = Path(ardoc_job_log).parent
        if ardoc_job_logdir.is_dir():
            clean_directory(ardoc_job_logdir, r"^log.*$")

if __name__ == "__main__":
    main()
