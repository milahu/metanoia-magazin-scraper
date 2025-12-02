#!/usr/bin/env python3

# Create a reproducible RAR archive

import os
import subprocess
import time
import shlex
import argparse
from pathlib import Path

EPOCH = 0  # Jan 1 1970

def list_files_sorted(src_dir):
    """Return all files under src_dir sorted by POSIX path for reproducibility."""
    src_dir = Path(src_dir)
    files = []
    for path in src_dir.rglob('*'):
        if path.is_file():
            files.append(path)
    # Sort by POSIX string so it's 100% deterministic on all platforms
    files.sort(key=lambda p: p.as_posix())
    return files

def set_mtime(path, ts):
    """Set atime and mtime to ts."""
    os.utime(path, (ts, ts))

def main():
    parser = argparse.ArgumentParser(description="Create a reproducible RAR archive")
    parser.add_argument("dst", help="Destination RAR file")
    parser.add_argument("src", help="Source directory")
    parser.add_argument("--volsize", default="1G", help="Volume size (default 1G)")
    args = parser.parse_args()

    src = Path(args.src).resolve()
    dst = Path(args.dst).resolve()

    # Step 1: Collect files sorted
    files = list_files_sorted(src)

    # # Step 2: Save real timestamps
    # original_times = {}
    # for f in files:
    #     st = f.stat()
    #     original_times[f] = (st.st_atime, st.st_mtime)

    try:
        # Step 3: Normalize timestamps to epoch for reproducibility
        for f in files:
            set_mtime(f, EPOCH)

        # Step 4: Create archive using explicit file list in sorted order
        # RAR accepts file lists via stdin with '@-'
        # args = ["rar", "a", f"-v{args.volsize}", dst.as_posix(), "@-"] # error: Cannot open -
        args = ["rar", "a", f"-v{args.volsize}", dst.as_posix(), "@/dev/stdin"]
        print(">", shlex.join(args))
        proc = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            text=True
        )
        for f in files:
            # proc.stdin.write(f.relative_to(src).as_posix() + "\n") # error: No such file or directory
            proc.stdin.write(f.as_posix() + "\n")
        proc.stdin.close()
        proc.wait()

        if proc.returncode != 0:
            raise RuntimeError("rar returned an error")

        print("done", dst)

    finally:
        # # Step 5: Restore original timestamps
        # for f, (at, mt) in original_times.items():
        #     os.utime(f, (at, mt))
        pass

if __name__ == "__main__":
    main()
