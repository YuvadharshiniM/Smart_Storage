"""Scanner package for file scanning functionality."""
from .scanner import FileScanner
from .duplicate_finder import find_duplicates, count_duplicates, calculate_wasted_space

__all__ = ['FileScanner', 'find_duplicates', 'count_duplicates', 'calculate_wasted_space']
