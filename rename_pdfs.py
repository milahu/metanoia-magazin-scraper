#!/usr/bin/env python3

import os
import re
from bs4 import BeautifulSoup

# -----------------------------
# CONFIGURATION
# -----------------------------
HTML_INDEX_FILE = "www.metanoia-magazin.com/einzelausgaben/index.html"
PDF_DIRECTORY = "Metanoia.Magazin.2025-11.Ausgaben.1.bis.69.German.Books"
# -----------------------------


def extract_titles_from_html(html_file):
    """
    Extracts issue numbers and titles from the HTML index file.
    Returns a dict: { "34": "Boombranche Krebs und ihr tumorhaftes Wachstum", ... }
    """
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    title_map = {}

    for a in soup.find_all("a", class_="product-name"):
        title_text = a.get("title") or a.text.strip()

        # FIXME
        # Doppelausgabe 68/69: Marxismus und Zionismus - Doppelschlag gegen den Westen
        # Doppelausgabe 63/64: Alles unter Kontrolle
        # Doppelausgabe 58/59: Israel - Freund und Alliierter?
        # Großausgabe 65: Chinas globaler Vormarsch auf Samtpfoten
        # Neuauflage Doppelausgabe 53/54: Die Sexualisierung unserer Kinder
        # Neuauflage Doppelausgabe 51/52: Digitales Gefängnis
        # Neuauflage Doppelausgabe 45/46: Das Grosse Erwachen vom "Grossen Erwachen"
        # Neuauflage Doppelausgabe 43/44: Massenpsychose
        # Doppelausgabe 41/42: Great Reset: Perestroika-Täuschung 2.0
        # Doppelausgabe 38/39: AIDS als Blaupause für Corona

        # Extract issue number from title ("Ausgabe 34:", "Ausgabe 21:", etc.)
        match = re.search(r"Ausgabe\s+(\d+)", title_text)
        if not match:
            continue

        issue_num = match.group(1)

        cleaned_title = str(title_text)

        # Remove the "Neuauflage Ausgabe XX:" prefix from the title
        cleaned_title = re.sub(r"^Neuauflage\s+Ausgabe\s+\d+:\s*", "", cleaned_title).strip()

        cleaned_title = re.sub(r"^Ausgabe\s+\d+:\s*", "", cleaned_title).strip()

        # Metanoia.Magazin.Ausgabe.12.2017-11 Die traditionelle Familie - Fundament unserer Gesellschaft unter Beschuss von allen Seiten!.pdf
        cleaned_title = cleaned_title.replace("!", ".")

        # Metanoia.Magazin.Ausgabe.18.2018-07 Impfen als Fortschrittsdogma einer modernen Gesellschaft?.pdf
        cleaned_title = cleaned_title.replace("?", ".")

        # Metanoia.Magazin.Ausgabe.13.2017-12 Der unbemerkte Niedergang: Eine Zivilisation gibt sich auf.pdf
        cleaned_title = cleaned_title.replace(":", ".")

        # Metanoia.Magazin.Ausgabe.50.2022-10 China - Der grosse Sprung vom Rei$$brett zur Weltmacht.pdf
        cleaned_title = cleaned_title.replace("$", "s")

        # Metanoia.Magazin.Ausgabe.33.2020-07 Mit der Corona-Diktatur zur «Neuen Normalität».pdf
        cleaned_title = cleaned_title.replace("«", "")
        cleaned_title = cleaned_title.replace("»", "")

        # ndash -> dash
        cleaned_title = cleaned_title.replace("–", "-")

        cleaned_title = re.sub(r"\.{2,}", ".", cleaned_title).strip()

        cleaned_title = cleaned_title.rstrip(".")

        title_map[issue_num] = cleaned_title

    return title_map


def rename_pdfs(pdf_dir, title_map):
    """
    Renames PDF files based on extracted titles.
    """
    for filename in os.listdir(pdf_dir):
        if not filename.lower().endswith(".pdf"):
            continue

        # Match pattern like: Metanoia.Magazin.Ausgabe.34.2020-08.pdf
        match = re.match(r"(Metanoia\.Magazin\.Ausgabe\.(\d+)\.[0-9\-]+)\.pdf$", filename)
        if not match:
            continue

        base_name = match.group(1)
        issue_num = match.group(2)

        if issue_num not in title_map:
            print(f"⚠ No title found for issue {issue_num} (file: {filename})")
            continue

        new_title = title_map[issue_num]
        new_filename = f"{base_name} {new_title}.pdf"

        old_path = os.path.join(pdf_dir, filename)
        new_path = os.path.join(pdf_dir, new_filename)

        print(f"Renaming:\n  {filename}\n→ {new_filename}\n")
        if 1:
            os.rename(old_path, new_path)


def main():
    title_map = extract_titles_from_html(HTML_INDEX_FILE)
    rename_pdfs(PDF_DIRECTORY, title_map)


if __name__ == "__main__":
    main()
