
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import Dict, List, Callable
from PIL import Image
from datetime import datetime

class MainWindow:
    """Main UI window for File Organizer application"""
    
    def __init__(self, app_controller):
        self.app = app_controller
        self.root = ctk.CTk()
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize UI variables
        self._init_variables()
        
        # Setup window
        self._setup_window()
        
        # Load icons first
        self._load_icons()
        
        # Create UI (which now can use the loaded icons)
        self._create_ui()
    
    def _init_variables(self):
        """Initialize UI variables"""
        self.folder_var = ctk.StringVar()
        self.create_folders_var = ctk.BooleanVar(value=True)
        self.move_files_var = ctk.BooleanVar(value=True)
        self.organize_by_date_var = ctk.BooleanVar()
        self.skip_hidden_var = ctk.BooleanVar(value=True)
        self.custom_tags_var = ctk.StringVar()
        self.file_count_var = ctk.StringVar(value="Select a folder to see file count")
        self.status_var = ctk.StringVar(value="Ready to organize files!")
        self.min_size_var = ctk.StringVar(value="0")
        self.max_size_var = ctk.StringVar(value="")
        self.size_unit_var = ctk.StringVar(value="MB")
        
        # Initialize icons dictionary
        self.icons = {}
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(self.root, mode='determinate', height=6)
        
        # Bind folder selection change
        self.folder_var.trace('w', self._on_folder_change)
    
    def _setup_window(self):
        """Setup main window properties"""
        self.root.title("File Organizer")
        self.root.geometry("1000x700")
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'app_logo.ico')
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
    
    def _load_icons(self):
        """Load application icons"""
        self.icons = {}
        icon_names = ["folder", "manual", "statistics", "file", "duplicates", "undo", 
                     "preview", "rocket", "cancel", "settings"]
        
        for icon_name in icon_names:
            try:
                icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', f'{icon_name}.png')
                if os.path.exists(icon_path):
                    self.icons[icon_name] = ctk.CTkImage(Image.open(icon_path), size=(20, 20))
                else:
                    self.icons[icon_name] = None
            except Exception:
                self.icons[icon_name] = None
    
    def _create_ui(self):
        """Create the main UI layout"""
        # Main container
        main_container = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        main_container.pack(fill="both", expand=True)
        
        # Create sidebar and content
        self._create_sidebar(main_container)
        self._create_content_area(main_container)
    
    def _create_sidebar(self, parent):
        """Create application sidebar"""
        sidebar = ctk.CTkFrame(parent, width=200, corner_radius=0)
        sidebar.pack(side="left", fill="y", padx=(0, 10), pady=10)
        sidebar.pack_propagate(False)
        
        # Title
        title_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        title_frame.pack(pady=(10, 20))
        
        ctk.CTkLabel(title_frame, text="File Organizer", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="center")
        
        # Sidebar buttons
        sidebar_buttons = [
            ("Browse Folder", self.app.browse_folder, "folder"),
            ("Manual Assign", self.app.open_manual_assignment_window, "manual"),
            ("Statistics", self.app.get_folder_statistics, "statistics"),
            ("File Types", self.app.open_file_types_editor, "file"),
            ("Find Duplicates", self.app.find_duplicates, "duplicates"),
            ("Undo Last", self.app.undo_last_operation, "undo")
        ]
        
        for text, command, icon_name in sidebar_buttons:
            btn = ctk.CTkButton(
                sidebar, text=text, command=command, corner_radius=5, 
                anchor="w", height=40, image=self.icons.get(icon_name),
                compound="left", font=ctk.CTkFont(size=13)
            )
            btn.pack(fill="x", padx=5, pady=2)
        
        # Version info
        ctk.CTkLabel(sidebar, text="", height=20).pack(side="bottom", fill="x")
        ctk.CTkLabel(sidebar, text="Version 2.0", 
                    font=ctk.CTkFont(size=10), text_color="gray70").pack(side="bottom", pady=(0, 10))
    
    def _create_content_area(self, parent):
        """Create main content area"""
        content_frame = ctk.CTkFrame(parent, corner_radius=10)
        content_frame.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)
        
        # Header
        self._create_header(content_frame)
        
        # Folder selection
        self._create_folder_selection(content_frame)
        
        # Options tabs
        self._create_options_tabs(content_frame)
        
        # File count and progress
        self._create_progress_section(content_frame)
        
        # Action buttons
        self._create_action_buttons(content_frame)
        
        # Status bar
        self._create_status_bar(content_frame)
    
    def _create_header(self, parent):
        """Create header section"""
        header_content = ctk.CTkFrame(parent, fg_color="transparent")
        header_content.pack(fill="x", pady=(15, 5), padx=20)
        
        ctk.CTkLabel(header_content, text="Organize Your Files", 
                    font=ctk.CTkFont(size=27, weight="bold")).pack(pady=(0, 5))
        
        ctk.CTkLabel(header_content, text="Automatically sort files into categorized folders",
                    font=ctk.CTkFont(size=12), text_color="gray70").pack()
    
    def _create_folder_selection(self, parent):
        """Create folder selection section"""
        frame = ctk.CTkFrame(parent, height=70)
        frame.pack(fill="x", pady=(0, 15), padx=20)
        
        ctk.CTkLabel(frame, text="Folder to Organize:", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=15, pady=(9, 3))
        
        entry_frame = ctk.CTkFrame(frame, fg_color="transparent")
        entry_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        entry = ctk.CTkEntry(entry_frame, textvariable=self.folder_var, height=42,
                            font=ctk.CTkFont(size=14), corner_radius=6)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        button = ctk.CTkButton(entry_frame, text="Browse", 
                              command=self._browse_folder_internal, width=90, height=42,
                              font=ctk.CTkFont(size=12))
        button.pack(side="right")
    
    def _create_options_tabs(self, parent):
        """Create options tabview"""
        tabview = ctk.CTkTabview(parent, height=300)
        tabview.pack(fill="x", padx=20, pady=(0, 15))
        
        # Basic Options Tab
        basic_tab = tabview.add("Organization Options")
        self._create_basic_options(basic_tab)
        
        # Advanced Options Tab (if needed in future)
        # advanced_tab = tabview.add("Advanced")
        # self._create_advanced_options(advanced_tab)
    
    def _create_basic_options(self, parent):
        """Create basic options in tab"""
        options_frame = ctk.CTkFrame(parent, fg_color="transparent")
        options_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Options grid layout
        options_grid = ctk.CTkFrame(options_frame, fg_color="transparent")
        options_grid.pack(fill="x", pady=(0, 15))
        
        # First column - Basic Settings
        col1 = ctk.CTkFrame(options_grid, fg_color="transparent")
        col1.pack(side="left", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(col1, text="Basic Settings:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        options = [
            ("Create category folders", self.create_folders_var),
            ("Move files (instead of copy)", self.move_files_var),
            ("Organize by date (YYYY-MM)", self.organize_by_date_var),
            ("Skip hidden files", self.skip_hidden_var)
        ]
        
        for text, var in options:
            cb = ctk.CTkCheckBox(col1, text=text, variable=var, 
                                font=ctk.CTkFont(size=14))
            cb.pack(anchor="w", pady=5)
        
        # Second column - Custom Tags
        col2 = ctk.CTkFrame(options_grid, fg_color="transparent")
        col2.pack(side="left", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(col2, text="Custom Tags:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(col2, text="Create additional folders for these tags:",
                    font=ctk.CTkFont(size=13), text_color="gray70").pack(anchor="w")
        
        ctk.CTkEntry(col2, textvariable=self.custom_tags_var, height=38,
                    placeholder_text="e.g.: project1, important, temp",
                    font=ctk.CTkFont(size=14)).pack(fill="x", pady=(8, 0))
        
        # Size filtering section
        self._create_size_filter(options_frame)
    
    def _create_size_filter(self, parent):
        """Create size filtering section"""
        size_frame = ctk.CTkFrame(parent, fg_color="transparent")
        size_frame.pack(fill="x", pady=(15, 0))
        
        ctk.CTkLabel(size_frame, text="File Size Filter:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        filter_controls = ctk.CTkFrame(size_frame, fg_color="transparent")
        filter_controls.pack(fill="x")
        
        # Min size
        ctk.CTkLabel(filter_controls, text="Min:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        ctk.CTkEntry(filter_controls, textvariable=self.min_size_var, width=80, height=32,
                    font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 15))
        
        # Max size
        ctk.CTkLabel(filter_controls, text="Max:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        ctk.CTkEntry(filter_controls, textvariable=self.max_size_var, width=80, height=32,
                    font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 15))
        
        # Unit
        ctk.CTkLabel(filter_controls, text="Unit:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        ctk.CTkOptionMenu(filter_controls, variable=self.size_unit_var, 
                         values=["B", "KB", "MB", "GB"], width=70, height=32,
                         font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 15))
        
        # Help text
        ctk.CTkLabel(filter_controls, text="(Leave empty for no limit)", 
                    font=ctk.CTkFont(size=12), text_color="gray70").pack(side="left")
    
    def _create_progress_section(self, parent):
        """Create progress and file count section"""
        # File count
        ctk.CTkLabel(parent, textvariable=self.file_count_var, 
                    font=ctk.CTkFont(size=13)).pack(pady=(5, 0), padx=20, anchor="w")
        
        # Progress bar
        self.progress.pack(fill="x", padx=20, pady=(10, 5))
    
    def _create_action_buttons(self, parent):
        """Create action buttons section"""
        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=(5, 10))
        
        # Preview button
        ctk.CTkButton(
            action_frame, text="   Preview Changes", command=self.app.preview_organization,
            fg_color="#3a7ebf", hover_color="#2d5985", height=38, width=180,
            font=ctk.CTkFont(size=13), image=self.icons.get("preview"),
            compound="left", anchor="center"
        ).pack(side="left", padx=(0, 10))
        
        # Organize button
        ctk.CTkButton(
            action_frame, text="   Organize Files", command=self.app.organize_files,
            fg_color="#2CC985", hover_color="#27AE60", height=38, width=180,
            font=ctk.CTkFont(size=13, weight="bold"), image=self.icons.get("rocket"),
            compound="left", anchor="center"
        ).pack(side="left", padx=(0, 10))
        
        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            action_frame, text="   Cancel", command=self.app.cancel_operation,
            state="disabled", height=38, width=120, font=ctk.CTkFont(size=13),
            image=self.icons.get("cancel"), compound="left", anchor="center"
        )
        self.cancel_btn.pack(side="left")
    
    def _create_status_bar(self, parent):
        """Create status bar section"""
        status_frame = ctk.CTkFrame(parent, height=36, corner_radius=0)
        status_frame.pack(fill="x", side="bottom", padx=0, pady=0)
        
        # Top border
        ctk.CTkFrame(status_frame, height=1, fg_color="#333333").pack(fill="x", pady=(0, 5))
        
        # Status label
        status_label = ctk.CTkLabel(status_frame, textvariable=self.status_var,
                                  font=ctk.CTkFont(size=11), anchor="w")
        status_label.pack(side="left", padx=10)
        
        # Footer
        ctk.CTkLabel(status_frame, text="© 2025 File Organizer | A project by mggyslz",
                    font=ctk.CTkFont(size=11), text_color="gray70",
                    anchor="center", height=25).pack(side="bottom", fill="x", pady=(0, 5))
    
    # =============================================================================
    # Event Handlers
    # =============================================================================
    
    def _browse_folder_internal(self):
        """Internal browse folder handler"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)
    
    def _on_folder_change(self, *args):
        """Handle folder selection change"""
        folder = self.folder_var.get()
        if folder and os.path.isdir(folder):
            self.app.update_file_count(folder)
        else:
            self.file_count_var.set("Select a folder to see file count")
    
    # =============================================================================
    # Public Interface Methods
    # =============================================================================
    
    def browse_folder(self):
        """Public method to browse for folder"""
        return filedialog.askdirectory()
    
    def get_selected_folder(self):
        """Get currently selected folder"""
        return self.folder_var.get()
    
    def set_file_count(self, count_text: str):
        """Set file count display"""
        self.file_count_var.set(count_text)
    
    def set_status(self, status_text: str):
        """Set status bar text"""
        self.status_var.set(status_text)
    
    def update_progress(self, current: int, total: int):
        """Update progress bar"""
        if total > 0:
            self.progress.set(current / total)
        else:
            self.progress.set(0)
    
    def reset_progress(self):
        """Reset progress bar"""
        self.progress.set(0)
    
    def set_operation_state(self, in_progress: bool):
        """Enable/disable UI elements based on operation state"""
        # Enable/disable cancel button
        self.cancel_btn.configure(state="normal" if in_progress else "disabled")
        
        # TODO: Add logic to disable other buttons during operation if needed
    
    def get_current_settings(self) -> Dict:
        """Get current UI settings"""
        return {
            'organize_by_date': self.organize_by_date_var.get(),
            'move_files': self.move_files_var.get(),
            'create_folders': self.create_folders_var.get(),
            'skip_hidden': self.skip_hidden_var.get(),
            'custom_tags': self.custom_tags_var.get(),
            'last_folder': self.folder_var.get(),
            'min_size': self.min_size_var.get(),
            'max_size': self.max_size_var.get(),
            'size_unit': self.size_unit_var.get()
        }
    
    def load_settings(self, settings: Dict):
        """Load settings into UI"""
        self.organize_by_date_var.set(settings.get('organize_by_date', False))
        self.move_files_var.set(settings.get('move_files', True))
        self.create_folders_var.set(settings.get('create_folders', True))
        self.skip_hidden_var.set(settings.get('skip_hidden', True))
        self.custom_tags_var.set(settings.get('custom_tags', ''))
        self.folder_var.set(settings.get('last_folder', ''))
        self.min_size_var.set(settings.get('min_size', '0'))
        self.max_size_var.set(settings.get('max_size', ''))
        self.size_unit_var.set(settings.get('size_unit', 'MB'))
    
    # =============================================================================
    # Dialog Windows
    # =============================================================================
    
    def show_folder_statistics(self, stats: Dict):
        """Show folder statistics window"""
        stats_window = ctk.CTkToplevel(self.root)
        stats_window.title("Folder Statistics")
        stats_window.geometry("400x300")
        self._bring_to_front(stats_window)
        
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
    
    def show_preview(self, preview_data: Dict[str, List[str]]):
        """Show organization preview window"""
        preview_window = ctk.CTkToplevel(self.root)
        preview_window.title("Organization Preview")
        preview_window.geometry("600x400")
        self._bring_to_front(preview_window)
        
        # Create text widget with scrollbar
        text_frame = ctk.CTkFrame(preview_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        text_widget = ctk.CTkTextbox(text_frame, wrap="word")
        text_widget.pack(fill="both", expand=True)
        
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
    
    def show_duplicates(self, duplicates: Dict, folder: str, security_perf=None):
        """Show duplicates management window"""
        dup_window = ctk.CTkToplevel(self.root)
        dup_window.title("Duplicate Files")
        dup_window.geometry("900x650")
        self._bring_to_front(dup_window)
        
        main_frame = ctk.CTkFrame(dup_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title and instructions
        ctk.CTkLabel(main_frame, text="Duplicate Files Found", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 5))
        
        instructions = ("✓ Check files you want to delete (keep at least one per set)\n"
                       "ⓘ Files grouped below are 100% identical in content")
        ctk.CTkLabel(main_frame, text=instructions, font=ctk.CTkFont(size=11),
                    text_color="gray70").pack(pady=(0, 15))
        
        # Create notebook for different groups
        notebook = ctk.CTkTabview(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        file_checkboxes = {}
        
        # Create tabs for each duplicate group
        for group_idx, (hash_val, files) in enumerate(duplicates.items()):
            tab = notebook.add(f"Set {group_idx + 1}")
            scroll_frame = ctk.CTkScrollableFrame(tab)
            scroll_frame.pack(fill="both", expand=True)
            
            # Header with toggle all button
            header_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            header_frame.pack(fill="x", pady=(0, 5))
            
            ctk.CTkLabel(header_frame, 
                        text=f"Duplicate Set {group_idx + 1} ({len(files)} files):",
                        font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
            
            def create_toggle_func(group_files):
                def toggle_all():
                    any_unchecked = any(not file_checkboxes[file][0].get() for file in group_files)
                    for file in group_files:
                        file_checkboxes[file][0].set(1 if any_unchecked else 0)
                return toggle_all
            
            toggle_btn = ctk.CTkButton(header_frame, text="Toggle All",
                                     command=create_toggle_func(files),
                                     width=80, height=25, font=ctk.CTkFont(size=10))
            toggle_btn.pack(side="right", padx=(10, 0))
            
            # Create checkboxes for each file
            for file in files:
                file_frame = ctk.CTkFrame(scroll_frame)
                file_frame.pack(fill="x", pady=2)
                
                filename = os.path.basename(file)
                cb_var = ctk.IntVar(value=0)
                cb = ctk.CTkCheckBox(file_frame, text=filename, variable=cb_var)
                cb.pack(side="left", padx=(0, 10))
                
                # Show file info
                self._add_file_info(file_frame, os.path.join(folder, file))
                file_checkboxes[file] = (cb_var, file_frame)
        
        # Action buttons
        self._create_duplicate_action_buttons(main_frame, dup_window, duplicates, 
                                            file_checkboxes, folder, security_perf)
    
    def _add_file_info(self, parent, file_path):
        """Add file information labels"""
        try:
            stat = os.stat(file_path)
            size = self._format_size(stat.st_size)
            mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            
            size_frame = ctk.CTkFrame(parent, fg_color="transparent", width=80)
            size_frame.pack(side="left", padx=(0, 10))
            ctk.CTkLabel(size_frame, text=size).pack()
            
            date_frame = ctk.CTkFrame(parent, fg_color="transparent", width=120)
            date_frame.pack(side="left", padx=(0, 10))
            ctk.CTkLabel(date_frame, text=mod_time).pack()
            
        except Exception:
            error_frame = ctk.CTkFrame(parent, fg_color="transparent")
            error_frame.pack(side="left")
            ctk.CTkLabel(error_frame, text="(Error reading file info)",
                        text_color="gray70").pack()
    
    def _create_duplicate_action_buttons(self, parent, window, duplicates, file_checkboxes, folder, security_perf):
        """Create action buttons for duplicate management"""
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", pady=(10, 0))
        
        def delete_selected_duplicates():
            # Verify at least one file is kept in each group
            for group_idx, (hash_val, files) in enumerate(duplicates.items()):
                selected_for_deletion = sum(file_checkboxes[file][0].get() for file in files)
                if selected_for_deletion == len(files):
                    messagebox.showerror("Error", f"You must keep at least one file in Set {group_idx + 1}")
                    return
            
            total_to_delete = sum(cb_var.get() for cb_var, _ in file_checkboxes.values())
            if total_to_delete == 0:
                messagebox.showwarning("Warning", "No files selected for deletion")
                return
            
            if not messagebox.askyesno("Confirm", f"Permanently delete {total_to_delete} selected file(s)?"):
                return
            
            deleted_count = 0
            errors = []
            
            for file, (cb_var, _) in file_checkboxes.items():
                if cb_var.get() == 1:
                    file_path = os.path.join(folder, file)
                    try:
                        if security_perf:
                            security_perf.secure_delete(file_path)
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
            window.destroy()
            # Update file count in main window
            self.app.update_file_count(folder)
        
        # Update delete count dynamically
        def update_delete_count():
            total = sum(cb_var.get() for cb_var, _ in file_checkboxes.values())
            delete_btn.configure(text=f"🗑️ Delete Selected ({total})")
        
        delete_btn = ctk.CTkButton(button_frame, text=f"🗑️ Delete Selected (0)",
                                  command=delete_selected_duplicates,
                                  fg_color="#FF5555", hover_color="#FF0000",
                                  font=ctk.CTkFont(size=12, weight="bold"))
        delete_btn.pack(side="left", padx=(0, 10))
        
        # Bind checkbox changes to update count
        for cb_var, _ in file_checkboxes.values():
            cb_var.trace_add("write", lambda *_: update_delete_count())
        
        ctk.CTkButton(button_frame, text="Close", command=window.destroy).pack(side="right")
    
    def show_file_types_editor(self, file_types: Dict[str, List[str]], save_callback: Callable):
        """Show file types editor window"""
        editor = ctk.CTkToplevel(self.root)
        editor.title("Edit File Type Categories")
        editor.geometry("600x500")
        self._bring_to_front(editor)

        main_frame = ctk.CTkFrame(editor, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Instructions
        ctk.CTkLabel(main_frame, text="Edit File Type Categories", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="Add extensions with dots (e.g., .pdf, .jpg)", 
                    font=ctk.CTkFont(size=10, slant="italic")).pack(pady=(0, 10))

        # Textbox for displaying file types
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))

        textbox = ctk.CTkTextbox(list_frame, width=70, height=15)
        textbox.pack(fill="both", expand=True)
        textbox.configure(state="disabled")

        # Populate and refresh textbox
        def refresh_textbox():
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            items = []
            for category, extensions in file_types.items():
                line = f"{category}: {', '.join(extensions)}\n"
                textbox.insert("end", line)
                items.append((category, extensions))
            textbox.configure(state="disabled")
            textbox._items = items

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

        # Button functions
        def add_edit_type():
            category = cat_var.get().strip()
            extensions_text = ext_var.get().strip()
            
            if not category or not extensions_text:
                messagebox.showerror("Error", "Both category name and extensions must be filled.")
                return
            
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

        def remove_type():
            if not hasattr(textbox, "_items") or not textbox._items:
                messagebox.showwarning("Warning", "No categories to remove.")
                return
            
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

        def load_selection():
            if not hasattr(textbox, "_items") or not textbox._items:
                return
            
            cursor_pos = textbox.index("insert")
            line_num = int(cursor_pos.split('.')[0]) - 1
            
            if 0 <= line_num < len(textbox._items):
                cat, extensions = textbox._items[line_num]
                cat_var.set(cat)
                ext_var.set(', '.join(extensions))

        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")

        ctk.CTkButton(button_frame, text="➕ Add/Update Category", 
                      command=add_edit_type).pack(side="left", padx=(0, 10))
        ctk.CTkButton(button_frame, text="🗑️ Remove Selected", 
                      command=remove_type).pack(side="left", padx=(0, 10))
        ctk.CTkButton(button_frame, text="📝 Edit Selected", 
                      command=load_selection).pack(side="left")

        # Bind double-click to edit
        textbox.bind('<Double-1>', lambda e: load_selection())
    
    def show_manual_assignment(self, files: List[str], file_types: Dict[str, List[str]],
                                custom_tags: str, manual_assignments: Dict[str, str],
                                save_callback: Callable, folder: str):
            """Show manual assignment window"""
            win = ctk.CTkToplevel(self.root)
            win.title("Manual File Assignment")
            win.geometry("860x680")
            self._bring_to_front(win)

            main_frame = ctk.CTkFrame(win, corner_radius=0)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Title and instructions
            ctk.CTkLabel(main_frame, text="Manual File Assignment", 
                        font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0, 5))

            info_text = ("Select files and assign categories. Use Ctrl+Click for multiple selection.\n"
                        "You can assign categories to multiple files at once.")
            ctk.CTkLabel(main_frame, text=info_text, 
                        font=ctk.CTkFont(size=10, slant="italic")).pack(pady=(0, 15))

            # Create interface
            self._create_manual_assignment_interface(main_frame, files, file_types, 
                                                custom_tags, manual_assignments, 
                                                save_callback, folder, win)
    
    def _create_manual_assignment_interface(self, parent, files, file_types, custom_tags, 
                                          manual_assignments, save_callback, folder, window):
        """Create the manual assignment interface"""
        # Main content with tabs
        notebook = ctk.CTkTabview(parent)
        notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        multi_frame = notebook.add("File Assignment")
        
        # Get available categories
        def get_categories():
            categories = list(file_types.keys())
            categories.extend([tag.strip() for tag in custom_tags.split(",") if tag.strip()])
            try:
                subfolders = [f for f in os.listdir(folder) 
                            if os.path.isdir(os.path.join(folder, f))]
                categories.extend(subfolders)
            except Exception:
                pass
            categories.append("None")
            return sorted(list(set(categories)))
        
        # Files list with search
        files_frame = ctk.CTkFrame(multi_frame)
        files_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Search bar
        search_frame = ctk.CTkFrame(files_frame)
        search_frame.pack(fill="x", pady=(0, 5))
        
        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=search_var, 
                                   placeholder_text="Search files...")
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Scrollable file list
        scroll_frame = ctk.CTkScrollableFrame(files_frame)
        scroll_frame.pack(fill="both", expand=True)
        
        # Create file checkboxes
        file_checkboxes = {}
        file_frames = {}
        
        for file in files:
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
        
        # Search functionality
        def search_files():
            keyword = search_var.get().lower()
            for file, frame in file_frames.items():
                if keyword in file.lower():
                    frame.pack(fill="x", pady=2)
                else:
                    frame.pack_forget()
        
        search_var.trace_add("write", lambda *args: search_files())
        
        # Assignment controls
        assign_frame = ctk.CTkFrame(multi_frame)
        assign_frame.pack(fill="x")
        
        category_var = ctk.StringVar(value="None")
        categories = get_categories()
        
        ctk.CTkLabel(assign_frame, text="Select Category:").pack(anchor="w")
        category_combo = ctk.CTkOptionMenu(assign_frame, variable=category_var, values=categories)
        category_combo.pack(anchor="w", pady=(5, 10))
        
        def assign_to_selected():
            selected_files = [file for file, (var, _) in file_checkboxes.items() if var.get() == 1]
            
            if not selected_files:
                messagebox.showwarning("Warning", "Please select files to assign.")
                return
            
            category = category_var.get()
            
            for file in selected_files:
                if category == "None":
                    manual_assignments.pop(file, None)
                else:
                    manual_assignments[file] = category
                
                current_assignment = manual_assignments.get(file, "None")
                file_checkboxes[file][1].configure(text=f"{file} → {current_assignment}")
            
            messagebox.showinfo("Success", f"Assigned {len(selected_files)} files to '{category}'")
        
        ctk.CTkButton(assign_frame, text="✅ Assign to Selected Files", 
                     command=assign_to_selected).pack(anchor="w", pady=(0, 5))
        
        # Selection info and controls
        def update_selection_info():
            selected_count = sum(var.get() for var, _ in file_checkboxes.values())
            selection_info.set(f"Selected: {selected_count} files")
        
        selection_info = ctk.StringVar(value="Selected: 0 files")
        ctk.CTkLabel(assign_frame, textvariable=selection_info, 
                    font=ctk.CTkFont(size=10, slant="italic")).pack(anchor="w")
        
        for var, _ in file_checkboxes.values():
            var.trace_add("write", lambda *args: update_selection_info())
        
        # Selection buttons
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
        
        # Bottom buttons
        self._create_manual_assignment_buttons(parent, window, manual_assignments, save_callback)
    
    def _create_manual_assignment_buttons(self, parent, window, manual_assignments, save_callback):
        """Create bottom buttons for manual assignment window"""
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", pady=(10, 0))
        
        def save_and_close():
            save_callback(manual_assignments)
            window.destroy()
        
        def clear_all():
            if messagebox.askyesno("Confirm", "Clear all manual assignments?"):
                manual_assignments.clear()
                messagebox.showinfo("Cleared", "All manual assignments cleared!")
                window.destroy()
        
        ctk.CTkButton(button_frame, text="💾 Save & Close", 
                     command=save_and_close).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(button_frame, text="❌ Cancel", 
                     command=window.destroy).pack(side="right")
        
        ctk.CTkButton(button_frame, text="🗑️ Clear All", 
                     command=clear_all).pack(side="left")
    
    # =============================================================================
    # Utility Methods
    # =============================================================================
    
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
    
    def _bring_to_front(self, window):
        """Bring window to front and focus"""
        window.lift()
        window.focus()
        window.grab_set()
    
    # =============================================================================
    # Application Lifecycle
    # =============================================================================
    
    def run(self):
        """Start the main application loop"""
        self.root.mainloop()
    
    def destroy(self):
        """Destroy the main window"""
        self.root.destroy()