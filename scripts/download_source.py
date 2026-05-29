#!/usr/bin/env python3
"""Download and import selected sources from discovery results."""
import sys
import json
import os
import re
import urllib.request
import time

DATA_DIR = os.path.expanduser("~/pi-cwd-20260526/notebooklm_data")
SOURCES_DIR = os.path.join(DATA_DIR, "sources")
PENDING_FILE = os.path.join(DATA_DIR, "pending_imports.json")

def download_file(url, dest_path):
    """Download file from URL to dest_path."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=30) as response:
            with open(dest_path, 'wb') as f:
                f.write(response.read())
        return True, None
    except Exception as e:
        return False, str(e)

def write_pending_imports(new_sources, notebook_id):
    """Write pending imports to JSON file, appending to existing entries."""
    pending_entry = {
        "notebook_id": notebook_id,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total": len(new_sources),
        "sources": new_sources
    }

    # Check if file exists
    existing = []
    if os.path.exists(PENDING_FILE):
        try:
            with open(PENDING_FILE, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing = []

    # Merge: append new sources, deduplicate by filepath
    existing_sources = existing.get("sources", []) if isinstance(existing, dict) else existing
    existing_filepaths = {s.get("filepath") for s in existing_sources if isinstance(s, dict)}

    for new_src in new_sources:
        if new_src.get("filepath") not in existing_filepaths:
            existing_sources.append(new_src)

    # Write back
    merged = {
        "notebook_id": notebook_id,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total": len(existing_sources),
        "sources": existing_sources
    }

    try:
        with open(PENDING_FILE, 'w', encoding='utf-8') as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Failed to write pending_imports.json: {e}", file=sys.stderr)

    return PENDING_FILE

def import_sources(indices_str, discover_json, notebook_id="default"):
    """Import selected sources by index."""
    indices = [int(x.strip()) for x in indices_str.split(",")]
    discover_data = json.loads(discover_json)
    sources = discover_data.get("sources", [])

    notebook_sources_dir = os.path.join(SOURCES_DIR, notebook_id)
    os.makedirs(notebook_sources_dir, exist_ok=True)

    imported = []
    failed = []

    for idx in indices:
        source = next((s for s in sources if s.get("id") == idx), None)
        if not source:
            failed.append({"index": idx, "reason": "Not found in discovery results"})
            continue

        url = source.get("url", "")
        title = source.get("title", "untitled")
        file_type = source.get("type", "webpage")

        safe_title = re.sub(r'[^\w\s-]', '', title)[:50].strip()
        ext = ".pdf" if file_type == "pdf" else ".html"
        filename = f"{safe_title}{ext}"
        filepath = os.path.join(notebook_sources_dir, filename)

        counter = 1
        while os.path.exists(filepath):
            filename = f"{safe_title}_{counter}{ext}"
            filepath = os.path.join(notebook_sources_dir, filename)
            counter += 1

        print(f"Downloading [{idx}]: {title}", file=sys.stderr)
        success, error = download_file(url, filepath)

        if success:
            imported.append({
                "index": idx,
                "title": title,
                "filename": filename,
                "filepath": filepath,
                "type": file_type,
                "url": url,
                "status": "pending_import",
                "notebook_id": notebook_id
            })
            print(f"Downloaded: {filename}", file=sys.stderr)
        else:
            failed.append({"index": idx, "title": title, "reason": error})
            print(f"Failed: {title} - {error}", file=sys.stderr)

        time.sleep(0.5)

    # Write to pending_imports.json
    pending_path = None
    if imported:
        pending_path = write_pending_imports(imported, notebook_id)

    return {
        "imported_count": len(imported),
        "failed_count": len(failed),
        "imported": imported,
        "failed": failed,
        "notebook_id": notebook_id,
        "pending_imports_path": pending_path
    }

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    indices = sys.argv[1] if len(sys.argv) > 1 else "1"
    discover_json = sys.argv[2] if len(sys.argv) > 2 else "{}"
    notebook_id = sys.argv[3] if len(sys.argv) > 3 else "default"

    result = import_sources(indices, discover_json, notebook_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))