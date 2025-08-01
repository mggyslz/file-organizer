import os
import shutil
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Callable
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class FileOperations:
    """Handles all file system operations with threading support"""
    
    def __init__(self, file_types: Dict[str, List[str]]):
        self.file_types = file_types
        self._cancel_flag = False
    
    def cancel_operation(self):
        """Cancel ongoing operation"""
        self._cancel_flag = True
    
    def reset_cancel_flag(self):
        """Reset cancel flag for new operations"""
        self._cancel_flag = False
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0
    
    def passes_size_filter(self, file_path: str, min_size_bytes: int = 0, 
                          max_size_bytes: int = float('inf')) -> bool:
        """Check if file passes size filter"""
        file_size = self.get_file_size(file_path)
        return min_size_bytes <= file_size <= max_size_bytes
    
    def get_file_category(self, filename: str) -> str:
        """Get category for a file based on its extension"""
        ext = os.path.splitext(filename)[1].lower()
        
        for category, extensions in self.file_types.items():
            if ext in extensions:
                return category
        
        return "Others"
    
    def get_custom_tag_category(self, filename: str, custom_tags: List[str]) -> Optional[str]:
        """Check if file matches any custom tags"""
        filename_lower = filename.lower()
        for tag in custom_tags:
            if tag.lower() in filename_lower:
                return tag
        return None
    
    def get_date_folder(self, file_path: str) -> str:
        """Get date-based folder name"""
        try:
            stat = os.stat(file_path)
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            return mod_time.strftime("%Y-%m")
        except Exception:
            return "Unknown-Date"
    
    def get_files_in_folder(self, folder: str, skip_hidden: bool = True,
                           min_size_bytes: int = 0, max_size_bytes: int = float('inf')) -> List[str]:
        """Get list of files in folder with size filtering"""
        try:
            all_files = [f for f in os.listdir(folder) 
                        if os.path.isfile(os.path.join(folder, f))]
            
            if skip_hidden:
                all_files = [f for f in all_files if not f.startswith('.')]
            
            # Apply size filtering
            filtered_files = []
            for f in all_files:
                file_path = os.path.join(folder, f)
                if self.passes_size_filter(file_path, min_size_bytes, max_size_bytes):
                    filtered_files.append(f)
            
            return filtered_files
        except Exception as e:
            raise Exception(f"Error reading folder: {str(e)}")
    
    def get_organization_preview(self, folder: str, custom_tags: List[str], 
                               organize_by_date: bool, skip_hidden: bool,
                               manual_assignments: Dict[str, str],
                               min_size_bytes: int = 0, 
                               max_size_bytes: int = float('inf')) -> Dict[str, List[str]]:
        """Get preview of how files will be organized"""
        preview = {}
        
        try:
            files = self.get_files_in_folder(folder, skip_hidden, min_size_bytes, max_size_bytes)
            
            for filename in files:
                if self._cancel_flag:
                    break
                    
                file_path = os.path.join(folder, filename)
                
                # Check manual assignment first
                category = manual_assignments.get(filename)
                
                if not category:
                    custom_category = self.get_custom_tag_category(filename, custom_tags)
                    if custom_category:
                        category = custom_category
                    else:
                        category = self.get_file_category(filename)
                
                # Add date folder if needed
                if organize_by_date:
                    date_folder = self.get_date_folder(file_path)
                    category = f"{category}/{date_folder}"
                
                if category not in preview:
                    preview[category] = []
                preview[category].append(filename)
                
        except Exception as e:
            raise Exception(f"Error previewing files: {str(e)}")
        
        return preview
    
    def get_unique_path(self, path: str) -> str:
        """Get unique path if file already exists"""
        if not os.path.exists(path):
            return path
        
        directory = os.path.dirname(path)
        filename = os.path.basename(path)
        name, ext = os.path.splitext(filename)
        
        counter = 1
        while os.path.exists(path):
            new_filename = f"{name}_{counter}{ext}"
            path = os.path.join(directory, new_filename)
            counter += 1
        
        return path
    
    def organize_files_async(self, folder: str, custom_tags: List[str], 
                        organize_by_date: bool, create_folders: bool,
                        move_files: bool, skip_hidden: bool,
                        manual_assignments: Dict[str, str],
                        min_size_bytes: int = 0, max_size_bytes: int = float('inf'),
                        progress_callback: Callable = None, 
                        status_callback: Callable = None,
                        completion_callback: Callable = None,
                        thread_safe_update: Callable = None) -> None:
        """
        Organize files asynchronously in a background thread
        """
        def organize_worker():
            try:
                self.reset_cancel_flag()
                result = self.organize_files(
                    folder, custom_tags, organize_by_date, create_folders,
                    move_files, skip_hidden, manual_assignments,
                    min_size_bytes, max_size_bytes,
                    lambda current, total: thread_safe_update(0, lambda: progress_callback(current, total)) if progress_callback and thread_safe_update else None,
                    lambda msg: thread_safe_update(0, lambda: status_callback(msg)) if status_callback and thread_safe_update else None
                )
                if completion_callback and thread_safe_update:
                    thread_safe_update(0, lambda: completion_callback(result, None))
            except Exception as e:
                if completion_callback and thread_safe_update:
                    thread_safe_update(0, lambda: completion_callback(None, e))
    
        thread = threading.Thread(target=organize_worker, daemon=True)
        thread.start()
        return thread
    
    def organize_files(self, folder: str, custom_tags: List[str], 
                      organize_by_date: bool, create_folders: bool,
                      move_files: bool, skip_hidden: bool,
                      manual_assignments: Dict[str, str],
                      min_size_bytes: int = 0, max_size_bytes: int = float('inf'),
                      progress_callback: Callable = None, 
                      status_callback: Callable = None) -> Tuple[int, List[str], List[Tuple]]:
        """
        Organize files in the specified folder
        Returns: (organized_count, errors, undo_operations)
        """
        undo_operations = []
        errors = []
        organized = 0
        
        try:
            files = self.get_files_in_folder(folder, skip_hidden, min_size_bytes, max_size_bytes)
            total_files = len(files)
            
            # Use ThreadPoolExecutor for parallel processing of file operations
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_file = {}
                
                for i, filename in enumerate(files):
                    if self._cancel_flag:
                        break
                        
                    file_path = os.path.join(folder, filename)
                    
                    # Update progress
                    if progress_callback:
                        progress_callback(i + 1, total_files)
                    if status_callback:
                        status_callback(f"Processing: {filename}")
                    
                    # Submit file processing to thread pool
                    future = executor.submit(
                        self._process_single_file,
                        file_path, filename, folder, custom_tags,
                        organize_by_date, create_folders, move_files,
                        manual_assignments
                    )
                    future_to_file[future] = filename
                
                # Collect results
                for future in as_completed(future_to_file):
                    if self._cancel_flag:
                        break
                        
                    filename = future_to_file[future]
                    try:
                        result = future.result()
                        if result:
                            operation, success = result
                            if success:
                                undo_operations.append(operation)
                                organized += 1
                            else:
                                errors.append(f"{filename}: Operation failed")
                    except Exception as e:
                        errors.append(f"{filename}: {str(e)}")
                        
        except Exception as e:
            raise Exception(f"Error organizing files: {str(e)}")
        
        return organized, errors, undo_operations
    
    def _process_single_file(self, file_path: str, filename: str, folder: str,
                           custom_tags: List[str], organize_by_date: bool,
                           create_folders: bool, move_files: bool,
                           manual_assignments: Dict[str, str]) -> Optional[Tuple[Tuple, bool]]:
        """Process a single file for organization"""
        try:
            # Check manual assignment first
            category = manual_assignments.get(filename)
            
            if not category:
                # Determine category
                custom_category = self.get_custom_tag_category(filename, custom_tags)
                if custom_category:
                    category = custom_category
                else:
                    category = self.get_file_category(filename)
            
            # Create destination path
            if create_folders:
                if organize_by_date:
                    date_folder = self.get_date_folder(file_path)
                    dest_folder = os.path.join(folder, category, date_folder)
                else:
                    dest_folder = os.path.join(folder, category)
                
                os.makedirs(dest_folder, exist_ok=True)
                dest_path = os.path.join(dest_folder, filename)
            else:
                dest_path = os.path.join(folder, filename)
            
            # Handle duplicate names
            dest_path = self.get_unique_path(dest_path)
            
            # Move or copy file
            if file_path != dest_path:
                if move_files:
                    shutil.move(file_path, dest_path)
                    operation = ('move', file_path, dest_path)
                else:
                    shutil.copy2(file_path, dest_path)
                    operation = ('copy', file_path, dest_path)
                
                return operation, True
            
        except Exception:
            return None, False
        
        return None, True
    
    def undo_operations_async(self, operations: List[Tuple],
                            status_callback: Callable = None,
                            completion_callback: Callable = None,
                            thread_safe_update: Callable = None) -> threading.Thread:
        """Undo operations asynchronously"""
        def undo_worker():
            try:
                result = self.undo_operations(
                    operations,
                    lambda msg: thread_safe_update(0, lambda: status_callback(msg)) if status_callback and thread_safe_update else None
                )
                if completion_callback and thread_safe_update:
                    thread_safe_update(0, lambda: completion_callback(result, None))
            except Exception as e:
                if completion_callback and thread_safe_update:
                    thread_safe_update(0, lambda: completion_callback(None, e))

        thread = threading.Thread(target=undo_worker, daemon=True)
        thread.start()
        return thread
    
    def undo_operations(self, operations: List[Tuple], 
                    status_callback: Callable = None) -> Tuple[int, List[str]]:
        """
        Undo file operations and remove empty folders
        Returns: (undone_count, errors)
        """
        undone = 0
        errors = []
        folders_to_check = set()  # Track folders that might become empty
        
        # First pass: undo file operations
        for operation_type, source, destination in reversed(operations):
            if self._cancel_flag:
                break
                
            try:
                if status_callback:
                    status_callback(f"Undoing: {os.path.basename(destination)}")
                
                if operation_type == 'move':
                    if os.path.exists(destination):
                        shutil.move(destination, source)
                        undone += 1
                        # Track the folder that contained the moved file
                        folders_to_check.add(os.path.dirname(destination))
                elif operation_type == 'copy':
                    if os.path.exists(destination):
                        os.remove(destination)
                        undone += 1
                        # Track the folder that contained the copied file
                        folders_to_check.add(os.path.dirname(destination))
            except Exception as e:
                errors.append(f"{os.path.basename(destination)}: {str(e)}")
        
        # Second pass: remove empty folders
        removed_folders = []
        for folder in folders_to_check:
            try:
                # Walk up the directory tree to check for empty folders
                current_folder = folder
                while current_folder and os.path.exists(current_folder):
                    # Skip if folder is not empty
                    if os.listdir(current_folder):
                        break
                    
                    # Remove empty folder
                    os.rmdir(current_folder)
                    removed_folders.append(current_folder)
                    
                    # Move up to parent directory
                    current_folder = os.path.dirname(current_folder)
                    
            except Exception as e:
                errors.append(f"Error removing folder {folder}: {str(e)}")
        
        return undone, errors, removed_folders
    
    def check_folder_permissions(self, folder: str) -> bool:
        """Check if folder has write permissions"""
        return os.access(folder, os.W_OK)
    
    def get_folder_statistics(self, folder: str, skip_hidden: bool = True) -> Dict[str, int]:
        """Get statistics about folder contents"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'size_ranges': {
                'tiny': 0,      # < 1KB
                'small': 0,     # 1KB - 1MB
                'medium': 0,    # 1MB - 100MB
                'large': 0,     # 100MB - 1GB
                'huge': 0       # > 1GB
            }
        }
        
        try:
            files = [f for f in os.listdir(folder) 
                    if os.path.isfile(os.path.join(folder, f))]
            
            if skip_hidden:
                files = [f for f in files if not f.startswith('.')]
            
            for filename in files:
                file_path = os.path.join(folder, filename)
                file_size = self.get_file_size(file_path)
                
                stats['total_files'] += 1
                stats['total_size'] += file_size
                
                # Categorize by size
                if file_size < 1024:  # < 1KB
                    stats['size_ranges']['tiny'] += 1
                elif file_size < 1024 * 1024:  # < 1MB
                    stats['size_ranges']['small'] += 1
                elif file_size < 100 * 1024 * 1024:  # < 100MB
                    stats['size_ranges']['medium'] += 1
                elif file_size < 1024 * 1024 * 1024:  # < 1GB
                    stats['size_ranges']['large'] += 1
                else:  # >= 1GB
                    stats['size_ranges']['huge'] += 1
                    
        except Exception:
            pass
        
        return stats