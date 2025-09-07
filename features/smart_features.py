# smart_features.py
import os
import hashlib
from typing import Dict, List, Tuple, Callable
from collections import defaultdict

class SmartFeatures:
    """AI-powered features for file organization"""
    
    @staticmethod
    def find_duplicates(folder: str, chunk_size: int = 65536) -> Dict[str, List[str]]:
        """
        Find duplicate files in a folder using content hashing
        Returns: {hash: [list of relative file paths]}
        """
        hashes = defaultdict(list)
        
        try:
            # Get all files in the folder (not subdirectories)
            files = [f for f in os.listdir(folder) 
                    if os.path.isfile(os.path.join(folder, f)) and not f.startswith('.')]
            
            for filename in files:
                filepath = os.path.join(folder, filename)
                try:
                    # Skip empty files
                    if os.path.getsize(filepath) == 0:
                        continue
                        
                    file_hash = SmartFeatures._file_hash(filepath, chunk_size)
                    # Store relative filename instead of full path for UI consistency
                    hashes[file_hash].append(filename)
                except (OSError, IOError, PermissionError) as e:
                    print(f"Error processing {filename}: {e}")
                    continue
                    
        except (OSError, IOError) as e:
            raise Exception(f"Cannot access folder: {e}")
        
        # Filter out non-duplicates and empty results
        duplicates = {h: paths for h, paths in hashes.items() if len(paths) > 1}
        
        if not duplicates:
            return {}
            
        return duplicates

    @staticmethod
    def _file_hash(filepath: str, chunk_size: int) -> str:
        """Calculate SHA256 hash of a file with better error handling"""
        hash_sha256 = hashlib.sha256()
        
        try:
            with open(filepath, "rb") as f:
                # Read file in chunks to handle large files efficiently
                while chunk := f.read(chunk_size):
                    hash_sha256.update(chunk)
        except (OSError, IOError, MemoryError) as e:
            raise IOError(f"Cannot hash file {os.path.basename(filepath)}: {e}")
            
        return hash_sha256.hexdigest()

    @staticmethod
    def suggest_categories(files: List[str], existing_categories: Dict[str, List[str]]) -> Dict[str, str]:
        """
        Suggest categories for files based on patterns
        Returns: {filename: suggested_category}
        """
        suggestions = {}
        
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            
            # First check if extension matches existing categories
            suggested_category = None
            for category, extensions in existing_categories.items():
                if ext in extensions:
                    suggested_category = category
                    break
            
            # If no existing category found, make a basic suggestion
            if not suggested_category:
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff']:
                    suggested_category = "Images"
                elif ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
                    suggested_category = "Documents"
                elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv']:
                    suggested_category = "Videos"
                elif ext in ['.mp3', '.wav', '.ogg', '.flac', '.aac']:
                    suggested_category = "Audio"
                else:
                    suggested_category = "Others"
                    
            suggestions[filename] = suggested_category
        
        return suggestions

    @staticmethod
    def batch_process(folders: List[str], operation: Callable, **kwargs) -> Dict[str, Tuple[int, List[str]]]:
        """
        Process multiple folders with the same operation
        Returns: {folder_path: (success_count, error_messages)}
        """
        results = {}
        
        for folder in folders:
            if not os.path.isdir(folder):
                results[folder] = (0, ["Folder does not exist or is not accessible"])
                continue
                
            try:
                success, errors = operation(folder, **kwargs)
                results[folder] = (success, errors if isinstance(errors, list) else [str(errors)])
            except Exception as e:
                results[folder] = (0, [f"Operation failed: {str(e)}"])
        
        return results