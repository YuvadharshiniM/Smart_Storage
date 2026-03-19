"""
CLI Interface for SmartStorage - Full System Scan
Command: python cli/scan.py

Automatically scans all available drives on the system,
finds duplicate files, and reports wasted space.
No path argument needed.
"""
import sys
import json
import os
import string
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scanner import FileScanner
from scanner.duplicate_finder import find_duplicates, count_duplicates, calculate_wasted_space
import config


def format_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_all_drives() -> list:
    """Return a list of all accessible drive root paths on Windows, excluding C:\\."""
    drives = []
    for letter in string.ascii_uppercase:
        if letter.upper() == 'C':
            continue  # Skip C drive (system drive)
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives


def print_progress(message: str):
    print(f"  [INFO] {message}")


def save_index_to_json(files_data: list):
    os.makedirs(os.path.dirname(config.INDEX_FILE_PATH), exist_ok=True)
    index_data = {
        "total_files": len(files_data),
        "files": files_data
    }
    with open(config.INDEX_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)


def main():
    print("\n" + "=" * 60)
    print("  SmartStorage - Full System Duplicate Scanner")
    print("=" * 60)

    # Detect all drives
    drives = get_all_drives()
    print(f"\n  Drives found: {', '.join(drives)}")
    print("  Scanning entire system — this may take a while...\n")

    all_files = []
    scanner = FileScanner()

    for drive in drives:
        print(f"  Scanning {drive}")
        print("-" * 60)
        try:
            files = scanner.scan_directory(drive, progress_callback=print_progress)
            all_files.extend(files)
            print(f"  -> {len(files)} files found on {drive}\n")
        except Exception as e:
            print(f"  [WARN] Could not fully scan {drive}: {e}\n")

    # Summary of scan
    print("=" * 60)
    print(f"  Total files scanned across all drives: {len(all_files)}")
    if all_files:
        total_size = sum(f.get('size', 0) for f in all_files)
        print(f"  Total size of all files: {format_size(total_size)}")
    print("=" * 60)

    # Save index
    print("\n  Saving file index...")
    save_index_to_json(all_files)

    # Find duplicates
    print("  Analyzing for duplicates...\n")
    duplicate_groups = find_duplicates(all_files)
    stats = count_duplicates(all_files)
    wasted_space = calculate_wasted_space(all_files)

    # Duplicate summary
    print("=" * 60)
    print("  Duplicate Report")
    print("=" * 60)
    print(f"  Duplicate groups : {stats['groups']}")
    print(f"  Duplicate files  : {stats['files']}")
    print(f"  Space saveable   : {format_size(wasted_space)}")
    print("=" * 60 + "\n")

    if not duplicate_groups:
        print("  No duplicate files found! Your system is clean.\n")
        return

    # Detailed duplicate groups
    # Build a size lookup for saveable space per group
    hash_to_size = {}
    for f in all_files:
        h = f.get('hash')
        if h and h not in hash_to_size:
            hash_to_size[h] = f.get('size', 0)

    # Rebuild groups with file names for display
    hash_groups_full = {}
    for f in all_files:
        h = f.get('hash')
        if not h:
            continue
        if h not in hash_groups_full:
            hash_groups_full[h] = []
        hash_groups_full[h].append(f)

    dup_entries = [v for v in hash_groups_full.values() if len(v) > 1]

    for i, group in enumerate(dup_entries, 1):
        count = len(group)
        file_size = group[0].get('size', 0)
        saveable = format_size((count - 1) * file_size)
        print(f"  Group {i}  |  {count} identical files  |  Save {saveable}")
        print(f"  {'─' * 54}")
        for j, f in enumerate(group):
            marker = "  KEEP  " if j == 0 else "  DUPE  "
            name = os.path.basename(f.get('path', ''))
            path = f.get('path', '')
            print(f"  [{marker}] {name}")
            print(f"           {path}")
        print()

    print("=" * 60)
    print("  Scan complete.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
