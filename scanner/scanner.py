"""
File Scanner Module
Handles recursive directory scanning and file indexing.
"""
import os
from pathlib import Path
from typing import List, Dict

from .hash_utils import generate_file_hash


class FileScanner:
    """Scanner class for recursively scanning directories and collecting file information."""
    
    def __init__(self):
        self.scanned_files = []
    
    def scan_directory(self, directory_path: str, progress_callback=None) -> List[Dict[str, any]]:
        """
        Recursively scan a directory and collect file information.
        
        Args:
            directory_path (str): Path to the directory to scan
            progress_callback (callable, optional): Callback function to report progress
            
        Returns:
            List[Dict]: List of dictionaries containing file information
        """
        self.scanned_files = []
        
        # Validate directory
        path = Path(directory_path)
        if not path.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")
        
        # Start scanning
        if progress_callback:
            progress_callback("Starting scan...")
        
        self._scan_recursive(path, progress_callback)
        
        if progress_callback:
            progress_callback(f"Scan complete! Found {len(self.scanned_files)} files.")
        
        return self.scanned_files
    
    def _scan_recursive(self, path: Path, progress_callback=None):
        """
        Internal recursive method to scan directories.
        
        Args:
            path (Path): Current path to scan
            progress_callback (callable, optional): Callback function to report progress
        """
        try:
            # Iterate through all items in the directory
            for item in path.iterdir():
                try:
                    # Skip if it's a directory, recursively scan it
                    if item.is_dir():
                        self._scan_recursive(item, progress_callback)
                    # If it's a file, collect its information
                    elif item.is_file():
                        if progress_callback:
                            progress_callback(f"Scanning: {item}")

                        file_info = self._collect_file_info(item)
                        if file_info is not None:
                            self.scanned_files.append(file_info)
                        
                        # Report progress every 100 files
                        if progress_callback and len(self.scanned_files) % 100 == 0:
                            progress_callback(f"Files found: {len(self.scanned_files)}")
                
                except (PermissionError, OSError) as e:
                    # Skip files/folders we can't access
                    if progress_callback:
                        progress_callback(f"Skipped (no permission): {item}")
                    continue
        
        except (PermissionError, OSError) as e:
            # Skip directories we can't access
            if progress_callback:
                progress_callback(f"Skipped directory (no permission): {path}")
    
    def _collect_file_info(self, file_path: Path) -> Dict[str, any]:
        """
        Collect information about a file.
        
        Args:
            file_path (Path): Path to the file
            
        Returns:
            Dict: Dictionary containing file information
        """
        try:
            file_stats = file_path.stat()
            file_hash = generate_file_hash(str(file_path))

            if not file_hash:
                return None

            return {
                "path": str(file_path.absolute()),
                "size": file_stats.st_size,
                "name": file_path.name,
                "hash": file_hash,
            }
        except (OSError, PermissionError):
            return None
    
    def get_file_count(self) -> int:
        """
        Get the total number of files scanned.
        
        Returns:
            int: Number of files
        """
        return len(self.scanned_files)
