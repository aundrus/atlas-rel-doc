#!/usr/bin/env python3

#
# ARDOC - NIghtly COntrol System
# Author Alex Undrus <undrus@bnl.gov>
#
# ----------------------------------------------------------
# ardoc_cachescan.py - Python migration of ardoc_cachescan.pl
# ----------------------------------------------------------
import os
import sys
import argparse

def main():
    """
    Main function to scan ardoc_cache files.
    """
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Scan ardoc_cache files for specific sections.")
    
    # Output file
    parser.add_argument(
        "-o", "--output",
        default=os.path.join(os.environ.get("ARDOC_WORK_AREA", "."), "cache_scan_result"),
        help="Output file path. Defaults to $ARDOC_WORK_AREA/cache_scan_result"
    )
    
    # Input files
    parser.add_argument(
        "-f", "--files",
        action="append",
        required=True,
        help="An ardoc_cache file to scan. This option can be specified multiple times."
    )

    # Mutually exclusive group for -c and -d
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--com", dest="section_com", help="Extract commands from the specified section.")
    group.add_argument("-d", "--def", dest="section_def", help="Extract definitions from the specified section.")

    args = parser.parse_args()

    # Determine mode and section
    if args.section_com:
        mode = "com"
        section = args.section_com
    else:
        mode = "def"
        section = args.section_def

    # --- File Processing ---
    try:
        with open(args.output, 'w') as outfile:
            for filepath in args.files:
                if not os.path.isfile(filepath):
                    continue

                with open(filepath, 'r') as infile:
                    lines = infile.readlines()

                in_section = False
                in_bypass = False
                
                for line in lines:
                    # Clean up the line
                    line = line.strip()
                    line_low = line.lower()
                    
                    if mode == "com":
                        # --- Command Extraction Logic ---
                        if line.startswith(f"<{section}"):
                            in_section = True
                            continue

                        if not in_section:
                            continue

                        # Check for end of section
                        if line_low.startswith('<') and not line_low.startswith('</bypass'):
                            break
                        
                        if line_low.startswith('<bypass'):
                            in_bypass = True
                            outfile.write("if [ \"${ARDOC_BYPASS}\" != \"yes\" ]; then :;\n")
                            continue
                        
                        if line_low.startswith('</bypass'):
                            in_bypass = False
                            outfile.write("fi\n")
                            continue

                        # Process line content
                        line_low_no_space = line_low.replace(" ", "")
                        
                        # Keywords to exclude from automatic export
                        exclude_keywords = ['source', 'cmt', 'echo', 'broadcast', 'stat=']
                        exclude_prefixes = ['if', ':', 'make', '#']
                        
                        is_excluded = any(kw in line_low for kw in exclude_keywords) or \
                                      any(line_low.startswith(p) for p in exclude_prefixes) or \
                                      line_low.startswith('fi[^a-zA-Z0-9]')

                        if '=' in line_low and not is_excluded:
                            outfile.write(f"export {line}\n")
                        elif line_low.startswith("cmtprojectpath=") or \
                             line_low.startswith("cmtroot=") or \
                             line_low.startswith("cmtpath="):
                            outfile.write(f"export {line}\n")
                        else:
                            if line: # Write non-empty lines
                                outfile.write(f"{line}\n")

                    elif mode == "def":
                        # --- Definition Extraction Logic ---
                        if line.startswith(f"<{section}"):
                            # Remove <section ... > tags
                            clean_line = line.replace('<', '').replace('>', '').strip()
                            # Remove section name itself
                            clean_line = clean_line.replace(section, '', 1).strip()
                            
                            parts = clean_line.split()
                            for part in parts:
                                if part:
                                    outfile.write(f"{part}\n")

    except IOError as e:
        sys.stderr.write(f"ardoc_cachescan.py: error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    if not os.environ.get("ARDOC_WORK_AREA"):
        sys.stderr.write("ardoc_cachescan.py: error: ARDOC_WORK_AREA environment variable is not set.\n")
        # Allow to proceed for basic testing, but it might fail on default output
    main()
