#!/usr/bin/env python3
import os
import sys
import subprocess
import re

def main():
    """
    Creates a project suffix based on environment variables, primarily ARDOC_ARCH.
    This is a Python migration of the ardoc_project_suffix_creator.pl script.
    """
    # --- Get Environment Variables ---
    ardoc_suffix_prepend = os.environ.get("ARDOC_SUFFIX_PREPEND", "")
    ardoc_arch = os.environ.get("ARDOC_ARCH", "")
    ardoc_project_name = os.environ.get("ARDOC_PROJECT_NAME", "")
    ardoc_home = os.environ.get("ARDOC_HOME", "")

    # --- Get Short Name from Translator Script ---
    short_name = ""
    if ardoc_home and ardoc_project_name:
        translator_script = os.path.join(ardoc_home, 'ardoc_project_translator.py')
        try:
            result = subprocess.run(
                ['python', translator_script, ardoc_project_name],
                capture_output=True,
                text=True,
                check=True
            )
            short_name = result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            # If the script fails or is not found, proceed with an empty short_name
            # This mimics the original script's behavior of not handling the error.
            pass

    fields = ardoc_arch.split('-')

    # --- Determine Machine Architecture ---
    machine = ""
    for field in fields:
        if "i686" in field or "ia32" in field:
            machine = "32B"
            break
        if "x86_64" in field or "amd64" in field:
            machine = "64B"
            break

    # --- Determine OS and Compiler ---
    opsyst = ""
    os_map = {
        "slc3": "S3", "slc4": "S4", "slc5": "S5", "slc6": "S6",
        "cc7": "C7", "centos7": "C7", "el9": "E9", "centos9": "C9",
        "mac104": "M104", "mac105": "M105", "mac106": "M106",
        "mac107": "M107", "mac108": "M108", "mac109": "M109",
        "mac1010": "M1010"
    }
    for field in fields:
        if field in os_map:
            opsyst = os_map[field]
            break

    # --- Determine GCC Version ---
    gcc_map = {
        "gcc46": "G46", "gcc47": "G47", "gcc48": "G48", "gcc49": "G49",
        "gcc45": "G45", "gcc4": "G4", "gcc61": "G61", "gcc62": "G62",
        "gcc8": "G8", "gcc9": "G9", "gcc10": "G10", "gcc11": "G11",
        "gcc12": "G12", "gcc13": "G13"
    }
    for field in fields:
        if field in gcc_map:
            opsyst += gcc_map[field]
            break

    # --- Determine ICC ---
    for field in fields:
        if "icc" in field:
            opsyst += "IC"
            break
            
    # --- Determine Clang Version ---
    clang_patterns = {
        r'^.*clang3[0-6].*$': "C3",
        r'^.*clang37.*$': "C37",
        r'^.*clang38.*$': "C38",
        r'^.*clang39.*$': "C39",
        r'^.*clang5.*$': "C5",
        r'^.*clang6.*$': "C6",
        r'^.*clang7.*$': "C7",
        r'^.*clang8.*$': "C8",
        r'^.*clang9.*$': "C9",
        r'^.*clang10.*$': "C10",
    }
    for field in fields:
        found_clang = False
        for pattern, code in clang_patterns.items():
            if re.match(pattern, field):
                opsyst += code
                found_clang = True
                break
        if found_clang:
            break

    # --- Determine LLVM ---
    for field in fields:
        if "llvm" in field:
            opsyst += "VM"
            break

    # --- Determine Build Type (Opt/Dbg) ---
    opt = ""
    for field in fields:
        if "opt" in field:
            opt = "Opt"
            break
        if "dbg" in field:
            opt = "Dbg"
            break

    # --- Print Final Suffix ---
    final_suffix = f"{ardoc_suffix_prepend}{machine}{opsyst}{short_name}{opt}"
    sys.stdout.write(final_suffix)

if __name__ == "__main__":
    main()
