"""
Duplicate File Finder Module
Identifies duplicate files by comparing SHA-256 hashes.
"""
from typing import List, Dict


def find_duplicates(file_metadata: List[Dict[str, any]]) -> List[List[str]]:
    """
    Find duplicate files by grouping them by identical hash values.
    
    Args:
        file_metadata (List[Dict]): List of file metadata dictionaries.
                                     Each dict must contain 'path' and 'hash' keys.
    
    Returns:
        List[List[str]]: List of duplicate groups. Each group is a list of file paths
                         that share the same hash. Only groups with 2+ files are returned.
    
    Example:
        >>> files = [
        ...     {"path": "/a/file1.txt", "size": 100, "hash": "abc123"},
        ...     {"path": "/b/file2.txt", "size": 100, "hash": "abc123"},
        ...     {"path": "/c/file3.txt", "size": 200, "hash": "def456"}
        ... ]
        >>> find_duplicates(files)
        [['/a/file1.txt', '/b/file2.txt']]
    """
    # Group files by hash
    hash_groups = {}
    
    for file_info in file_metadata:
        file_hash = file_info.get("hash")
        file_path = file_info.get("path")
        
        # Skip files without hash or path
        if not file_hash or not file_path:
            continue
        
        # Add file to hash group
        if file_hash not in hash_groups:
            hash_groups[file_hash] = []
        
        hash_groups[file_hash].append(file_path)
    
    # Filter groups to include only duplicates (2+ files with same hash)
    duplicates = [
        paths for paths in hash_groups.values()
        if len(paths) > 1
    ]
    
    return duplicates


def count_duplicates(file_metadata: List[Dict[str, any]]) -> Dict[str, int]:
    """
    Count the number of duplicate groups and total duplicate files.
    
    Args:
        file_metadata (List[Dict]): List of file metadata dictionaries.
    
    Returns:
        Dict[str, int]: Dictionary with 'groups' (number of duplicate groups) and
                        'files' (total number of duplicate files).
    """
    duplicate_groups = find_duplicates(file_metadata)
    
    total_duplicate_files = sum(len(group) for group in duplicate_groups)
    
    return {
        "groups": len(duplicate_groups),
        "files": total_duplicate_files
    }


def calculate_wasted_space(file_metadata: List[Dict[str, any]]) -> int:
    """
    Calculate total wasted storage space from duplicate files.
    
    For each duplicate group, the wasted space is (n-1) * file_size,
    where n is the number of duplicates.
    
    Args:
        file_metadata (List[Dict]): List of file metadata dictionaries.
                                     Each dict must contain 'path', 'hash', and 'size'.
    
    Returns:
        int: Total wasted space in bytes.
    """
    # Group files by hash with size information
    hash_groups = {}
    
    for file_info in file_metadata:
        file_hash = file_info.get("hash")
        file_size = file_info.get("size", 0)
        
        if not file_hash:
            continue
        
        if file_hash not in hash_groups:
            hash_groups[file_hash] = {
                "count": 0,
                "size": file_size
            }
        
        hash_groups[file_hash]["count"] += 1
    
    # Calculate wasted space
    wasted_space = 0
    for group_info in hash_groups.values():
        if group_info["count"] > 1:
            # Wasted space = (n-1) * file_size
            wasted_space += (group_info["count"] - 1) * group_info["size"]
    
    return wasted_space
