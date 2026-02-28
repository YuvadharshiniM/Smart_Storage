"""
CLI Interface for Duplicate File Finder
Command: python find_duplicates.py
"""
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scanner import find_duplicates, count_duplicates, calculate_wasted_space
import config


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def main():
    """Main function to run the duplicate finder."""
    
    # Display header
    print("\n" + "="*60)
    print(" SmartStorage - Duplicate File Finder")
    print("="*60)
    
    # Load file index
    try:
        with open(config.INDEX_FILE_PATH, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        files = index_data.get("files", [])
        
        if not files:
            print("\n[INFO] No files found in index.")
            print("[INFO] Run 'python cli/scan.py <directory>' first to scan files.")
            return
        
        print(f"\n[INFO] Loaded {len(files)} files from index")
        print(f"[INFO] Index file: {config.INDEX_FILE_PATH}\n")
        
    except FileNotFoundError:
        print(f"\n[ERROR] Index file not found: {config.INDEX_FILE_PATH}")
        print("[INFO] Run 'python cli/scan.py <directory>' first to scan files.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"\n[ERROR] Invalid JSON in index file")
        sys.exit(1)
    
    # Find duplicates
    print("[INFO] Analyzing for duplicates...\n")
    
    duplicate_groups = find_duplicates(files)
    stats = count_duplicates(files)
    wasted_space = calculate_wasted_space(files)
    
    # Display summary
    print("-"*60)
    print(" Summary")
    print("-"*60)
    print(f" Total files scanned: {len(files)}")
    print(f" Duplicate groups found: {stats['groups']}")
    print(f" Total duplicate files: {stats['files']}")
    print(f" Wasted space: {format_size(wasted_space)}")
    print("-"*60 + "\n")
    
    # Display duplicate groups
    if duplicate_groups:
        print("="*60)
        print(" Duplicate Files")
        print("="*60 + "\n")
        
        for i, group in enumerate(duplicate_groups, 1):
            print(f"Group {i} ({len(group)} copies):")
            for path in group:
                print(f"  → {path}")
            print()
    else:
        print("[INFO] No duplicate files found! ✓\n")


if __name__ == "__main__":
    main()
