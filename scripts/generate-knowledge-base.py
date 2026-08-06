#!/usr/bin/env python3
"""Generate a deterministic JSON artifact from the committed knowledge base.

This script is used at development/build time to turn the source PDF, DOCX, and
Markdown files in knowledge_base/ into a single text-based artifact consumed by
the Next.js application. The original binary files are never modified.
"""

import glob
import json
import os
import sys
from datetime import datetime, timezone

from PyPDF2 import PdfReader
from docx import Document


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(ROOT_DIR, "knowledge_base")
OUTPUT_PATH = os.path.join(ROOT_DIR, "src", "data", "knowledge-base.json")


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    text_parts = [paragraph.text for paragraph in doc.paragraphs]
    return "\n".join(text_parts)


def main() -> int:
    entries = []
    failures = []

    file_paths = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.*")))
    if not file_paths:
        print(f"ERROR: No knowledge-base files found in {SOURCE_DIR}", file=sys.stderr)
        return 1

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        text = ""

        try:
            if file_ext == ".md":
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            elif file_ext == ".pdf":
                text = extract_text_from_pdf(file_path)
            elif file_ext == ".docx":
                text = extract_text_from_docx(file_path)
            else:
                failures.append(f"Unsupported file type {file_ext} for {file_name}")
                continue
        except Exception as e:
            failures.append(f"Error processing {file_name}: {e}")
            continue

        if not text.strip():
            failures.append(
                f"No text extracted from {file_name}; the document may be empty or use an unsupported format"
            )
            continue

        entries.append({
            "fileName": file_name,
            "text": text,
        })

    if failures:
        for failure in failures:
            print(f"WARNING: {failure}", file=sys.stderr)

    if not entries:
        print("ERROR: No knowledge-base entries could be extracted", file=sys.stderr)
        return 1

    artifact = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceDirectory": "knowledge_base",
        "entryCount": len(entries),
        "entries": entries,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(artifact, f, ensure_ascii=False, indent=2)

    total_chars = sum(len(entry["text"]) for entry in entries)
    print(f"Generated {OUTPUT_PATH}")
    print(f"  Entries: {len(entries)}")
    print(f"  Total characters: {total_chars}")
    if failures:
        print(f"  Warnings: {len(failures)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
