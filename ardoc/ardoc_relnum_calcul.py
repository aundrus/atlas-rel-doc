#!/usr/bin/env python3

import os
import sys
import re
from pathlib import Path
from datetime import datetime

def get_file_age_in_days(file_path: Path) -> int:
    """
    Calculates the age of a file in days.
    This is a Python equivalent of the 'ardoc_mtime' subroutine in the original script.
    """
    try:
        mod_time_sec = file_path.stat().st_mtime
        mod_time_dt = datetime.fromtimestamp(mod_time_sec)
        current_time_dt = datetime.now()
        
        # The original script's logic is based on the day of the year.
        mod_day_of_year = mod_time_dt.timetuple().tm_yday
        current_day_of_year = current_time_dt.timetuple().tm_yday
        
        diff_days = current_day_of_year - mod_day_of_year
        
        # Account for year change
        if diff_days < 0:
            # A simple way to handle the year wrap-around, assuming no files are older than a year.
            # This matches the original script's logic of `+ 366`.
            diff_days += 366
            
        return diff_days
    except FileNotFoundError:
        return -1 # Return an indicator that the file doesn't exist

def main():
    """
    Main function to calculate a release number based on a lifetime parameter.
    This script is a Python migration of 'ardoc_relnum_calcul.pl'.
    """
    if len(sys.argv) != 2:
        print("ardoc_relnum_calcul: one arg req: lifetime parameter", file=sys.stderr)
        sys.exit(1)

    # --- Get environment variables ---
    ardoc_hour_str = os.environ.get("ARDOC_HOUR", "")
    ardoc_day_offset_str = os.environ.get("ARDOC_DAY_OFFSET", "")
    ardoc_project_home = os.environ.get("ARDOC_PROJECT_HOME")
    ardoc_project_relname_gen = os.environ.get("ARDOC_PROJECT_RELNAME_GEN")
    
    lifetime_arg = sys.argv[1]
    lifetime_num_str = lifetime_arg
    last_sym = ""

    # --- Parse lifetime argument ---
    if lifetime_arg and not lifetime_arg[-1].isdigit():
        last_sym = lifetime_arg[-1]
        lifetime_num_str = lifetime_arg[:-1]

    try:
        lifetime_num = int(lifetime_num_str)
    except ValueError:
        print(f"Error in lifetime format: {lifetime_arg}", file=sys.stderr)
        sys.exit(1)

    # --- Cyclic Mode (if lifetime ends with 'c') ---
    if last_sym.lower() == 'c':
        if not ardoc_project_home or not Path(ardoc_project_home).is_dir():
            print(f"Error: ARDOC_PROJECT_HOME is not set or not a directory.", file=sys.stderr)
            # The original script would fail on opendir, so we exit.
            sys.exit(1)

        all_files = os.listdir(ardoc_project_home)
        
        # Filter for files matching the release name generator prefix
        release_files = [f for f in all_files if f.startswith(str(ardoc_project_relname_gen))]
        
        rel_numbers = set()
        max_rel_num = -1
        max_age_rel_num = -1
        max_age_days = -1

        for filename in release_files:
            parts = filename.split('_')
            if parts and parts[-1].isdigit():
                rel_num = int(parts[-1])
                rel_numbers.add(rel_num)
                
                if rel_num > max_rel_num:
                    max_rel_num = rel_num
                
                file_age = get_file_age_in_days(Path(ardoc_project_home) / filename)
                if file_age > max_age_days:
                    max_age_days = file_age
                    max_age_rel_num = rel_num
        
        final_rel_num = 0
        if max_rel_num < (lifetime_num - 1):
            final_rel_num = max_rel_num + 1
        else:
            # Find the first unused release number starting from 0
            i = 0
            while True:
                if i not in rel_numbers:
                    final_rel_num = i
                    break
                # The original script has a potential infinite loop if all numbers
                # up to max_age_rel_num are taken. We add a safeguard.
                if i > max_age_rel_num and i > max_rel_num:
                    final_rel_num = i # Should not be reached with original logic
                    break
                i += 1
        
        sys.stdout.write(str(final_rel_num))

    # --- Time-based Mode ---
    else:
        now = datetime.now()
        
        if lifetime_num == 7:
            time_num = now.weekday() # Monday is 0, Sunday is 6
        else:
            time_num = now.timetuple().tm_yday # Day of the year (1-366)

        if ardoc_day_offset_str.isdigit():
            time_num += int(ardoc_day_offset_str)

        if ardoc_hour_str.isdigit():
            ardoc_hour = int(ardoc_hour_str)
            if now.hour >= ardoc_hour:
                if time_num == 6 and lifetime_num == 7: # Sunday wraps to 0
                    time_num = 0
                else:
                    time_num += 1
        
        final_rel_num = ""
        if lifetime_num == 0:
            final_rel_num = ""
        elif lifetime_num == 1:
            final_rel_num = 0
        else:
            final_rel_num = time_num % lifetime_num
        
        sys.stdout.write(str(final_rel_num))

    sys.exit(0)

if __name__ == "__main__":
    main()
