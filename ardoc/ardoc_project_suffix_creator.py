#!/usr/bin/env python3
import os
import re

def main():
    ardoc_suffix_prepend = os.environ.get("ARDOC_SUFFIX_PREPEND", "")
    ardoc_arch = os.environ.get("ARDOC_ARCH", "")
    ardoc_project_name = os.environ.get("ARDOC_PROJECT_NAME", "")

    full_name = ardoc_project_name
    fields = ardoc_arch.split('-')

    machine = ""
    for field in fields:
        if "i686" in field or "ia32" in field:
            machine = "32B"
            break
        if "x86_64" in field or "amd64" in field:
            machine = "64B"
            break
        if "aarch64" in field:
            machine = "ARM64B"
            break

    opsyst = ""
    os_map = {
        "slc3": "S3", "slc4": "S4", "slc5": "S5", "slc6": "S6",
        "cc7": "C7", "centos7": "C7", "centos9": "C9", "el9": "E9",
        "mac104": "M104", "mac105": "M105", "mac106": "M106",
        "mac107": "M107", "mac108": "M108", "mac109": "M109",
        "mac1010": "M1010"
    }
    for field in fields:
        for key, value in os_map.items():
            if key in field:
                opsyst = value
                break
        if opsyst:
            break

    compiler_map = {
        "gcc46": "G46", "gcc47": "G47", "gcc48": "G48", "gcc49": "G49",
        "gcc45": "G45", "gcc4": "G4", "gcc61": "G61", "gcc62": "G62",
        "gcc8": "G8", "gcc9": "G9", "gcc10": "G10", "gcc11": "G11",
        "gcc12": "G12", "gcc13": "G13", "gcc14": "G14", "gcc15": "G15"
    }
    for field in fields:
        found = False
        for key, value in compiler_map.items():
            if key in field:
                opsyst += value
                found = True
                break
        if found:
            break

    for field in fields:
        if "icc" in field:
            opsyst += "IC"
            break
            
    clang_map = {
        r".*clang3[0-6].*": "C3",
        r".*clang37.*": "C37", r".*clang38.*": "C38", r".*clang39.*": "C39",
        r".*clang5.*": "C5", r".*clang6.*": "C6", r".*clang7.*": "C7",
        r".*clang8.*": "C8", r".*clang9.*": "C9", r".*clang10.*": "C10",
        r".*clang15.*": "C15", r".*clang16.*": "C16", r".*clang17.*": "C17",
        r".*clang18.*": "C18", r".*clang19.*": "C19", r".*clang20.*": "C20"
    }
    for field in fields:
        found = False
        for pattern, value in clang_map.items():
            if re.match(pattern, field):
                opsyst += value
                found = True
                break
        if found:
            break

    for field in fields:
        if "llvm" in field:
            opsyst += "VM"
            break

    opt = ""
    for field in fields:
        if "opt" in field:
            opt = "Opt"
            break
        if "dbg" in field:
            opt = "Dbg"
            break

    print(f"{ardoc_suffix_prepend}{machine}{opsyst}{full_name}{opt}", end='')

if __name__ == "__main__":
    main()
