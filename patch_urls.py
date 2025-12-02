#!/usr/bin/env python3

import os
import re
import requests

OLD_PREFIX = "https://www.expresszeitung.com/"
NEW_PREFIX = "https://www.metanoia-magazin.com/"

def resolve_redirect(url):
    """Return the final URL after following all redirects."""
    try:
        r = requests.get(url, allow_redirects=True, timeout=10)
        return r.url
    except Exception as e:
        print(f"[ERROR] Failed to resolve redirect for {url}: {e}")
        return url  # fallback to original


def process_html_file(filepath, cache):
    """Replace URLs in a single HTML file in-place."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r'https://www\.expresszeitung\.com/[^\s"\'<>]*')
    urls = set(pattern.findall(content))

    if not urls:
        # return
        if not re.search(r"expresszeitung\.com", content, flags=re.IGNORECASE):
            return

    print(f"\nProcessing: {filepath}")
    print(f"  Found {len(urls)} URL(s) to patch.")

    for old_url in urls:
        new_candidate = old_url.replace(OLD_PREFIX, NEW_PREFIX)

        # Use cache to avoid repeated HTTP requests
        if new_candidate not in cache:
            print(f"    Resolving redirect: {new_candidate}")
            final_url = resolve_redirect(new_candidate)
            cache[new_candidate] = final_url
        else:
            final_url = cache[new_candidate]

        print(f"    Replacing:\n      {old_url}\n      -> {final_url}")

        content = content.replace(old_url, final_url)

    # case sensitive
    # content = content.replace("expresszeitung.com", "metanoia-magazin.com")

    # case insensitive
    content = re.sub(r"expresszeitung\.com", "metanoia-magazin.com", content, flags=re.IGNORECASE)

    # Write back modified file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def patch_directory(root_dir):
    """Walk the directory recursively and patch all HTML files."""
    redirect_cache = {}

    ext_list = [
        ".html",
        ".txt", # robots.txt
        ".rss", # blog.rss
    ]

    for subdir, _, files in os.walk(root_dir):
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext in ext_list:
                filepath = os.path.join(subdir, filename)
                process_html_file(filepath, redirect_cache)

    print("\n✔️ Done!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python patch_urls.py <directory>")
        exit(1)

    patch_directory(sys.argv[1])
