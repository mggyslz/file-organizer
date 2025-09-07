import os
import sys
import threading
from typing import Dict, List
from tkinter import messagebox
import customtkinter as ctk

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from config.config_manager import ConfigManager
from core.file_operations import FileOperations
from ui.main_window import MainWindow
from features.smart_features import SmartFeatures
from features.security_performance import SecurityPerformance

class FileOrganizer:
    """Main File Organizer application controller"""
    
    def __init__(self):
        # Initialize core components
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        self.file_ops = FileOperations(self.config['file_types'])
        self.smart_features = SmartFeatures()
        self.security_perf = SecurityPerformance()
        
        # Operation state
        self.current_operation_thread = None
        self.operation_in_progress = False
        self.undo_operations = []
        self.manual_assignments = self.config.get('manual_assignments', {})
        
        # Initialize UI
        self.main_window = MainWindow(self)
        
        # Load saved settings
        self._load_settings()
    
    def _load_settings(self):
        """Load settings from configuration"""
        settings = {
            'organize_by_date': self.config.get('organize_by_date', False),
            'move_files': self.config.get('move_files', True),
            'create_folders': self.config.get('create_folders', True),
            'skip_hidden': self.config.get('skip_hidden', True),
            'custom_tags': self.config.get('custom_tags', ''),
            'last_folder': self.config.get('last_folder', ''),
            'min_size': self.config.get('min_size', '0'),
            'max_size': self.config.get('max_size', ''),
            'size_unit': self.config.get('size_unit', 'MB')
        }
        self.main_window.load_settings(settings)
    
    def save_settings(self):
        """Save current settings to configuration"""
        settings = self.main_window.get_current_settings()
        self.config.update(settings)
        self.config['file_types'] = self.file_ops.file_types
        self.config['manual_assignments'] = self.manual_assignments
        self.config_manager.save_config(self.config)
    
    def _convert_size_to_bytes(self, size_str: str, unit: str, is_max: bool = False) -> int:
        """Convert size string to bytes"""
        if not size_str or not size_str.strip():
            return 0 if not is_max else float('inf')
        
        try:
            size = float(size_str)
            multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
            return int(size * multipliers.get(unit, 1))
        except ValueError:
            return 0 if not is_max else float('inf')
    
    # =============================================================================
    # File Operations
    # =============================================================================
    
    def browse_folder(self):
        """Browse for folder and update file count"""
        folder = self.main_window.browse_folder()
        if folder:
            self.update_file_count(folder)
    
    def update_file_count(self, folder: str):
        """Update file count display"""
        if not folder or not os.path.isdir(folder):
            self.main_window.set_file_count("Select a folder to see file count")
            return
            
        try:
            settings = self.main_window.get_current_settings()
            min_size = self._convert_size_to_bytes(settings['min_size'], 'min')
            max_size = self._convert_size_to_bytes(settings['max_size'], settings['size_unit'], True)
            
            files = self.file_ops.get_files_in_folder(
                folder, settings['skip_hidden'], min_size, max_size
            )
            self.main_window.set_file_count(f"Found {len(files)} files to organize")
        except Exception:
            self.main_window.set_file_count("Error reading folder")
    
    def get_folder_statistics(self):
        """Show folder statistics"""
        folder = self.main_window.get_selected_folder()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Warning", "Please select a valid folder first.")
            return
        
        try:
            settings = self.main_window.get_current_settings()
            stats = self.file_ops.get_folder_statistics(folder, settings['skip_hidden'])
            self.main_window.show_folder_statistics(stats)
        except Exception as e:
            messagebox.showerror("Error", f"Error getting folder statistics: {str(e)}")
    
    def preview_organization(self):
        """Preview file organization"""
        folder = self.main_window.get_selected_folder()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Warning", "Please select a valid folder first.")
            return
        
        try:
            settings = self.main_window.get_current_settings()
            custom_tags = [tag.strip() for tag in settings['custom_tags'].split(",") if tag.strip()]
            
            min_size = self._convert_size_to_bytes(settings['min_size'], 'min')
            max_size = self._convert_size_to_bytes(settings['max_size'], settings['size_unit'], True)
            
            preview_data = self.file_ops.get_organization_preview(
                folder, custom_tags, settings['organize_by_date'],
                settings['skip_hidden'], self.manual_assignments,
                min_size, max_size
            )
            
            if not preview_data:
                messagebox.showinfo("Preview", "No files found to organize with current filters.")
                return
            
            self.main_window.show_preview(preview_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error previewing organization: {str(e)}")
    
    def organize_files(self):
        """Organize files asynchronously"""
        if self.operation_in_progress:
            messagebox.showwarning("Warning", "An operation is already in progress.")
            return
        
        folder = self.main_window.get_selected_folder()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Warning", "Please select a valid folder first.")
            return
        
        if not self.file_ops.check_folder_permissions(folder):
            messagebox.showerror("Error", "No write permission for the selected folder.")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to organize the files?"):
            return
        
        try:
            settings = self.main_window.get_current_settings()
            custom_tags = [tag.strip() for tag in settings['custom_tags'].split(",") if tag.strip()]
            
            min_size = self._convert_size_to_bytes(settings['min_size'], 'min')
            max_size = self._convert_size_to_bytes(settings['max_size'], settings['size_unit'], True)
            
            self._start_operation()
            
            def completion_callback(result, error):
                self._end_operation()
                
                if error:
                    messagebox.showerror("Error", f"Error organizing files: {str(error)}")
                    self.main_window.set_status("Error occurred during organization")
                    return
                
                organized, errors, undo_ops = result
                
                if undo_ops:
                    self.undo_operations = undo_ops
                
                self.save_settings()
                self._show_organization_results(organized, errors)
                self.update_file_count(folder)
            
            self.current_operation_thread = self.file_ops.organize_files_async(
                folder, custom_tags, settings['organize_by_date'],
                settings['create_folders'], settings['move_files'],
                settings['skip_hidden'], self.manual_assignments,
                min_size, max_size,
                self.main_window.update_progress,
                self.main_window.set_status,
                completion_callback,
                self.main_window.root.after
            )
            
        except Exception as e:
            self._end_operation()
            messagebox.showerror("Error", f"Error starting organization: {str(e)}")
    
    def _show_organization_results(self, organized: int, errors: List[str]):
        """Show organization results"""
        message = f"Organization complete!\n\nFiles organized: {organized}"
        if errors:
            message += f"\nErrors encountered: {len(errors)}"
            message += "\n\nFirst few errors:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                message += f"\n... and {len(errors) - 5} more errors"
        
        messagebox.showinfo("Complete", message)
        self.main_window.set_status("Organization complete!")
    
    def undo_last_operation(self):
        """Undo the last file organization operation including folder removal"""
        if self.operation_in_progress:
            messagebox.showwarning("Warning", "Please wait for current operation to complete.")
            return
        
        if not self.undo_operations:
            messagebox.showinfo("Undo", "No operations to undo.")
            return
        
        if not messagebox.askyesno("Confirm Undo", "Are you sure you want to undo the last operation? This will remove any empty folders created during organization."):
            return
        
        try:
            self._start_operation()
            
            def completion_callback(result, error):
                self._end_operation()
                
                if error:
                    messagebox.showerror("Error", f"Error during undo: {str(error)}")
                    self.main_window.set_status("Error occurred during undo")
                    return
                
                undone, errors, removed_folders = result
                self.undo_operations = []
                
                message = f"Undo complete!\n\nFiles restored: {undone}"
                if removed_folders:
                    message += f"\nRemoved {len(removed_folders)} empty folders"
                if errors:
                    message += f"\nErrors encountered: {len(errors)}"
                    message += "\n\nFirst few errors:\n" + "\n".join(errors[:3])
                    if len(errors) > 3:
                        message += f"\n... and {len(errors) - 3} more errors"
                
                messagebox.showinfo("Undo Complete", message)
                self.main_window.set_status("Undo operation complete!")
                
                folder = self.main_window.get_selected_folder()
                if folder and os.path.isdir(folder):
                    self.update_file_count(folder)
            
            self.current_operation_thread = self.file_ops.undo_operations_async(
                self.undo_operations, self.main_window.set_status, 
                completion_callback, self.main_window.root.after
            )
                
        except Exception as e:
            self._end_operation()
            messagebox.showerror("Error", f"Error starting undo: {str(e)}")
    
    def cancel_operation(self):
        """Cancel current operation"""
        if self.operation_in_progress and self.current_operation_thread:
            self.file_ops.cancel_operation()
            self.main_window.set_status("Cancelling operation...")
    
    def _start_operation(self):
        """Start operation state"""
        self.operation_in_progress = True
        self.main_window.set_operation_state(True)
        self.main_window.reset_progress()
    
    def _end_operation(self):
        """End operation state"""
        self.operation_in_progress = False
        self.current_operation_thread = None
        self.main_window.set_operation_state(False)
        self.main_window.reset_progress()
    
    # =============================================================================
    # Advanced Features
    # =============================================================================
    
    def find_duplicates(self):
            """Find and manage duplicate files with improved error handling"""
            if self.operation_in_progress:
                messagebox.showwarning("Warning", "Please wait for current operation to complete.")
                return
                
            folder = self.main_window.get_selected_folder()
            if not folder or not os.path.isdir(folder):
                messagebox.showwarning("Warning", "Please select a valid folder first.")
                return

            try:
                # Show progress
                self.main_window.set_status("Scanning for duplicate files...")
                
                # Find duplicates
                duplicates = self.smart_features.find_duplicates(folder)
                
                if not duplicates:
                    self.main_window.set_status("No duplicate files found")
                    messagebox.showinfo("No Duplicates", "No duplicate files found in the selected folder!")
                    return
                
                # Calculate statistics
                total_duplicates = sum(len(files) for files in duplicates.values())
                total_groups = len(duplicates)
                
                self.main_window.set_status(f"Found {total_duplicates} duplicates in {total_groups} groups")
                
                # Show duplicates window
                self.main_window.show_duplicates(duplicates, folder, self.security_perf)
                
            except PermissionError:
                messagebox.showerror("Permission Error", 
                    "Cannot access some files in the folder. Please check permissions.")
                self.main_window.set_status("Permission error occurred")
            except FileNotFoundError:
                messagebox.showerror("Error", "The selected folder no longer exists.")
                self.main_window.set_status("Folder not found")
            except Exception as e:
                error_msg = f"Error finding duplicates: {str(e)}"
                messagebox.showerror("Error", error_msg)
                self.main_window.set_status("Error occurred while finding duplicates")
                print(f"Duplicate finding error: {e}")  # For debugging
    
    def open_file_types_editor(self):
        """Open file types editor"""
        def save_callback():
            self.file_ops.file_types = self.config['file_types']
            self.save_settings()
        
        self.main_window.show_file_types_editor(self.config['file_types'], save_callback)
    
    def open_manual_assignment_window(self):
        """Open manual file assignment window"""
        folder = self.main_window.get_selected_folder()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Warning", "Please select a valid folder first.")
            return
        
        try:
            settings = self.main_window.get_current_settings()
            min_size = self._convert_size_to_bytes(settings['min_size'], 'min')
            max_size = self._convert_size_to_bytes(settings['max_size'], settings['size_unit'], True)
            
            files = self.file_ops.get_files_in_folder(
                folder, settings['skip_hidden'], min_size, max_size
            )
            
            if not files:
                messagebox.showinfo("No Files", "No files found in the selected folder with current filters.")
                return
            
            def save_assignments(assignments: Dict[str, str]):
                self.manual_assignments = assignments
                self.save_settings()
                messagebox.showinfo("Saved", "Manual assignments saved successfully!")
            
            self.main_window.show_manual_assignment(
                files, self.config['file_types'], settings['custom_tags'],
                self.manual_assignments, save_assignments, folder
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error opening manual assignment window: {str(e)}")
    
    # =============================================================================
    # Application Lifecycle
    # =============================================================================
    
    def run(self):
        """Start the application"""
        try:
            self.main_window.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.main_window.run()
        except KeyboardInterrupt:
            pass
        finally:
            self.save_settings()
            
    def on_closing(self):
        """Handle application closing"""
        if self.operation_in_progress:
            if messagebox.askyesno("Confirm Exit", "An operation is in progress. Do you want to cancel it and exit?"):
                self.file_ops.cancel_operation()
                self.main_window.root.after(1000, self.main_window.root.destroy)
            return
        
        self.save_settings()
        self.main_window.root.destroy()

def main():
    """Main entry point"""
    try:
        app = FileOrganizer()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
    
    #  date folder
    