#!/usr/bin/env python3

import os
import re
import shutil
import pdftotext

INPUT_DIR = "Metanoia.Magazin.Ausgaben.1.bis.69"
OUTPUT_DIR = INPUT_DIR

# German month name → number
MONTHS = {
    "januar": "01",
    "februar": "02",
    "märz": "03",
    "maerz": "03",  # fallback without umlaut
    "april": "04",
    "mai": "05",
    "juni": "06",
    "juli": "07",
    "august": "08",
    "september": "09",
    "oktober": "10",
    "november": "11",
    "dezember": "12",
}

def extract_first_page_text(pdf_path):
    """Return text of first page using python-pdftotext."""
    with open(pdf_path, "rb") as f:
        pdf = pdftotext.PDF(f)
    return pdf[0]


def extract_date_from_text(text):
    """
    Find the line containing 'Ausgabe' and parse date from it.
    Supports formats like:
      'Ausgabe 3, Januar 2017'
      'Ausgabe Nr. 17 / Mai 2018'
      'Ausgabe 21 | 2018'
    """

    # get first line containing "Ausgabe"
    line = None
    for l in text.splitlines():
        if "Ausgabe" in l:
            line = l.strip()
            break
    if not line:
        raise ValueError("No 'Ausgabe' line found")

    # Normalize text for easier matching
    clean = line.lower().replace("nr.", "").replace("|", " ").replace("/", " ")

    # Try extracting a month + year
    month = None
    year = None

    # Match "Mai 2018" or "Januar 2017"
    m = re.search(r"(\b[a-zäöü]+)\s+(\d{4})", clean)
    if m:
        month_name = m.group(1)
        year = m.group(2)
        month = MONTHS.get(month_name)
        if month:
            return year, month

    # # Some issues may have only the year ("Ausgabe 21 | 2018")
    # # → Cannot deduce month: default to "01"
    # m = re.search(r"\b(\d{4})\b", clean)
    # if m:
    #     year = m.group(1)
    #     month = "01"
    #     return year, month

    raise ValueError(f"Could not parse date from line: {line}")


def process_pdf(pdf_path):
    """Extract date and build new filename."""
    basename = os.path.basename(pdf_path)

    # Extract text from first page
    text = extract_first_page_text(pdf_path)

    # Extract date (year, month)
    year, month = extract_date_from_text(text)

    # Insert date before ".pdf"
    name_no_ext = basename[:-4]
    new_name = f"{name_no_ext}.{year}-{month}.pdf"

    return new_name


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in os.listdir(INPUT_DIR):
        if not filename.lower().endswith(".pdf"):
            continue

        source_path = os.path.join(INPUT_DIR, filename)
        try:
            new_name = process_pdf(source_path)
        except Exception as e:
            print(f"ERROR parsing {filename}: {e}")
            continue

        dest_path = os.path.join(OUTPUT_DIR, new_name)
        if source_path != dest_path:
            print(f"→ {filename}  →  {new_name}")
            shutil.move(source_path, dest_path)


if __name__ == "__main__":
    main()
