#!/usr/bin/env python3
import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="ardoc_oracle_errortester")
    parser.add_argument("filename", help="name of logfile")
    args = parser.parse_args()

    filename = args.filename

    e_patterns = ["ORA-", "permission denied", "Disk quota exceeded", ": Error:", "CVBFGG"]
    e_ignore = ["CVBFGH", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"]
    e_correlators = ["", "", "", "ardoc", ""]
    
    eeee = ""
    problems = 0
    lineE = 0
    lineT = 0

    if os.path.isfile(filename):
        try:
            with open(filename, 'r', errors='ignore') as f:
                for line in f:
                    lineT += 1
                    for i, pattern in enumerate(e_patterns):
                        if pattern in line and e_ignore[i] not in line:
                            if e_correlators[i] and e_correlators[i] not in line:
                                continue
                            if lineE == 0:
                                lineE = lineT
                                eeee = pattern
                                problems = 2
                            # No break here, continue checking other patterns on the same line, 
                            # but only the first one found in the file will be reported.
        except Exception as e:
            eeee = f"Error reading file {filename}: {e}"
            problems = 10
    else:
        eeee = f"logfile not found: {filename}"
        problems = 10

    print(eeee)

if __name__ == "__main__":
    main()
