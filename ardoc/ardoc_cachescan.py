#!/usr/bin/env python3
import os
import sys
import argparse
import re

def main():
    parser = argparse.ArgumentParser(description='ARDOC Cache Scanner')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--def_section', metavar='SECTION', help='Define section')
    group.add_argument('-c', '--com_section', metavar='SECTION', help='Command section')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-f', '--files', nargs='+', required=True, help='Input cache files')

    args = parser.parse_args()

    opt = "def" if args.def_section else "com"
    section = args.def_section if args.def_section else args.com_section
    
    output_file = args.output if args.output else os.path.join(os.environ.get("ARDOC_WORK_AREA", "."), "cache_scan_result")

    if not section:
        print("ardoc_cachescan.py: error: a section must be provided with -c or -d", file=sys.stderr)
        sys.exit(1)

    sect = re.sub(r'\s+', ' ', section)

    with open(output_file, 'w') as tf:
        for file_path in args.files:
            if not os.path.isfile(file_path):
                continue

            with open(file_path, 'r') as fr:
                lines = fr.readlines()

            in_section = False
            in_bypass = False
            for line in lines:
                line = line.strip()
                line_low = line.lower()
                
                if opt == "com":
                    # Check for section boundaries
                    if line_low.startswith('<') and not line_low.startswith('</bypass') and not line_low.startswith('<bypass'):
                        if in_section:
                            if in_bypass:
                                tf.write("fi\n")
                                in_bypass = False
                            break # End of the current section
                    
                    if in_section:
                        if line_low.startswith('<bypass'):
                            in_bypass = True
                            tf.write('if [ "${ARDOC_BYPASS}" != "yes" ]; then :;\n')
                            continue
                        if line_low.startswith('</bypass'):
                            if in_bypass:
                                tf.write("fi\n")
                            in_bypass = False
                            continue

                        # Process line content
                        if (re.search(r'=', line_low) and 
                            'source' not in line_low and 
                            'cmt' not in line and 
                            'echo' not in line_low and 
                            'broadcast' not in line_low and 
                            not line_low.startswith('if') and 
                            not line_low.startswith(':') and 
                            not line_low.startswith('make') and 
                            not re.match(r'fi[^a-zA-Z0-9]', line_low) and 
                            not re.match(r'stat=', line_low) and 
                            not line_low.startswith('#')):
                            tf.write(f"export {line}\n")
                        elif (line_low.startswith('cmtprojectpath=') or 
                              line_low.startswith('cmtroot=') or 
                              line_low.startswith('cmtpath=')):
                            tf.write(f"export {line}\n")
                        else:
                            if line: # non-empty line
                                tf.write(f"{line}\n")

                    if line.startswith(f"<{sect}"):
                        in_section = True

                elif opt == "def":
                    if line.startswith(f"<{sect}"):
                        line_content = re.sub(r'[<>]', '', line)
                        line_content = re.sub(r'^\s*' + re.escape(sect) + r'\s*', '', line_content, flags=re.IGNORECASE)
                        variables = line_content.split()
                        for var in variables:
                            tf.write(f"{var}\n")

if __name__ == "__main__":
    main()
