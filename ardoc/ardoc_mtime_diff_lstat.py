#!/usr/bin/env python3
import os
import sys
import time

def main():
    for filepath in sys.argv[1:]:
        try:
            # Get the modification time using lstat
            mod_time_struct = time.localtime(os.lstat(filepath).st_mtime)
            
            # Get current time
            cur_time_struct = time.localtime()

            # Convert to seconds since epoch
            timemod = time.mktime(mod_time_struct)
            timecur = time.mktime(cur_time_struct)
            
            # Calculate difference
            timedif = timecur - timemod
            diffhour = timedif / 3600
            diftimprec_1 = int((diffhour / 24) * 10)
            
            print(diftimprec_1, end='')

        except FileNotFoundError:
            sys.stderr.write(f"Error: File not found: {filepath}\n")
        except Exception as e:
            sys.stderr.write(f"An error occurred: {e}\n")

if __name__ == "__main__":
    main()
