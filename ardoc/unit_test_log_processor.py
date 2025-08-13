#!/usr/bin/env python3

import os
import sys
import shutil
from pathlib import Path

def main():
    """
    Processes a unit test log file to re-categorize certain errors.

    This script is a Python migration of 'unit_test_log_processor.pl'.
    It reads a log file, and when it encounters the line '[ERROR_MESSAGE]',
    it inspects the *next* line. If that line indicates that no tests were
    found, it changes the message type to '[MINOR_WARNING_MESSAGE]'.
    Otherwise, it keeps it as '[ERROR_MESSAGE]'.
    """
    # --- Argument and Environment Validation ---
    if len(sys.argv) != 2:
        print("unit_test_log_processor: Error: one arg req: file name", file=sys.stderr)
        sys.exit(1)

    workspace_path_str = os.environ.get("WORKSPACE")
    if not workspace_path_str:
        print("unit_test_log_processor: Error: WORKSPACE not defined", file=sys.stderr)
        sys.exit(1)

    workspace_path = Path(workspace_path_str)
    if not workspace_path.is_dir():
        print(f"unit_test_log_processor: Error: WORKSPACE {workspace_path_str} does not exist", file=sys.stderr)
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.is_file():
        print(f"unit_test_log_processor: Error: file {file_path} does not exist", file=sys.stderr)
        sys.exit(1)

    # --- File Processing ---
    copy_file_path = workspace_path / f"{file_path.name}_copy"
    print(f"unit_test_log_processor: Info: copy {file_path} {copy_file_path}")

    try:
        # Create a temporary copy to read from
        shutil.copy(file_path, copy_file_path)

        # Read all lines from the copy
        with copy_file_path.open('r', encoding='utf-8', errors='ignore') as f_in:
            lines = f_in.readlines()

        # Open the original file to be overwritten
        with file_path.open('w', encoding='utf-8') as f_out:
            iterator = iter(lines)
            for line in iterator:
                # Using strip() is safer than the Perl script's two-step trim
                if line.strip() == "[ERROR_MESSAGE]":
                    try:
                        # Get the next line, which is the payload of the error
                        next_line = next(iterator)
                        # Check if the payload is the "no tests found" message
                        if "No tests were found" in next_line:
                            f_out.write("[MINOR_WARNING_MESSAGE]\\n")
                            f_out.write(next_line)
                        else:
                            # Otherwise, restore the original error message
                            f_out.write("[ERROR_MESSAGE]\\n")
                            f_out.write(next_line)
                    except StopIteration:
                        # This case handles if [ERROR_MESSAGE] is the last line
                        # The original script would just end, so we do nothing.
                        pass
                else:
                    # If it's not a message marker, write the line as is
                    f_out.write(line)

    except Exception as e:
        print(f"An error occurred during processing: {e}", file=sys.stderr)
    finally:
        # Clean up the temporary copy file
        if copy_file_path.exists():
            copy_file_path.unlink()

if __name__ == "__main__":
    main()
