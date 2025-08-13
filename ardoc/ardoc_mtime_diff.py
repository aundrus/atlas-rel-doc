#!/usr/bin/env python3

import sys
import os
from pathlib import Path
import time

def main():
    """
    Calculates a value based on the time difference between a file's 
    modification time and the current time.

    This script is a Python migration of the Perl script 'ardoc_mtime_diff.pl'.
    It takes one or more file paths as command-line arguments. For each file,
    it calculates a value representing the age of the file in tenths of a day.
    """
    if len(sys.argv) < 2:
        # The original script exits silently, this provides a bit more info.
        print("Usage: ardoc_mtime_diff.py <file1> [file2...]", file=sys.stderr)
        sys.exit(1)

    # Process each file provided on the command line
    for file_path_str in sys.argv[1:]:
        file_path = Path(file_path_str)
        
        try:
            # Get the modification time (in seconds since the epoch)
            mod_time_sec = file_path.stat().st_mtime
            
            # Get the current time (in seconds since the epoch)
            current_time_sec = time.time()
            
            # Calculate the difference in seconds
            time_diff_sec = current_time_sec - mod_time_sec
            
            # Convert the difference to hours
            time_diff_hours = time_diff_sec / 3600
            
            # Calculate the final value, mimicking the Perl script's logic:
            # int( (difference_in_hours / 24) * 10 )
            # This represents the number of tenths of a day since modification.
            diff_time_prec_1 = int((time_diff_hours / 24) * 10)
            
            # The original script prints the result without a newline.
            # Using sys.stdout.write to replicate this behavior.
            sys.stdout.write(str(diff_time_prec_1))

        except FileNotFoundError:
            # The original script would likely fail with a warning.
            # This provides a clearer error message.
            print(f"Error: File not found at '{file_path_str}'", file=sys.stderr)
            # The original script would likely stop processing here, so we exit.
            sys.exit(1)
        except Exception as e:
            print(f"An error occurred while processing '{file_path_str}': {e}", file=sys.stderr)
            sys.exit(1)

    # The original script exits with an implicit status code.
    # We exit explicitly. The loop above handles printing.
    sys.exit(0)

if __name__ == "__main__":
    main()
