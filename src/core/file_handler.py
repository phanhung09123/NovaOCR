"""File Handler - Single Responsibility Principle"""
import os
from pathlib import Path
from typing import List, Tuple
from natsort import natsorted


class FileHandler:
    """
    Handles file discovery, validation, and duplicate detection.
    """
    
    VALID_EXTENSIONS = ('.pdf', '.jpg', '.jpeg', '.png', '.webp')
    
    @staticmethod
    def find_valid_files(folder_path: str) -> List[str]:
        """
        Find all valid files in a folder.
        
        Args:
            folder_path: Path to folder to search
            
        Returns:
            List of absolute paths to valid files, naturally sorted
            
        Raises:
            FileNotFoundError: If folder doesn't exist
        """
        folder = Path(folder_path)
        
        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        if not folder.is_dir():
            raise NotADirectoryError(f"Not a directory: {folder_path}")
        
        # Get all files in folder
        all_files = [f for f in folder.iterdir() if f.is_file()]
        
        # Filter by extension
        valid_files = [
            f for f in all_files 
            if f.suffix.lower() in FileHandler.VALID_EXTENSIONS
        ]
        
        # Natural sort (handles numbers correctly)
        sorted_files = natsorted(valid_files, key=lambda x: x.name.lower())
        
        # Return absolute paths as strings
        return [str(f.resolve()) for f in sorted_files]
    
    @staticmethod
    def detect_duplicates(file_paths: List[str]) -> List[Tuple[str, str]]:
        """
        Detect duplicate filenames (case-insensitive).
        
        Args:
            file_paths: List of file paths
            
        Returns:
            List of tuples (original_file, duplicate_file)
        """
        seen_names = {}
        duplicates = []
        
        for file_path in file_paths:
            filename = Path(file_path).name.lower()
            
            if filename in seen_names:
                duplicates.append((seen_names[filename], file_path))
            else:
                seen_names[filename] = file_path
        
        return duplicates
    
    @staticmethod
    def validate_folder(folder_path: str) -> Tuple[bool, str, int]:
        """
        Validate folder and return status.
        
        Args:
            folder_path: Path to validate
            
        Returns:
            Tuple of (is_valid, message, file_count)
        """
        try:
            files = FileHandler.find_valid_files(folder_path)
            
            if not files:
                return False, "No valid files found in folder", 0
            
            duplicates = FileHandler.detect_duplicates(files)
            
            if duplicates:
                dup_msg = "\n".join([f"  - '{Path(d[0]).name}' and '{Path(d[1]).name}'" 
                                    for d in duplicates])
                warning = f"Warning: Duplicate filenames detected:\n{dup_msg}"
                return True, warning, len(files)
            
            return True, f"Found {len(files)} valid file(s)", len(files)
            
        except Exception as e:
            return False, str(e), 0
