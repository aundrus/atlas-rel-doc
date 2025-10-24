#!/usr/bin/env python3
import os
import sys
import subprocess
import signal

def get_pids(procs, pids_to_check, group_id):
    """
    Recursively find all descendant processes for a given list of PIDs
    within the same process group.
    """
    all_descendants = []
    for pid_to_check in pids_to_check:
        children = []
        for proc in procs:
            if proc['ppid'] == pid_to_check and proc['pgid'] == group_id:
                children.append(proc['pid'])
        
        if children:
            all_descendants.extend(children)
            all_descendants.extend(get_pids(procs, children, group_id))
            
    return all_descendants

def main():
    if len(sys.argv) < 3:
        print("ardoc_kill_fam.py: arguments required: process number(s), signal")
        sys.exit(1)

    try:
        sig = int(sys.argv[-1])
        if not (0 <= sig <= 15):
             raise ValueError
    except ValueError:
        print("ardoc_kill_fam.py: signal (last argument) must be an integer between 0 and 15")
        sys.exit(1)

    proc_numbers_to_kill = []
    for arg in sys.argv[1:-1]:
        try:
            proc_numbers_to_kill.append(int(arg))
        except ValueError:
            print(f"ardoc_kill_fam.py: invalid process number: {arg}")
            continue

    uid = os.getuid()
    
    for procnum in proc_numbers_to_kill:
        print(f"ardoc_kill_fam.py: handling process {procnum} ...")
        
        try:
            output = subprocess.check_output(['ps', '-ww', '-u', str(uid), '-o', 'pid,ppid,pgid,args'], text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running ps: {e}")
            continue

        procs = []
        lines = output.strip().split('\n')
        header = lines[0].strip().split()
        
        group_id = None

        for line in lines[1:]:
            parts = line.strip().split(None, 3)
            if len(parts) < 3:
                continue
            
            pid = int(parts[0])
            ppid = int(parts[1])
            pgid = int(parts[2])
            
            if pid == procnum:
                group_id = pgid

            procs.append({'pid': pid, 'ppid': ppid, 'pgid': pgid})

        if group_id is None:
            print(f"ardoc_kill_fam.py: could not find process {procnum} for user {uid}")
            continue

        pids_to_kill = [procnum]
        descendants = get_pids(procs, pids_to_kill, group_id)
        pids_to_kill.extend(descendants)

        for pid in set(pids_to_kill):
            print(f"ardoc_kill_fam.py: killing {pid} with signal {sig}")
            try:
                os.kill(pid, sig)
            except ProcessLookupError:
                print(f"ardoc_kill_fam.py: process {pid} not found.")
            except PermissionError:
                print(f"ardoc_kill_fam.py: permission denied to kill process {pid}.")
            except Exception as e:
                print(f"ardoc_kill_fam.py: failed to kill process {pid}: {e}")


if __name__ == "__main__":
    main()
