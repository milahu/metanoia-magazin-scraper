#!/usr/bin/env python3

import os
import re
from urllib.parse import urlparse, urljoin, urlunparse, unquote

BASE_URL = "https://www.metanoia-magazin.com/"
ROOT_DIR = "www.metanoia-magazin.com"

# Regex for absolute links
# ABS_LINK_RE = re.compile(r'href="(https://www\.metanoia-magazin\.com/[^"]*)"')
# ABS_LINK_RE = re.compile(r'''["'](https://www\.metanoia-magazin\.com/[^"]*)["']''')
ABS_LINK_RE = re.compile(r'''(https://www\.metanoia-magazin\.com/[^"'\s]*)''')


def file_exists_for_url_path(url_path):
    """
    Given a URL path like '/jahresabo/ez-ab-10001.3',
    try to find the local file under ROOT_DIR.

    Tries the following in order:
    1. ROOT_DIR/path
    2. ROOT_DIR/path.html
    3. ROOT_DIR/path/index.html
    """
    url_path = url_path.lstrip("/")
    base = os.path.join(ROOT_DIR, url_path)

    # 1. Exact match
    if os.path.isfile(base):
        return base

    # 2. Try .html
    if not base.endswith(".html"):
        candidate_html = base + ".html"
        if os.path.isfile(candidate_html):
            return candidate_html

    # 3. Directory with index.html
    candidate_index = os.path.join(base, "index.html")
    if os.path.isfile(candidate_index):
        return candidate_index

    return None


def make_relative(from_file, to_file):
    """
    Compute the correct relative path from from_file → to_file.
    """
    from_dir = os.path.dirname(from_file)
    rel = os.path.relpath(to_file, start=from_dir)
    return rel


def process_file(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()

    modified = content
    changes = []

    for match in ABS_LINK_RE.finditer(content):
        abs_url = match.group(1)
        parsed = urlparse(abs_url)
        url_path = unquote(parsed.path)

        local_target = file_exists_for_url_path(url_path)
        if not local_target:
            # Target file does not exist — skip.
            continue

        # Compute relative link
        rel_link = make_relative(html_file, local_target)

        # Ensure .html suffix in the URL if it's missing
        if not rel_link.endswith(".html"):
            rel_link += ".html"

        old = abs_url
        new = rel_link

        changes.append((old, new))
        # modified = modified.replace(f'href="{old}"', f'href="{new}"')
        modified = modified.replace(old, new)

    if changes:
        print(f"[UPDATED] {html_file}")
        for old, new in changes:
            print(f"  {old}  →  {new}")

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(modified)


def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        for filename in files:
            if filename.endswith(".html"):
                full_path = os.path.join(root, filename)
                process_file(full_path)


if __name__ == "__main__":
    main()
