# security_performance.py
import os
import time
from typing import Callable, Any
from functools import wraps
import hashlib

class SecurityPerformance:
    """Security and performance optimization utilities"""
    
    @staticmethod
    def secure_delete(filepath: str, passes: int = 3) -> None:
        """Securely delete a file by overwriting its content"""
        try:
            with open(filepath, "ba+") as f:
                length = f.tell()
                for _ in range(passes):
                    f.seek(0)
                    f.write(os.urandom(length))
            os.remove(filepath)
        except Exception:
            pass

    @staticmethod
    def timeit(func: Callable) -> Callable:
        """Decorator to measure execution time"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f"{func.__name__} executed in {end-start:.4f}s")
            return result
        return wrapper

    @staticmethod
    def memoize(maxsize: int = 128) -> Callable:
        """Memoization decorator for expensive functions"""
        cache = {}
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = str(args) + str(kwargs)
                
                if key not in cache:
                    if len(cache) >= maxsize:
                        cache.popitem()
                    cache[key] = func(*args, **kwargs)
                
                return cache[key]
            return wrapper
        return decorator

    @staticmethod
    def process_large_folders(folder: str, operation: Callable, 
                            batch_size: int = 100) -> None:
        """
        Process large folders in batches to prevent memory issues
        """
        for root, dirs, files in os.walk(folder):
            for i in range(0, len(files), batch_size):
                batch = files[i:i+batch_size]
                operation([os.path.join(root, f) for f in batch])

    @staticmethod
    def verify_integrity(filepath: str, original_hash: str) -> bool:
        """Verify file integrity using SHA256 hash"""
        current_hash = SecurityPerformance._file_hash(filepath)
        return current_hash == original_hash

    @staticmethod
    def _file_hash(filepath: str, chunk_size: int = 8192) -> str:
        """Calculate SHA256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()