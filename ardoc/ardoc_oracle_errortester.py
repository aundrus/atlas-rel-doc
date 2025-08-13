#!/usr/bin/env python3

import sys
from pathlib import Path

def find_first_error(filename: str) -> tuple[str, int]:
    """
    Scans a log file for a predefined set of error patterns.

    This function mimics the core logic of the original ardoc_oracle_errortester.pl script.
    It searches for the first occurrence of an error, respecting ignore patterns and
    correlator patterns.

    Args:
        filename: The path to the log file to scan.

    Returns:
        A tuple containing:
        - The string of the first error pattern found (or an error message).
        - A problem code (0 for success, 2 for errors found, 10 for file not found).
    """
    # Configuration of patterns to search for, ignore, and correlate
    e_patterns = ("ORA-", "permission denied", "Disk quota exceeded", ": Error:", "CVBFGG")
    e_ignore = ("CVBFGH", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG")
    e_correlators = ("", "", "", "ardoc", "")
    
    first_error_message = ""
    problems = 0

    file_path = Path(filename)
    if not file_path.is_file():
        first_error_message = f"logfile not found: {filename}"
        problems = 10
        return first_error_message, problems

    try:
        with file_path.open('r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                for i, pattern in enumerate(e_patterns):
                    # A line matches if:
                    # 1. It contains the error pattern.
                    # 2. It does NOT contain the corresponding ignore pattern.
                    # 3. If a correlator exists, the line must also contain it.
                    if (pattern in line and 
                        e_ignore[i] not in line and
                        (not e_correlators[i] or e_correlators[i] in line)):
                        
                        # This is the first error found in the file.
                        # Capture the pattern and problem code.
                        first_error_message = pattern
                        problems = 2
                        # Return immediately, as we only care about the first error.
                        return first_error_message, problems
    except Exception as e:
        # Handle potential read errors, though open with errors='ignore' is robust.
        first_error_message = f"Error reading file {filename}: {e}"
        problems = 10 # Use the same code as file not found for general file issues
        return first_error_message, problems
    
    # If the loop completes without finding any errors
    return first_error_message, problems

def main():
    """
    Main function to handle command-line arguments and orchestrate the error scan.
    """
    # The original script requires exactly one argument.
    if len(sys.argv) != 2:
        print("ardoc_oracle_errortester:", file=sys.stderr)
        print("One argument required: name of logfile", file=sys.stderr)
        sys.exit(2)

    filename = sys.argv[1]
    
    # Get the first error message found in the file.
    error_message, _ = find_first_error(filename)
    
    # The original script prints the result to standard output without a newline.
    sys.stdout.write(error_message)
    
    # The original script doesn't have an explicit exit code here, but 0 is standard.
    sys.exit(0)

if __name__ == "__main__":
    main()
