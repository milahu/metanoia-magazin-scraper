#!/usr/bin/env python3

src_dir = "www.metanoia-magazin.com"

import os
import re
import time
import json
import shlex
import shutil
import asyncio
import subprocess
from pathlib import Path

# pip install packaging
import packaging.version

def get_tar_version():
    try:
        # Run 'tar --version' with LANG=C to ensure consistent output
        result = subprocess.run(
            ["tar", "--version"],
            capture_output=True,
            text=True,
            check=True,
            env={
                "PATH": os.environ["PATH"],
                "LANG": "C",
            }
        )
        # Extract version from the first line
        first_line = result.stdout.split('\n')[0]
        match = re.search(r'tar \(GNU tar\) (\d+\.\d+)', first_line)
        if match:
            return match.group(1)
        else:
            raise ValueError("Could not parse tar version from output")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running tar command: {e.stderr}") from e
    except Exception as e:
        raise RuntimeError(f"Error getting tar version: {str(e)}") from e

def check_min_version(current_version, min_version="1.28"):
    try:
        return packaging.version.parse(current_version) >= packaging.version.parse(min_version)
    except Exception as e:
        raise ValueError(f"Version comparison failed: {str(e)}") from e

def format_date(date_int):
    date_str = str(date_int)
    assert len(date_str) == 8, f"invalid date_str {date_str}"
    return "-".join([
        date_str[0:4], # year
        date_str[4:6], # month
        date_str[6:8], # day
    ])

def parse_date(date_str):
    assert len(date_str) == 10, f"invalid date_str {date_str}" # "2024-03-07"
    return int(date_str.replace("-", "")) # 20240307

async def main():

    # check dependencies
    for bin in ["tar", "pixz"]:
        assert shutil.which(bin), f"please install {bin}"

    # check tar version
    min_tar_version = "1.28"
    try:
        tar_version = get_tar_version()
        # print(f"Found tar version: {tar_version}")
        if check_min_version(tar_version, min_tar_version):
            # print(f"ok: tar version meets minimum requirement {min_tar_version}")
            # return 0
            pass
        else:
            print(f"error: tar version {tar_version} is below minimum requirement {min_tar_version}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

    # print("ok"); return # debug

    # create a reproducible tar archive
    # https://reproducible-builds.org/docs/archives/#full-example
    # https://stackoverflow.com/questions/32997526/how-to-create-a-tar-file-that-omits-timestamps-for-its-contents
    # https://unix.stackexchange.com/questions/438329/tar-produces-different-files-each-time
    temp_tar_path = f"{src_dir}.temp.{time.time()}.tar"
    print(f"creating {temp_tar_path}")
    args = [
        "tar",
        "--sort=name",
        "--mtime=UTC 1970-01-01",
        "--owner=0",
        "--group=0",
        "--numeric-owner",
        "--pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime",
        "-c",
        "-f", temp_tar_path,
        # archive contents
        src_dir,
    ]
    print(">", shlex.join(args))
    t1 = time.time()
    subprocess.run(args)
    t2 = time.time()
    print(f"done in {t2 - t1:.1f} seconds")

    dst_tar_path = f"{src_dir}.tar.xz"
    # use pixz to compress the tar archive
    print(f"creating {dst_tar_path}")
    args = [
        "pixz",
        "-1", # level 1: lowest compression
        "-k", # keep input file
        temp_tar_path,
        dst_tar_path,
    ]
    print(">", shlex.join(args))
    t1 = time.time()
    subprocess.run(args)
    t2 = time.time()
    print(f"done in {t2 - t1:.1f} seconds")

    # by default, pixz keeps the input file
    if 1:
        if os.path.exists(temp_tar_path):
            os.unlink(temp_tar_path)
    else:
        print(f"keeping tempfile {temp_tar_path}")

    print(f"done {dst_tar_path}")

if __name__ == "__main__":
    import sys
    asyncio.run(main())
