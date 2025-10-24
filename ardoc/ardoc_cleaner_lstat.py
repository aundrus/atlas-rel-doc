#!/usr/bin/env python3
import os
import sys
import time
import re
import shutil
import subprocess

def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("ardoc_cleaner_lstat.py: two or three arguments required:")
        print("-----path to area and maximum allowed age of files (days)")
        print("-----and exception regexp")
        sys.exit(1)

    area = sys.argv[1]
    try:
        days = float(sys.argv[2])
    except ValueError:
        print("ardoc_cleaner_lstat.py: days argument must be a number")
        sys.exit(1)

    reg_except = None
    if len(sys.argv) == 4:
        reg_except = sys.argv[3]

    if not os.path.isdir(area):
        print(f"ardoc_cleaner_lstat.py: area {area} does not exist")
        sys.exit(1)

    now = time.time()
    
    all_files = os.listdir(area)
    
    files_with_mtime = []
    for f in all_files:
        if f == '.' or f == '..':
            continue
        path = os.path.join(area, f)
        try:
            # For ardoc_cleaner_lstat, we use lstat which does not follow symlinks
            mtime = os.lstat(path).st_mtime
            files_with_mtime.append((path, mtime))
        except OSError:
            # A file could have been deleted between listdir and lstat
            continue

    # Sort by modification time, oldest first
    files_with_mtime.sort(key=lambda x: x[1])

    for path, mtime in files_with_mtime:
        if reg_except and re.search(reg_except, path):
            continue

        age_seconds = now - mtime
        age_days = age_seconds / (24 * 3600)

        if age_days <= days:
            # The rest of the files are newer, so we stop
            break
        
        print(f"ardoc_cleaner_lstat: age > {days} day(s):  {os.path.basename(path)} {age_days:.1f} > {days}")

        try:
            if os.path.islink(path):
                link_target = os.readlink(path)
                if '/eos/squash' in link_target:
                    print(f"ardoc_cleaner_lstat: SquashFS volume DELETED:  {path}")
                    result = subprocess.run(['eos', 'squash', 'rm', path], capture_output=True, text=True)
                    print(result.stdout)
                    print(result.stderr, file=sys.stderr)
                else:
                    print(f"ardoc_cleaner_lstat: link DELETED:  {path}")
                    os.remove(path)
            elif os.path.isdir(path):
                print(f"ardoc_cleaner_lstat: DELETED:  {path}")
                shutil.rmtree(path)
            else:
                print(f"ardoc_cleaner_lstat: DELETED:  {path}")
                os.remove(path)
        except Exception as e:
            print(f"ardoc_cleaner_lstat: Error deleting {path}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
