# smart_features.py
import os
import hashlib
from typing import Dict, List, Tuple, Callable
from collections import defaultdict

class SmartFeatures:
    """AI-powered features for file organization"""
    
    @staticmethod
    def find_duplicates(folder: str, chunk_size: int = 8192) -> Dict[str, List[str]]:
        """
        Find duplicate files in a folder using content hashing
        Returns: {hash: [list of file paths]}
        """
        hashes = defaultdict(list)
        
        for root, _, files in os.walk(folder):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    file_hash = SmartFeatures._file_hash(filepath, chunk_size)
                    hashes[file_hash].append(filepath)
                except (OSError, IOError):
                    continue
        
        # Filter out non-duplicates
        return {h: paths for h, paths in hashes.items() if len(paths) > 1}

    @staticmethod
    def _file_hash(filepath: str, chunk_size: int) -> str:
        """Calculate SHA256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    @staticmethod
    def suggest_categories(files: List[str], existing_categories: Dict[str, List[str]]) -> Dict[str, str]:
        """
        Suggest categories for files based on ML patterns
        Returns: {filename: suggested_category}
        """
        suggestions = {}
        
        # This would be replaced with actual ML model predictions
        # For now, we'll use a simple heuristic approach
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            
            # First check if extension matches existing categories
            for category, extensions in existing_categories.items():
                if ext in extensions:
                    suggestions[filename] = category
                    break
            else:
                # No existing category found - make a suggestion
                if ext in ('.jpg', '.png', '.gif'):
                    suggestions[filename] = "Images"
                elif ext in ('.doc', '.docx', '.pdf'):
                    suggestions[filename] = "Documents"
                else:
                    suggestions[filename] = "Others"
        
        return suggestions

    @staticmethod
    def batch_process(folders: List[str], operation: Callable, **kwargs) -> Dict[str, Tuple[int, List[str]]]:
        """
        Process multiple folders with the same operation
        Returns: {folder_path: (success_count, error_messages)}
        """
        results = {}
        
        for folder in folders:
            try:
                success, errors = operation(folder, **kwargs)
                results[folder] = (success, errors)
            except Exception as e:
                results[folder] = (0, [str(e)])
        
        return results