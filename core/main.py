import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import customtkinter as ctk
from tkinter import ttk
from typing import Dict, List, Callable
import threading
from PIL import Image

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from config.config_manager import ConfigManager
from core.file_operations import FileOperations
from ui.ui_components import UIComponents
from features.smart_features import SmartFeatures
from ui.ui_enhancements import UIEnhancements
from features.security_performance import SecurityPerformance

class FileOrganizer:
    """Main File Organizer application with async support"""
    
    def __init__(self):
        self.root = ctk.CTk()
        # Set application icon
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'app_logo.ico')
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        # Initialize managers
        self.config_manager = ConfigManager()
        
        # Load configuration
        self.config = self.config_manager.load_config()
        
        # Initialize file operations with loaded file types
        self.file_ops = FileOperations(self.config['file_types'])
        
        # Initialize additional features FIRST
        self.smart_features = SmartFeatures()
        self.ui_enhancements = UIEnhancements()  # Must be created before UIComponents
        self.security_perf = SecurityPerformance()
        
        # Initialize UI with both required arguments
        self.ui = UIComponents(self.root, self.ui_enhancements)
        
        # Undo operations
        self.undo_operations = []
        
        # Operation state
        self.current_operation_thread = None
        self.operation_in_progress = False
        
        # Initialize UI variables
        self._init_ui_variables()
        
        # Setup UI
        self._setup_ui()
        
        # Load saved settings
        self._load_settings()
        
    def _load_image(self, image_name, size=(24, 24)):
        """Load an image from the assets folder"""
        assets_path = os.path.join(os.path.dirname(__file__), '..', 'assets')
        image_path = os.path.join(assets_path, image_name)
        if os.path.exists(image_path):
            return ctk.CTkImage(Image.open(image_path), size=size)
        return None
        
    def bring_to_front(self, window):
        """Bring a popup window to the front and focus it"""
        window.lift()
        window.grab_set()
        window.focus_force()
    
    def _init_ui_variables(self):
        """Initialize UI variables"""
        self.folder_var = ctk.StringVar()
        self.create_folders_var = ctk.BooleanVar(value=True)
        self.move_files_var = ctk.BooleanVar(value=True)
        self.organize_by_date_var = ctk.BooleanVar()
        self.skip_hidden_var = ctk.BooleanVar(value=True)
        self.custom_tags_var = ctk.StringVar()
        self.file_count_var = ctk.StringVar(value="Select a folder to see file count")
        self.status_var = ctk.StringVar(value="Ready to organize files!")
        
        # Size filtering variables
        self.min_size_var = ctk.StringVar(value="0")
        self.max_size_var = ctk.StringVar(value="")
        self.size_unit_var = ctk.StringVar(value="MB")
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(self.root, mode='determinate', height=6)
        
        # Manual assignments
        self.manual_assignments = {}
        
        # Bind folder selection change
        self.folder_var.trace('w', self.on_folder_change)
    
    def _setup_ui(self):
        """Setup the main UI with sidebar"""
            # Load icons first
        self.folder_icon = self._load_image("folder.png")
        self.manual_icon = self._load_image("manual.png")
        self.stats_icon = self._load_image("statistics.png")
        self.filetype_icon = self._load_image("file.png")
        self.duplicate_icon = self._load_image("duplicates.png")
        self.undo_icon = self._load_image("undo.png")
        
        callbacks = {
            'browse_folder': self.browse_folder,
            'preview_organization': self.preview_organization,
            'organize_files': self.organize_files,
            'undo_last_operation': self.undo_last_operation,
            'open_file_types_editor': self.open_file_types_editor,
            'open_manual_assignment_window': self.open_manual_assignment_window,
            'cancel_operation': self.cancel_operation,
            'get_folder_statistics': self.get_folder_statistics,
            'find_duplicates': self.find_duplicates
        }
        
        # Main container with sidebar
        main_container = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        main_container.pack(fill="both", expand=True)
        
        # ===== Sidebar =====
        sidebar = ctk.CTkFrame(main_container, width=200, corner_radius=0)
        sidebar.pack(side="left", fill="y", padx=(0, 10), pady=10)
        sidebar.pack_propagate(False)
        

        # Create a container frame for better control of positioning
        title_frame = ctk.CTkFrame(sidebar, fg_color="transparent")  # Transparent background
        title_frame.pack(pady=(10, 20))  # Adjust these values to control vertical spacing

        # Create the label with centered alignment
        ctk.CTkLabel(title_frame, 
                    text="File Organizer", 
                    font=ctk.CTkFont(size=20, weight="bold"),
                    compound="left"  # Places icon to the left of text
                    ).pack(anchor="center")  # This centers the label horizontally

        # If you want even more precise control over the vertical position:
        # title_frame.pack(pady=(20, 25))  # Top and bottom padding
        
        # Sidebar buttons with icons
        sidebar_buttons = [
            ("Browse Folder", callbacks['browse_folder'], self.folder_icon),
            ("Manual Assign", callbacks['open_manual_assignment_window'], self.manual_icon),
            ("Statistics", callbacks['get_folder_statistics'], self.stats_icon),
            ("File Types", callbacks['open_file_types_editor'], self.filetype_icon),
            ("Find Duplicates", callbacks['find_duplicates'], self.duplicate_icon),
            ("Undo Last", callbacks['undo_last_operation'], self.undo_icon)
        ]
        
        for text, command, icon in sidebar_buttons:
            btn = ctk.CTkButton(
                sidebar, 
                text=text, 
                command=command,
                corner_radius=5, 
                anchor="w", 
                height=40,
                image=icon,
                compound="left",
                font=ctk.CTkFont(size=13)
            )
            btn.pack(fill="x", padx=5, pady=2)
        
        # Sidebar footer
        ctk.CTkLabel(sidebar, text="", height=20).pack(side="bottom", fill="x")  # Spacer
        ctk.CTkLabel(sidebar, text="Version 2.0", 
                    font=ctk.CTkFont(size=10), text_color="gray70").pack(side="bottom", pady=(0, 10))
        
        # ===== Main Content =====
        content_frame = ctk.CTkFrame(main_container, corner_radius=10)
        content_frame.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)
        
        # Header with subtle shadow effect
        header_content = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_content.pack(fill="x", pady=(15, 5), padx=20)
        
        ctk.CTkLabel(header_content, 
                    text="Organize Your Files", 
                    font=ctk.CTkFont(size=27, weight="bold")).pack(pady=(0, 5))
        
        ctk.CTkLabel(header_content, 
                    text="Automatically sort files into categorized folders",
                    font=ctk.CTkFont(size=12), 
                    text_color="gray70").pack()
        
        # Folder selection
        self._create_folder_selection_frame(content_frame, self.folder_var, callbacks['browse_folder'])
        
        # ===== Tab View for Options =====
        tabview = ctk.CTkTabview(content_frame, height=300)
        tabview.pack(fill="x", padx=20, pady=(0, 15))
        
        # Basic Options Tab
        tab_basic = tabview.add("Organization Options")
        if hasattr(self, 'settings_icon'):
            tab_basic.configure(image=self.settings_icon)
            
        self._create_options_frame(tab_basic, self.create_folders_var, self.move_files_var, 
                                 self.organize_by_date_var, self.skip_hidden_var, self.custom_tags_var)
        
        
        # File count and progress
        ctk.CTkLabel(content_frame, textvariable=self.file_count_var, 
                    font=ctk.CTkFont(size=13)).pack(pady=(5, 0), padx=20, anchor="w")
        
        self.progress.pack(fill="x", padx=20, pady=(10, 5))
        
        # Action buttons with better visual hierarchy
        action_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=(5, 10))
        
        # First load all icons
        preview_icon = self._load_image("preview.png", size=(20, 20))
        rocket_icon = self._load_image("rocket.png", size=(20, 20))
        cancel_icon = self._load_image("cancel.png", size=(20, 20))

        # Preview Changes Button (blue version)
        ctk.CTkButton(
            action_frame,
            text="   Preview Changes",  # Extra spaces for width
            command=callbacks['preview_organization'],
            fg_color="#3a7ebf",  # Blue color
            hover_color="#2d5985",  # Darker blue on hover
            border_width=1,
            text_color="white",
            height=38,  # Increased height
            width=180,  # Fixed width
            font=ctk.CTkFont(size=13),  # Slightly larger font
            image=preview_icon,
            compound="left",
            anchor="center"  # Center the content
        ).pack(side="left", padx=(0, 10))

        # Organize Files Button
        ctk.CTkButton(
            action_frame,
            text="   Organize Files", 
            command=callbacks['organize_files'],
            fg_color="#2CC985", 
            hover_color="#27AE60",
            height=38,
            width=180,
            font=ctk.CTkFont(size=13, weight="bold"),
            image=rocket_icon,
            compound="left",
            anchor="center"
        ).pack(side="left", padx=(0, 10))

        # Cancel Button
        self.cancel_btn = ctk.CTkButton(
            action_frame, 
            text="   Cancel", 
            command=callbacks['cancel_operation'], 
            state="disabled",
            height=38,
            width=120,  # Slightly narrower
            font=ctk.CTkFont(size=13),
            image=cancel_icon,
            compound="left",
            anchor="center"
        )
        self.cancel_btn.pack(side="left")
        
        # Status bar with subtle top border
        status_frame = ctk.CTkFrame(content_frame, height=36, corner_radius=0)
        status_frame.pack(fill="x", side="bottom", padx=0, pady=0)
        
        # Add top border
        ctk.CTkFrame(status_frame, height=1, fg_color="#333333").pack(fill="x", pady=(0, 5))
        
        # Status label
        status_label = ctk.CTkLabel(status_frame, textvariable=self.status_var,
                                  font=ctk.CTkFont(size=11), anchor="w")
        status_label.pack(side="left", padx=10)
        
        # Footer
        ctk.CTkLabel(status_frame,
                    text="© 2025 File Organizer | A project by mggyslz",
                    font=ctk.CTkFont(size=11),
                    text_color="gray70",
                    anchor="center",
                    height=25).pack(side="bottom", fill="x", pady=(0, 5))
    
    def _create_folder_selection_frame(self, parent, folder_var, browse_callback):
        frame = ctk.CTkFrame(parent, height=70)
        frame.pack(fill="x", pady=(0, 15), padx=20)
        
        ctk.CTkLabel(frame, text="Folder to Organize:", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=15, pady=(9, 3))
        
        entry_frame = ctk.CTkFrame(frame, fg_color="transparent")
        entry_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        entry = ctk.CTkEntry(entry_frame, textvariable=folder_var, height=42,
                            font=ctk.CTkFont(size=14), corner_radius=6)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        button = ctk.CTkButton(entry_frame, text="Browse", 
                              command=browse_callback, width=90, height=42,
                              font=ctk.CTkFont(size=12))
        button.pack(side="right")

    def _create_options_frame(self, parent, create_folders_var, move_files_var, 
                            organize_by_date_var, skip_hidden_var, custom_tags_var):
        # Main options frame with better spacing
        options_frame = ctk.CTkFrame(parent, fg_color="transparent")
        options_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Options grid layout
        options_grid = ctk.CTkFrame(options_frame, fg_color="transparent")
        options_grid.pack(fill="x", pady=(0, 15))
        
        # First column
        col1 = ctk.CTkFrame(options_grid, fg_color="transparent")
        col1.pack(side="left", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(col1, text="Basic Settings:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        options = [
            ("Create category folders", create_folders_var),
            ("Move files (instead of copy)", move_files_var),
            ("Organize by date (YYYY-MM)", organize_by_date_var),
            ("Skip hidden files", skip_hidden_var)
        ]
        
        for text, var in options:
            cb = ctk.CTkCheckBox(col1, text=text, variable=var, 
                                onvalue=True, offvalue=False,
                                font=ctk.CTkFont(size=14))
            cb.pack(anchor="w", pady=5)
        
        # Second column (custom tags)
        col2 = ctk.CTkFrame(options_grid, fg_color="transparent")
        col2.pack(side="left", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(col2, text="Custom Tags:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(col2, text="Create additional folders for these tags:",
                    font=ctk.CTkFont(size=13), text_color="gray70").pack(anchor="w")
        
        ctk.CTkEntry(col2, textvariable=custom_tags_var, height=38,
                    placeholder_text="e.g.: project1, important, temp",
                    font=ctk.CTkFont(size=14)).pack(fill="x", pady=(8, 0))

    def _create_size_filter_frame(self, parent, min_size_var, max_size_var, size_unit_var):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="File Size Filter:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 15))
        
        size_frame = ctk.CTkFrame(frame, fg_color="transparent")
        size_frame.pack(fill="x", pady=(0, 10))
        
        # Min size
        ctk.CTkLabel(size_frame, text="Minimum:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        ctk.CTkEntry(size_frame, textvariable=min_size_var, width=100, height=38,
                    font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 15))
        
        # Max size
        ctk.CTkLabel(size_frame, text="Maximum:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        ctk.CTkEntry(size_frame, textvariable=max_size_var, width=100, height=38,
                    font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 15))
        
        # Unit
        ctk.CTkLabel(size_frame, text="Unit:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        unit_menu = ctk.CTkOptionMenu(size_frame, variable=size_unit_var, 
                                     values=["B", "KB", "MB", "GB"], width=80,
                                     font=ctk.CTkFont(size=14), height=38)
        unit_menu.pack(side="left")
        
        # Help text
        ctk.CTkLabel(size_frame, text="(Leave empty for no size limit)", 
                    font=ctk.CTkFont(size=12), text_color="gray70").pack(side="left", padx=(15, 0))
    
    def _load_settings(self):
        """Load settings from configuration"""
        self.organize_by_date_var.set(self.config['organize_by_date'])
        self.move_files_var.set(self.config['move_files'])
        self.create_folders_var.set(self.config['create_folders'])
        self.skip_hidden_var.set(self.config['skip_hidden'])
        self.custom_tags_var.set(self.config['custom_tags'])
        self.folder_var.set(self.config['last_folder'])
        self.manual_assignments = self.config['manual_assignments']
        
        # Load size filter settings
        self.min_size_var.set(self.config.get('min_size', '0'))
        self.max_size_var.set(self.config.get('max_size', ''))
        self.size_unit_var.set(self.config.get('size_unit', 'MB'))
    
    def _save_settings(self):
        """Save current settings to configuration"""
        self.config.update({
            'organize_by_date': self.organize_by_date_var.get(),
            'move_files': self.move_files_var.get(),
            'create_folders': self.create_folders_var.get(),
            'skip_hidden': self.skip_hidden_var.get(),
            'custom_tags': self.custom_tags_var.get(),
            'last_folder': self.folder_var.get(),
            'file_types': self.file_ops.file_types,
            'manual_assignments': self.manual_assignments,
            'min_size': self.min_size_var.get(),
            'max_size': self.max_size_var.get(),
            'size_unit': self.size_unit_var.get()
        })
        self.config_manager.save_config(self.config)
    
    def _convert_size_to_bytes(self, size_str: str, unit: str) -> int:
        if not size_str or not size_str.strip():
            return 0 if unit == 'min' else float('inf')
        
        try:
            size = float(size_str)
            if unit == 'KB':
                return int(size * 1024)
            elif unit == 'MB':
                return int(size * 1024 * 1024)
            elif unit == 'GB':
                return int(size * 1024 * 1024 * 1024)
            else:
                return int(size)  
        except ValueError:
            return 0 if unit == 'min' else float('inf')
    
    def browse_folder(self):
        """Browse for folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)
    
    def on_folder_change(self, *args):
        """Handle folder selection change"""
        folder = self.folder_var.get()
        if folder and os.path.isdir(folder):
            self.update_file_count(folder)
        else:
            self.file_count_var.set("Select a folder to see file count")
    
    def update_file_count(self, folder: str):
        """Update file count display"""
        try:
            min_size = self._convert_size_to_bytes(self.min_size_var.get(), 'min')
            max_size_str = self.max_size_var.get().strip()
            max_size = self._convert_size_to_bytes(max_size_str, self.size_unit_var.get()) if max_size_str else float('inf')
            
            files = self.file_ops.get_files_in_folder(
                folder, self.skip_hidden_var.get(), min_size, max_size
            )
            self.file_count_var.set(f"Found {len(files)} files to organize")
        except Exception:
            self.file_count_var.set("Error reading folder")
    
    def get_folder_statistics(self):
        """Show folder statistics"""
        folder = self.folder_var.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Warning", "Please select a valid folder first.")
            return
        
        try:
            stats = self.file_ops.get_folder_statistics(folder, self.skip_hidden_var.get())
            self._show_folder_statistics(stats)
        except Exception as e:
            messagebox.showerror("Error", f"Error getting folder statistics: {str(e)}")
    
    def _show_folder_statistics(self, stats: Dict):
        """Show folder statistics in a popup window"""
        stats_window = ctk.CTkToplevel(self.root)
        stats_window.title("Folder Statistics")
        stats_window.geometry("400x300")
        self.bring_to_front(stats_window)
        
        frame = ctk.CTkFrame(stats_window, corner_radius=0)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        ctk.CTkLabel(frame, text="Folder Statistics", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0, 20))
        
        # Statistics content
        content = f"""Total Files: {stats['total_files']}
Total Size: {self._format_size(stats['total_size'])}

File Size Distribution:
• Tiny (< 1KB): {stats['size_ranges']['tiny']} files
• Small (1KB - 1MB): {stats['size_ranges']['small']} files
• Medium (1MB - 100MB): {stats['size_ranges']['medium']} files
• Large (100MB - 1GB): {stats['size_ranges']['large']} files
• Huge (> 1GB): {stats['size_ranges']['huge']} files"""
        
        text_widget = ctk.CTkTextbox(frame, wrap="word", height=12, width=40)
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", content)
        text_widget.configure(state="disabled")
        
        # Close button
        ctk.CTkButton(frame, text="Close", command=stats_window.destroy).pack(pady=(10, 0))
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def preview_organization(self):
        """Preview file organization"""
        folder = self.folder_var.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Warning", "Please select a valid folder first.")
            return
        
        try:
            custom_tags = [tag.strip() for tag in self.custom_tags_var.get().split(",") if tag.strip()]
            
            # Get size filter values
            min_size = self._convert_size_to_bytes(self.min_size_var.get(), 'min')
            max_size_str = self.max_size_var.get().strip()
            max_size = self._convert_size_to_bytes(max_size_str, self.size_unit_var.get()) if max_size_str else float('inf')
            
            preview_data = self.file_ops.get_organization_preview(
                folder, custom_tags, self.organize_by_date_var.get(),
                self.skip_hidden_var.get(), self.manual_assignments,
                min_size, max_size
            )
            
            if not preview_data:
                messagebox.showinfo("Preview", "No files found to organize with current filters.")
                return
            
            self._create_preview_window(preview_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error previewing organization: {str(e)}")
            
    def _create_preview_window(self, preview_data: Dict[str, List[str]]) -> None:
        """Create and show preview window with CTk widgets"""
        preview_window = ctk.CTkToplevel(self.root)
        preview_window.title("Organization Preview")
        preview_window.geometry("600x400")
        self.bring_to_front(preview_window)
        
        # Create text widget with scrollbar
        text_frame = ctk.CTkFrame(preview_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        text_widget = ctk.CTkTextbox(text_frame, wrap="word")
        scrollbar = ctk.CTkScrollbar(text_frame, orientation="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Pack text widget and scrollbar
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add preview content
        content = "File Organization Preview:\n\n"
        
        total_files = sum(len(files) for files in preview_data.values())
        content += f"Total files to organize: {total_files}\n\n"
        
        for category, files in preview_data.items():
            content += f"📁 {category} ({len(files)} files):\n"
            for file in files[:5]:  # Show first 5 files
                content += f"   • {file}\n"
            if len(files) > 5:
                content += f"   ... and {len(files) - 5} more files\n"
            content += "\n"
        
        text_widget.insert("1.0", content)
        text_widget.configure(state="disabled")
        
        # Close button
        button_frame = ctk.CTkFrame(preview_window)
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, text="Close", command=preview_window.destroy).pack()
    
    def find_duplicates(self):
        """Find duplicate files in the current folder with multi-select deletion"""
        from datetime import datetime  # Add this import at the top of the method
        
        folder = self.folder_var.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Warning", "Please select a valid folder first.")
            return

        try:
            duplicates = self.smart_features.find_duplicates(folder)
        
            if not duplicates:
                messagebox.showinfo("No Duplicates", "No duplicate files found!")
                return
            
            # Create a window to display duplicates
            dup_window = ctk.CTkToplevel(self.root)
            dup_window.title("Duplicated Files")
            dup_window.geometry("900x650")
            self.bring_to_front(dup_window)
        
            # Main frame
            main_frame = ctk.CTkFrame(dup_window)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Title and instructions
            ctk.CTkLabel(main_frame, 
                        text="Duplicated Files Found", 
                        font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 5))
            
            instructions = ("✓ Check files you want to delete (keep at least one per set)\n"
                             "ⓘ Files grouped below are 100% identical in content"
                             )
            ctk.CTkLabel(main_frame, 
                        text=instructions,
                        font=ctk.CTkFont(size=11),
                        text_color="gray70").pack(pady=(0, 15))
            
            # Create notebook for different groups
            notebook = ctk.CTkTabview(main_frame)
            notebook.pack(fill="both", expand=True, pady=(0, 10))
            
            # Store checkboxes for each file
            file_checkboxes = {}
            
            # Create a tab for each duplicate group
            for group_idx, (hash_val, files) in enumerate(duplicates.items()):
                tab = notebook.add(f"Set {group_idx + 1}")
                
                # Create scrollable frame
                scroll_frame = ctk.CTkScrollableFrame(tab)
                scroll_frame.pack(fill="both", expand=True)
                
                # Header with select all/none for this group
                header_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
                header_frame.pack(fill="x", pady=(0, 5))
                
                ctk.CTkLabel(header_frame, 
                            text=f"Duplicated Set {group_idx + 1} (Identical Files: {len(files)}):",
                            font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
                
                def create_group_toggle(group_files, frame):
                    def toggle_all():
                        # Get current state (if any are unchecked)
                        any_unchecked = any(not file_checkboxes[file][0].get() for file in group_files)
                        # Set all to the opposite state
                        for file in group_files:
                            file_checkboxes[file][0].set(1 if any_unchecked else 0)
                    return toggle_all
                
                toggle_btn = ctk.CTkButton(
                    header_frame,
                    text="Toggle All",
                    command=create_group_toggle(files, scroll_frame),
                    width=80,
                    height=25,
                    font=ctk.CTkFont(size=10)
                )
                toggle_btn.pack(side="right", padx=(10, 0))
                
                # Create checkboxes for each file in the group
                for file in files:
                    frame = ctk.CTkFrame(scroll_frame)
                    frame.pack(fill="x", pady=2)
                    
                    # Store just the filename (not full path)
                    filename = os.path.basename(file)
                    
                    # Create checkbox
                    cb_var = ctk.IntVar(value=0)
                    cb = ctk.CTkCheckBox(
                        frame, 
                        text=filename,
                        variable=cb_var,
                        onvalue=1,
                        offvalue=0
                    )
                    cb.pack(side="left", padx=(0, 10))
                    
                    # Show file info (with error handling)
                    file_path = os.path.join(folder, file)
                    try:
                        stat = os.stat(file_path)
                        size = self._format_size(stat.st_size)
                        mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                        
                        # Size label
                        size_frame = ctk.CTkFrame(frame, fg_color="transparent", width=80)
                        size_frame.pack(side="left", padx=(0, 10))
                        ctk.CTkLabel(size_frame, text=size).pack()
                        
                        # Date label
                        date_frame = ctk.CTkFrame(frame, fg_color="transparent", width=120)
                        date_frame.pack(side="left", padx=(0, 10))
                        ctk.CTkLabel(date_frame, text=mod_time).pack()
                        
                    except Exception as e:
                        # If we can't get file info, just show the filename
                        error_frame = ctk.CTkFrame(frame, fg_color="transparent")
                        error_frame.pack(side="left")
                        ctk.CTkLabel(error_frame, 
                                    text="(Error reading file info)",
                                    text_color="gray70").pack()
                    
                    file_checkboxes[file] = (cb_var, frame)
            
            # Action buttons
            button_frame = ctk.CTkFrame(main_frame)
            button_frame.pack(fill="x", pady=(10, 0))
            
            def delete_selected_duplicates():
                # Verify at least one file is kept in each group
                for group_idx, (hash_val, files) in enumerate(duplicates.items()):
                    selected_for_deletion = sum(file_checkboxes[file][0].get() for file in files)
                    if selected_for_deletion == len(files):
                        messagebox.showerror("Error", 
                                f"You must keep at least one file in Set {group_idx + 1}")
                        notebook.set(f"Set {group_idx + 1}")

                        return
                
                total_to_delete = sum(cb_var.get() for cb_var, _ in file_checkboxes.values())
                if total_to_delete == 0:
                    messagebox.showwarning("Warning", "No files selected for deletion")
                    return
                
                if not messagebox.askyesno("Confirm", 
                                        f"Permanently delete {total_to_delete} selected file(s)?"):
                    return
                
                deleted_count = 0
                errors = []
                
                for file, (cb_var, _) in file_checkboxes.items():
                    if cb_var.get() == 1:  # This file is marked for deletion
                        file_path = os.path.join(folder, file)
                        try:
                            if hasattr(self, 'security_perf') and self.security_perf:
                                self.security_perf.secure_delete(file_path)
                            else:
                                os.remove(file_path)
                            deleted_count += 1
                        except Exception as e:
                            errors.append(f"{os.path.basename(file)}: {str(e)}")
                
                # Show results
                result_msg = f"Successfully deleted {deleted_count} file(s)"
                if errors:
                    result_msg += f"\n\nFailed to delete {len(errors)} file(s):\n" + "\n".join(errors[:3])
                    if len(errors) > 3:
                        result_msg += f"\n...and {len(errors)-3} more"
                
                messagebox.showinfo("Results", result_msg)
                dup_window.destroy()
                self.update_file_count(folder)  # Refresh file count
            
            delete_btn = ctk.CTkButton(
                button_frame, 
                text=f"🗑️ Delete Selected ({sum(cb_var.get() for cb_var, _ in file_checkboxes.values())})",
                command=delete_selected_duplicates,
                fg_color="#FF5555",
                hover_color="#FF0000",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            delete_btn.pack(side="left", padx=(0, 10))
            
            # Update delete count when checkboxes change
            def update_delete_count():
                total = sum(cb_var.get() for cb_var, _ in file_checkboxes.values())
                delete_btn.configure(text=f"🗑️ Delete Selected ({total})")
            
            for cb_var, _ in file_checkboxes.values():
                cb_var.trace_add("write", lambda *_: update_delete_count())
            
            ctk.CTkButton(
                button_frame, 
                text="Close", 
                command=dup_window.destroy
            ).pack(side="right")

        except Exception as e:
            messagebox.showerror("Error", f"Error processing duplicates: {str(e)}")
            
    def organize_files(self):
        """Organize files in the selected folder asynchronously"""
        if self.operation_in_progress:
            messagebox.showwarning("Warning", "An operation is already in progress.")
            return
        
        folder = self.folder_var.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Warning", "Please select a valid folder first.")
            return
        
        # Check folder permissions
        if not self.file_ops.check_folder_permissions(folder):
            messagebox.showerror("Error", "No write permission for the selected folder.")
            return
        
        # Confirm organization
        if not messagebox.askyesno("Confirm", "Are you sure you want to organize the files?"):
            return
        
        try:
            custom_tags = [tag.strip() for tag in self.custom_tags_var.get().split(",") if tag.strip()]
            
            # Get size filter values
            min_size = self._convert_size_to_bytes(self.min_size_var.get(), 'min')
            max_size_str = self.max_size_var.get().strip()
            max_size = self._convert_size_to_bytes(max_size_str, self.size_unit_var.get()) if max_size_str else float('inf')
            
            # Set operation state
            self.operation_in_progress = True
            self.cancel_btn.configure(state="normal")
            
            # Reset progress
            self.progress.set(0)
            self.root.update()
            
            def progress_callback(current: int, total: int):
                """Update progress bar"""
                self.progress.set(current / total)
            
            def status_callback(message: str):
                """Update status message"""
                self.status_var.set(message)
            
            def completion_callback(result, error):
                """Handle completion"""
                self.operation_in_progress = False
                self.current_operation_thread = None
                self.cancel_btn.configure(state="disabled")
                
                if error:
                    messagebox.showerror("Error", f"Error organizing files: {str(error)}")
                    self.status_var.set("Error occurred during organization")
                    self.progress.set(0)
                    return
                
                organized, errors, undo_ops = result
                
                # Store undo operations
                if undo_ops:
                    self.undo_operations = undo_ops
                
                # Save settings
                self._save_settings()
                
                # Show results
                message = f"Organization complete!\n\nFiles organized: {organized}"
                if errors:
                    message += f"\nErrors encountered: {len(errors)}"
                    message += "\n\nFirst few errors:\n" + "\n".join(errors[:5])
                    if len(errors) > 5:
                        message += f"\n... and {len(errors) - 5} more errors"
                
                messagebox.showinfo("Complete", message)
                self.status_var.set("Organization complete!")
                
                # Update file count
                self.update_file_count(folder)
                
                # Reset progress
                self.progress.set(0)
            
            # Start async organization
            self.current_operation_thread = self.file_ops.organize_files_async(
                folder, custom_tags, self.organize_by_date_var.get(),
                self.create_folders_var.get(), self.move_files_var.get(),
                self.skip_hidden_var.get(), self.manual_assignments,
                min_size, max_size,
                progress_callback, status_callback, completion_callback,
                self.root.after
            )
            
        except Exception as e:
            self.operation_in_progress = False
            self.cancel_btn.configure(state="disabled")
            messagebox.showerror("Error", f"Error starting organization: {str(e)}")
            self.status_var.set("Error occurred")
            self.progress.set(0)
    
    def cancel_operation(self):
        """Cancel current operation"""
        if self.operation_in_progress and self.current_operation_thread:
            self.file_ops.cancel_operation()
            self.status_var.set("Cancelling operation...")
    
    def undo_last_operation(self):
        """Undo the last file organization operation asynchronously"""
        if self.operation_in_progress:
            messagebox.showwarning("Warning", "Please wait for current operation to complete.")
            return
        
        if not self.undo_operations:
            messagebox.showinfo("Undo", "No operations to undo.")
            return
        
        if not messagebox.askyesno("Confirm Undo", "Are you sure you want to undo the last operation?"):
            return
        
        try:
            # Set operation state
            self.operation_in_progress = True
            self.cancel_btn.configure(state="normal")
            
            def status_callback(message: str):
                """Update status message"""
                self.status_var.set(message)
            
            def completion_callback(result, error):
                """Handle completion"""
                self.operation_in_progress = False
                self.current_operation_thread = None
                self.cancel_btn.configure(state="disabled")
                
                if error:
                    messagebox.showerror("Error", f"Error during undo: {str(error)}")
                    self.status_var.set("Error occurred during undo")
                    return
                
                undone, errors = result
                
                # Clear undo operations
                self.undo_operations = []
                
                # Show results
                message = f"Undo complete!\n\nOperations undone: {undone}"
                if errors:
                    message += f"\nErrors encountered: {len(errors)}"
                    message += "\n\nErrors:\n" + "\n".join(errors[:5])
                    if len(errors) > 5:
                        message += f"\n... and {len(errors) - 5} more errors"
                
                messagebox.showinfo("Undo Complete", message)
                self.status_var.set("Undo operation complete!")
                
                # Update file count
                folder = self.folder_var.get()
                if folder and os.path.isdir(folder):
                    self.update_file_count(folder)
            
            # Start async undo
            self.current_operation_thread = self.file_ops.undo_operations_async(
                self.undo_operations, status_callback, completion_callback, self.root.after
            )
                
        except Exception as e:
            self.operation_in_progress = False
            self.cancel_btn.configure(state="disabled")
            messagebox.showerror("Error", f"Error starting undo: {str(e)}")
            self.status_var.set("Error occurred")
    
    def open_file_types_editor(self):
        """Open file types editor window"""
        def save_file_types():
            """Save file types configuration"""
            self.file_ops.file_types = self.config['file_types']
            self._save_settings()
        
        self._create_file_types_editor(self.config['file_types'], save_file_types)
    
    def _create_file_types_editor(self, file_types: Dict[str, List[str]], 
                                save_callback: Callable) -> None:
        """Create file types editor window with CTk widgets"""
        editor = ctk.CTkToplevel(self.root)
        editor.title("Edit File Type Categories")
        editor.geometry("600x500")
        self.bring_to_front(editor)

        main_frame = ctk.CTkFrame(editor, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Instructions
        ctk.CTkLabel(main_frame, text="Edit File Type Categories", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(0, 10))
    
        ctk.CTkLabel(main_frame, text="Add extensions with dots (e.g., .pdf, .jpg)", 
                    font=ctk.CTkFont(size=10, slant="italic")).pack(pady=(0, 10))

    # Textbox with scrollbar for displaying file types
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))

        textbox = ctk.CTkTextbox(list_frame, width=70, height=15)
        textbox.pack(side="left", fill="both", expand=True)

    # Disable text editing directly in the textbox
        textbox.configure(state="disabled")

    # Populate textbox
        def refresh_textbox():
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            for category, extensions in file_types.items():
                textbox.insert("end", f"{category}: {', '.join(extensions)}\n")
            textbox.configure(state="disabled")
        # Store the current items for selection tracking
            textbox._items = list(file_types.items())

        refresh_textbox()

    # Entry fields
        entry_frame = ctk.CTkFrame(main_frame)
        entry_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(entry_frame, text="Category Name:").grid(row=0, column=0, sticky="w", pady=2)
        cat_var = ctk.StringVar()
        ctk.CTkEntry(entry_frame, textvariable=cat_var, width=200).grid(row=0, column=1, sticky="w", padx=(10, 0))

        ctk.CTkLabel(entry_frame, text="Extensions:").grid(row=1, column=0, sticky="w", pady=2)
        ext_var = ctk.StringVar()
        ctk.CTkEntry(entry_frame, textvariable=ext_var, width=200).grid(row=1, column=1, sticky="w", padx=(10, 0))

    # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")

        def add_edit_type():
            category = cat_var.get().strip()
            extensions_text = ext_var.get().strip()
        
            if not category or not extensions_text:
                messagebox.showerror("Error", "Both category name and extensions must be filled.")
                return
        
        # Process extensions
            extensions = []
            for ext in extensions_text.split(','):
                ext = ext.strip().lower()
                if ext and not ext.startswith('.'):
                    ext = '.' + ext
                if ext:
                    extensions.append(ext)
        
            if not extensions:
                messagebox.showerror("Error", "Please provide valid extensions.")
                return
            
            file_types[category] = extensions
            refresh_textbox()
            save_callback()
            cat_var.set("")
            ext_var.set("")
            messagebox.showinfo("Success", f"Category '{category}' saved successfully!")

        ctk.CTkButton(button_frame, text="➕ Add/Update Category", 
                  command=add_edit_type).pack(side="left", padx=(0, 10))

        def remove_type():
            if not hasattr(textbox, "_items") or not textbox._items:
                messagebox.showwarning("Warning", "No categories to remove.")
                return
            
        # Get the current cursor position
            cursor_pos = textbox.index("insert")
            line_num = int(cursor_pos.split('.')[0]) - 1
        
            if 0 <= line_num < len(textbox._items):
                cat, _ = textbox._items[line_num]
                if messagebox.askyesno("Confirm", f"Remove category '{cat}'?"):
                    file_types.pop(cat, None)
                    refresh_textbox()
                    save_callback()
                    messagebox.showinfo("Success", f"Category '{cat}' removed successfully!")
            else:
                messagebox.showwarning("Warning", "Please click on a category to select it.")

        ctk.CTkButton(button_frame, text="🗑️ Remove Selected", 
                    command=remove_type).pack(side="left", padx=(0, 10))

        def load_selection():
            if not hasattr(textbox, "_items") or not textbox._items:
                return
            
            cursor_pos = textbox.index("insert")
            line_num = int(cursor_pos.split('.')[0]) - 1
        
            if 0 <= line_num < len(textbox._items):
                cat, extensions = textbox._items[line_num]
                cat_var.set(cat)
                ext_var.set(', '.join(extensions))

        ctk.CTkButton(button_frame, text="📝 Edit Selected", 
                    command=load_selection).pack(side="left")

        # Bind double-click to edit
        textbox.bind('<Double-1>', lambda e: load_selection())
    
    def open_manual_assignment_window(self):
        """Open manual file assignment window"""
        folder = self.folder_var.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Warning", "Please select a valid folder first.")
            return
        
        try:
            # Get size filter values
            min_size = self._convert_size_to_bytes(self.min_size_var.get(), 'min')
            max_size_str = self.max_size_var.get().strip()
            max_size = self._convert_size_to_bytes(max_size_str, self.size_unit_var.get()) if max_size_str else float('inf')
            
            files = self.file_ops.get_files_in_folder(
                folder, self.skip_hidden_var.get(), min_size, max_size
            )
            
            if not files:
                messagebox.showinfo("No Files", "No files found in the selected folder with current filters.")
                return
            
            def save_assignments(assignments: Dict[str, str]):
                """Save manual assignments"""
                self.manual_assignments = assignments
                self._save_settings()
                messagebox.showinfo("Saved", "Manual assignments saved successfully!")
            
            self._create_manual_assignment_window(
                files, self.config['file_types'], self.custom_tags_var.get(),
                self.manual_assignments, save_assignments
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error opening manual assignment window: {str(e)}")
    
    def _create_manual_assignment_window(self, files: List[str], file_types: Dict[str, List[str]],
                                        custom_tags: str, manual_assignments: Dict[str, str],
                                        save_callback: Callable) -> None:
        """Create enhanced manual file assignment window with multi-select"""
        win = ctk.CTkToplevel(self.root)
        win.title("Manual File Assignment")
        win.geometry("860x680")
        self.bring_to_front(win)

        # Store current folder path
        current_folder = self.folder_var.get()

        def get_available_categories():
            """Get all available categories including subfolders"""
            # Get predefined categories from file types
            categories = list(file_types.keys())
        
            # Add custom tags
            categories.extend([tag.strip() for tag in custom_tags.split(",") if tag.strip()])
        
            # Add existing subfolders as categories
            try:
                subfolders = [f for f in os.listdir(current_folder) 
                            if os.path.isdir(os.path.join(current_folder, f))]
                categories.extend(subfolders)
            except Exception:
                pass
            
            # Add "None" option
            categories.append("None")
        
            return sorted(list(set(categories)))  # Remove duplicates and sort

        # Create category_var here so it's accessible to all functions
        category_var = ctk.StringVar(value="None")
        category_combo = None  # Initialize as None, will be created in the interface

        def refresh_categories():
            """Refresh the category dropdown with current folders"""
            nonlocal category_combo
            if category_combo is None:
                return
                
            current_cat = category_var.get()
            categories = get_available_categories()
            category_combo.configure(values=categories)
            if current_cat in categories:
                category_var.set(current_cat)
            else:
                category_var.set("None")

        main_frame = ctk.CTkFrame(win, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title and instructions
        ctk.CTkLabel(main_frame, text="Manual File Assignment", 
                font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0, 5))

        info_text = ("Select files and assign categories. Use Ctrl+Click for multiple selection.\n"
                "You can assign categories to multiple files at once.")
        ctk.CTkLabel(main_frame, text=info_text, 
                font=ctk.CTkFont(size=10, slant="italic")).pack(pady=(0, 15))

        # Create notebook for different views
        notebook = ctk.CTkTabview(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 10))

        # Multi-select tab
        multi_frame = notebook.add("Multi-Select Assignment")

        # Create multi-select interface - pass category_var and get back category_combo
        category_combo = self._create_multi_select_interface(multi_frame, files, file_types, 
                            custom_tags, manual_assignments, save_callback, category_var)

        # Bottom buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))

        # Left side buttons (creation)
        left_button_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        left_button_frame.pack(side="left")

        def create_new_folder():
            """Create a new folder in the current directory"""
            dialog = ctk.CTkInputDialog(
                text="Enter folder name:", 
                title="Create New Folder"
            )
            folder_name = dialog.get_input()
        
            if not folder_name:  # User cancelled
                return
        
            try:
                # Validate folder name
                if not folder_name.strip():
                    raise ValueError("Folder name cannot be empty")
                if any(c in folder_name for c in '<>:"/\\|?*'):
                    raise ValueError("Folder name contains invalid characters")
            
                # Create full path
                folder_path = os.path.join(current_folder, folder_name)
            
                # Create the folder
                os.makedirs(folder_path, exist_ok=True)
            
                # Automatically add to categories and select it
                refresh_categories()
                category_var.set(folder_name)
                messagebox.showinfo("Success", f"Created new folder: {folder_name}")
        
            except Exception as e:
                messagebox.showerror("Error", f"Could not create folder: {str(e)}")

        def delete_selected_folder():
            """Delete the currently selected folder"""
            selected_category = category_var.get()
            
            if selected_category == "None":
                messagebox.showwarning("Warning", "Please select a folder to delete")
                return
            
            # Check if this is a predefined category
            is_predefined = (selected_category in file_types.keys() or 
                            selected_category in [tag.strip() for tag in custom_tags.split(",") if tag.strip()])
            
            if is_predefined:
                messagebox.showwarning("Warning", "Cannot delete predefined categories")
                return
            
            # Confirm deletion
            if not messagebox.askyesno("Confirm", f"Delete folder '{selected_category}' and all its contents?"):
                return
            
            try:
                folder_path = os.path.join(current_folder, selected_category)
                
                # First remove all files from manual assignments that are in this folder
                for file in list(manual_assignments.keys()):
                    if manual_assignments[file] == selected_category:
                        manual_assignments.pop(file)
                
                # Delete the folder and its contents
                import shutil
                shutil.rmtree(folder_path)
                
                # Refresh categories and reset selection
                refresh_categories()
                messagebox.showinfo("Success", f"Deleted folder: {selected_category}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete folder: {str(e)}")

        ctk.CTkButton(left_button_frame, text="📁 New Folder", 
                    command=create_new_folder).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(left_button_frame, text="🗑️ Delete Folder", 
                    command=delete_selected_folder).pack(side="left", padx=(0, 10))

        # Right side buttons (actions)
        right_button_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        right_button_frame.pack(side="right")

        def save_and_close():
            save_callback(manual_assignments)
            win.destroy()

        ctk.CTkButton(right_button_frame, text="💾 Save & Close", 
                command=save_and_close).pack(side="left", padx=(0, 10))

        ctk.CTkButton(right_button_frame, text="❌ Cancel", 
                command=win.destroy).pack(side="left")

        def clear_all():
            if messagebox.askyesno("Confirm", "Clear all manual assignments?"):
                manual_assignments.clear()
                messagebox.showinfo("Cleared", "All manual assignments cleared!")
                win.destroy()

        ctk.CTkButton(left_button_frame, text="🗑️ Clear All", 
                    command=clear_all).pack(side="left")

    def _create_multi_select_interface(self, parent: ctk.CTkFrame, files: List[str], 
                                    file_types: Dict[str, List[str]], custom_tags: str,
                                    manual_assignments: Dict[str, str], save_callback: Callable,
                                    category_var: ctk.StringVar) -> ctk.CTkOptionMenu:
        """Create multi-select assignment interface with folder categories and search"""
        current_folder = self.folder_var.get()

        def get_available_categories():
            categories = list(file_types.keys())
            categories.extend([tag.strip() for tag in custom_tags.split(",") if tag.strip()])
            try:
                subfolders = [f for f in os.listdir(current_folder) 
                            if os.path.isdir(os.path.join(current_folder, f))]
                categories.extend(subfolders)
            except Exception:
                pass
            categories.append("None")
            return sorted(list(set(categories)))

        # Files listbox with multi-select (using CTkScrollableFrame)
        files_frame = ctk.CTkFrame(parent)
        files_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Search Bar
        search_frame = ctk.CTkFrame(files_frame)
        search_frame.pack(fill="x", pady=(0, 5))

        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=search_var, placeholder_text="Search files...")
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Automatically search on every keystroke
        search_var.trace_add("write", lambda *args: search_files())


        scroll_frame = ctk.CTkScrollableFrame(files_frame)
        scroll_frame.pack(fill="both", expand=True)

        # Create checkboxes for each file
        file_checkboxes = {}
        file_frames = {}

        def create_file_entry(file):
            current_assignment = manual_assignments.get(file, "None")
            frame = ctk.CTkFrame(scroll_frame)
            frame.pack(fill="x", pady=2)
            var = ctk.IntVar(value=0)
            cb = ctk.CTkCheckBox(frame, text="", variable=var)
            cb.pack(side="left", padx=(0, 10))
            label = ctk.CTkLabel(frame, text=f"{file} → {current_assignment}", anchor="w")
            label.pack(side="left", fill="x", expand=True)
            file_checkboxes[file] = (var, label)
            file_frames[file] = frame

        for file in files:
            create_file_entry(file)

        def search_files():
            keyword = search_var.get().lower()
            for file, frame in file_frames.items():
                if keyword in file.lower():
                    frame.pack(fill="x", pady=2)
                else:
                    frame.pack_forget()


        # Category assignment frame
        assign_frame = ctk.CTkFrame(parent)
        assign_frame.pack(fill="x")

        categories = get_available_categories()

        ctk.CTkLabel(assign_frame, text="Select Category:").pack(anchor="w")
        category_combo = ctk.CTkOptionMenu(assign_frame, variable=category_var, values=categories)
        category_combo.pack(anchor="w", pady=(5, 10))

        def assign_to_selected():
            selected_files = []
            for file, (var, label) in file_checkboxes.items():
                if var.get() == 1:
                    selected_files.append(file)

            if not selected_files:
                messagebox.showwarning("Warning", "Please select files to assign.")
                return

            category = category_var.get()
            assigned_files = []

            for file in selected_files:
                if category == "None":
                    manual_assignments.pop(file, None)
                else:
                    manual_assignments[file] = category
                assigned_files.append(file)

                current_assignment = manual_assignments.get(file, "None")
                file_checkboxes[file][1].configure(text=f"{file} → {current_assignment}")

            if category != "None" and category not in file_types.keys() and \
            category not in [tag.strip() for tag in custom_tags.split(",") if tag.strip()]:
                save_callback(manual_assignments)

            messagebox.showinfo("Success", f"Assigned {len(assigned_files)} files to '{category}'")

        ctk.CTkButton(assign_frame, text="✅ Assign to Selected Files", 
                command=assign_to_selected).pack(anchor="w", pady=(0, 5))

        def update_selection_info():
            selected_count = sum(var.get() for var, _ in file_checkboxes.values())
            selection_info.set(f"Selected: {selected_count} files")

        selection_info = ctk.StringVar(value="Selected: 0 files")
        ctk.CTkLabel(assign_frame, textvariable=selection_info, 
                font=ctk.CTkFont(size=10, slant="italic")).pack(anchor="w")

        for var, _ in file_checkboxes.values():
            var.trace_add("write", lambda *args: update_selection_info())

        filter_frame = ctk.CTkFrame(assign_frame)
        filter_frame.pack(fill="x", pady=(10, 0))

        def select_unassigned():
            for file, (var, _) in file_checkboxes.items():
                var.set(1 if file not in manual_assignments else 0)
            update_selection_info()

        def select_all():
            for var, _ in file_checkboxes.values():
                var.set(1)
            update_selection_info()

        def clear_selection():
            for var, _ in file_checkboxes.values():
                var.set(0)
            update_selection_info()

        ctk.CTkButton(filter_frame, text="📝 Select Unassigned", 
                command=select_unassigned).pack(side="left", padx=(0, 5))
        ctk.CTkButton(filter_frame, text="🔍 Select All", 
                command=select_all).pack(side="left", padx=(0, 5))
        ctk.CTkButton(filter_frame, text="❌ Clear Selection", 
                command=clear_selection).pack(side="left")

        return category_combo

    
    def run(self):
        """Start the application"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            # Save settings on exit
            self._save_settings()
    
    def on_closing(self):
        """Handle application closing"""
        if self.operation_in_progress:
            if messagebox.askyesno("Confirm Exit", "An operation is in progress. Do you want to cancel it and exit?"):
                self.file_ops.cancel_operation()
                self.root.after(1000, self.root.destroy)  # Give time for cancellation
            return
        
        self._save_settings()
        self.root.destroy()

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