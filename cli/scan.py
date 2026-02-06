"""
CLI Interface for File Scanner
Command: python scan.py <directory_path>
"""
import sys
import json
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scanner import FileScanner
import config


def print_progress(message: str):
    """Print progress messages to the console."""
    print(f"[INFO] {message}")


def save_index_to_json(files_data: list, output_path: str):
    """
    Save the file index to a JSON file.
    
    Args:
        files_data (list): List of file information dictionaries
        output_path (str): Path to save the JSON file
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create the index structure
    index_data = {
        "total_files": len(files_data),
        "files": files_data
    }
    
    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print_progress(f"Index saved to: {output_path}")


def main():
    """Main function to run the CLI scanner."""
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python scan.py <directory_path>")
        print("Example: python scan.py C:\\Users\\YourName\\Documents")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    
    # Display header
    print("\n" + "="*60)
    print(" SmartStorage - File Scanner")
    print("="*60)
    print(f"Target Directory: {directory_path}\n")
    
    try:
        # Initialize scanner
        scanner = FileScanner()
        
        # Start scanning with progress callback
        print_progress("Scanning...")
        files = scanner.scan_directory(directory_path, progress_callback=print_progress)
        
        # Display summary
        print("\n" + "-"*60)
        print(f" Scan Summary")
        print("-"*60)
        print(f" Total files found: {len(files)}")
        
        if len(files) > 0:
            total_size = sum(f['size'] for f in files)
            print(f" Total size: {format_size(total_size)}")
        
        print("-"*60 + "\n")
        
        # Save to JSON
        print_progress("Saving index to JSON...")
        save_index_to_json(files, config.INDEX_FILE_PATH)
        
        print_progress("Scan completed successfully!")
        
    except ValueError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        sys.exit(1)


def format_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


if __name__ == "__main__":
    main()
