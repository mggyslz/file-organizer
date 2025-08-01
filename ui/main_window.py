
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import Dict, List, Callable
from PIL import Image
from datetime import datetime
import shutil

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
            ("Undo", self.app.undo_last_operation, "undo")
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
        """Show duplicates management window without tabs, pre-checking duplicates"""
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
        
        # Create scrollable area for all duplicates
        scroll_frame = ctk.CTkScrollableFrame(main_frame)
        scroll_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        file_checkboxes = {}
        
        # Create sections for each duplicate group
        for group_idx, (hash_val, files) in enumerate(duplicates.items()):
            # Group header
            header_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            header_frame.pack(fill="x", pady=(15, 5))
            
            ctk.CTkLabel(header_frame, 
                        text=f"Duplicate Set {group_idx + 1} ({len(files)} files):",
                        font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
            
            # Create checkboxes for each file
            for i, file in enumerate(files):
                file_frame = ctk.CTkFrame(scroll_frame)
                file_frame.pack(fill="x", pady=2)
                
                # Pre-check all except the first file in each group
                cb_var = ctk.IntVar(value=1 if i > 0 else 0)
                cb = ctk.CTkCheckBox(file_frame, text=os.path.basename(file), variable=cb_var)
                cb.pack(side="left", padx=(0, 10))
                
                # Show file info
                self._add_file_info(file_frame, file)
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
            self.app.update_file_count(folder)
        
        # Just a static delete button
        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Delete",
            command=delete_selected_duplicates,
            fg_color="#FF5555",
            hover_color="#FF0000",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        delete_btn.pack(side="left", padx=(0, 10))
        
        # Close button
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
        """Show manual assignment window with modern UI design"""
        win = ctk.CTkToplevel(self.root)
        win.title("Manual File Assignment")
        win.geometry("900x650")
        self._bring_to_front(win)

        # Main container with modern spacing
        main_frame = ctk.CTkFrame(win, corner_radius=12)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Header section with modern typography
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(15, 20))

        ctk.CTkLabel(header_frame, text="Manual File Assignment", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack()

        ctk.CTkLabel(header_frame, 
                    text="Select files and assign categories • Use Ctrl+Click for multiple selection",
                    font=ctk.CTkFont(size=11),
                    text_color=("#666666", "#CCCCCC")).pack(pady=(5, 0))

        # Create the main interface
        self._create_manual_assignment_interface(main_frame, files, file_types, 
                                            custom_tags, manual_assignments, 
                                            save_callback, folder, win)

    def _create_manual_assignment_interface(self, parent, files, file_types, custom_tags, 
                                        manual_assignments, save_callback, folder, window):
        """Create the manual assignment interface with modern layout"""
        # Main content area with cards
        content_frame = ctk.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Left panel - File list (70%)
        left_panel = ctk.CTkFrame(content_frame, corner_radius=12, border_width=1, border_color=("#DDDDDD", "#444444"))
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 12))
        
        # Right panel - Controls (30%)
        right_panel = ctk.CTkFrame(content_frame, corner_radius=12, width=280, border_width=1, border_color=("#DDDDDD", "#444444"))
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)
        
        # Get available categories
        def get_categories():
            categories = list(file_types.keys())
            categories.extend([tag.strip() for tag in custom_tags.split(",") if tag.strip()])
            try:
                subfolders = [f for f in os.listdir(folder) 
                            if os.path.isdir(os.path.join(folder, f)) and not f.startswith('.')]
                categories.extend(subfolders)
            except Exception:
                pass
            categories.append("None")
            return sorted(list(set(categories)))
        
        # ===== FILE LIST PANEL =====
        # Panel header
        list_header = ctk.CTkFrame(left_panel, fg_color="transparent")
        list_header.pack(fill="x", padx=15, pady=(15, 12))
        
        ctk.CTkLabel(list_header, text="Files", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        
        # Selection counter
        selected_counter = ctk.CTkLabel(list_header, text="0 selected",
                                    font=ctk.CTkFont(size=11),
                                    text_color=("#666666", "#CCCCCC"))
        selected_counter.pack(side="right")
        
        # Search bar with modern styling
        search_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        search_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=search_var,
                                placeholder_text="🔍 Search files...",
                                height=32,
                                corner_radius=8)
        search_entry.pack(fill="x")
        
        # File list with modern cards
        scroll_frame = ctk.CTkScrollableFrame(left_panel, corner_radius=8)
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        file_checkboxes = {}
        file_frames = {}
        
        for i, file in enumerate(files):
            current_assignment = manual_assignments.get(file, "None")
            
            # Modern file card
            card = ctk.CTkFrame(scroll_frame, corner_radius=8, height=50)
            card.pack(fill="x", pady=(0, 6))
            
            # Card content
            card_content = ctk.CTkFrame(card, fg_color="transparent")
            card_content.pack(fill="both", expand=True, padx=12, pady=10)
            
            # Checkbox
            var = ctk.IntVar(value=0)
            cb = ctk.CTkCheckBox(card_content, text="", variable=var, width=18)
            cb.pack(side="left", padx=(0, 10))
            
            # File info
            info_frame = ctk.CTkFrame(card_content, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True)
            
            # File name
            name_label = ctk.CTkLabel(info_frame, text=file, anchor="w",
                                    font=ctk.CTkFont(size=12))
            name_label.pack(fill="x")
            
            # Category badge
            category_color = "#4CAF50" if current_assignment != "None" else "#666666"
            assign_label = ctk.CTkLabel(info_frame, 
                                    text=f"📁 {current_assignment}",
                                    anchor="w",
                                    font=ctk.CTkFont(size=10),
                                    text_color=category_color)
            assign_label.pack(fill="x", pady=(1, 0))
            
            file_checkboxes[file] = (var, assign_label)
            file_frames[file] = card
        
        # Search functionality
        def search_files():
            keyword = search_var.get().lower()
            for file, frame in file_frames.items():
                if keyword in file.lower():
                    frame.pack(fill="x", pady=(0, 6))
                else:
                    frame.pack_forget()
        
        search_var.trace_add("write", lambda *args: search_files())
        
        # ===== CONTROL PANEL =====
        # Panel header
        control_header = ctk.CTkFrame(right_panel, fg_color="transparent")
        control_header.pack(fill="x", padx=15, pady=(15, 15))
        
        ctk.CTkLabel(control_header, text="Actions", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack()
        
        # Category assignment section
        category_section = ctk.CTkFrame(right_panel, corner_radius=8, border_width=1, border_color=("#DDDDDD", "#444444"))
        category_section.pack(fill="x", padx=15, pady=(0, 15))
        
        # Section content
        cat_content = ctk.CTkFrame(category_section, fg_color="transparent")
        cat_content.pack(fill="x", padx=12, pady=12)
        
        ctk.CTkLabel(cat_content, text="Assign Category",
                    font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 8))
        
        # Category dropdown
        category_var = ctk.StringVar(value="None")
        categories = get_categories()
        
        category_combo = ctk.CTkOptionMenu(cat_content, variable=category_var, 
                                        values=categories, height=28)
        category_combo.pack(fill="x", pady=(0, 10))
        
        # Assign button
        assign_btn = ctk.CTkButton(cat_content,
                                text="✓ Assign to Selected",
                                command=lambda: self._assign_to_selected(file_checkboxes, manual_assignments, category_var, selected_counter),
                                height=32,
                                corner_radius=8)
        assign_btn.pack(fill="x")
        
        # Selection controls
        selection_section = ctk.CTkFrame(right_panel, corner_radius=8, border_width=1, border_color=("#DDDDDD", "#444444"))
        selection_section.pack(fill="x", padx=15, pady=(0, 15))
        
        sel_content = ctk.CTkFrame(selection_section, fg_color="transparent")
        sel_content.pack(fill="x", padx=12, pady=12)
        
        ctk.CTkLabel(sel_content, text="Selection",
                    font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 8))
        
        # Selection buttons
        sel_btn_frame = ctk.CTkFrame(sel_content, fg_color="transparent")
        sel_btn_frame.pack(fill="x")
        
        ctk.CTkButton(sel_btn_frame, text="Select All",
                    command=lambda: self._select_unassigned(file_checkboxes, manual_assignments),
                    width=85, height=28).pack(side="left", padx=(0, 6))
        
        ctk.CTkButton(sel_btn_frame, text="Clear",
                    command=lambda: self._clear_selection(file_checkboxes),
                    width=70, height=28).pack(side="right")
        
        # Folder management
        folder_section = ctk.CTkFrame(right_panel, corner_radius=8, border_width=1, border_color=("#DDDDDD", "#444444"))
        folder_section.pack(fill="x", padx=15, pady=(0, 15))
        
        folder_content = ctk.CTkFrame(folder_section, fg_color="transparent")
        folder_content.pack(fill="x", padx=12, pady=12)
        
        ctk.CTkLabel(folder_content, text="Folders",
                    font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 8))
        
        # Folder buttons
        folder_btn_frame = ctk.CTkFrame(folder_content, fg_color="transparent")
        folder_btn_frame.pack(fill="x")
        
        ctk.CTkButton(folder_btn_frame, text="➕ Add",
                    command=lambda: self._add_folder(folder, category_combo, get_categories),
                    width=85, height=28).pack(side="left", padx=(0, 6))
        
        ctk.CTkButton(folder_btn_frame, text="🗑️ Delete",
                    command=lambda: self._delete_folder(window, folder, category_combo, get_categories),
                    width=70, height=28,
                    fg_color="#FF5555",
                    hover_color="#FF0000").pack(side="right")
        
        # Update selection info
        def update_selection_info():
            selected_count = sum(var.get() for var, _ in file_checkboxes.values())
            selected_counter.configure(text=f"{selected_count} selected")
        
        for var, _ in file_checkboxes.values():
            var.trace_add("write", lambda *args: update_selection_info())
        
        # Bottom action bar
        self._create_bottom_actions(parent, window, manual_assignments, save_callback)

    def _assign_to_selected(self, file_checkboxes, manual_assignments, category_var, counter):
        selected_files = [file for file, (var, label) in file_checkboxes.items() if var.get() == 1]
        
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
            category_color = "#4CAF50" if current_assignment != "None" else "#666666"
            file_checkboxes[file][1].configure(text=f"📁 {current_assignment}",
                                            text_color=category_color)
        
        messagebox.showinfo("Success", f"Assigned {len(selected_files)} files to '{category}'")

    def _select_unassigned(self, file_checkboxes, manual_assignments):
        for file, (var, _) in file_checkboxes.items():
            var.set(1 if file not in manual_assignments else 0)

    def _clear_selection(self, file_checkboxes):
        for var, _ in file_checkboxes.values():
            var.set(0)

    def _add_folder(self, base_folder, category_combo, get_categories_func):
        dialog = ctk.CTkInputDialog(text="Enter folder name:", title="Create New Folder")
        folder_name = dialog.get_input()
        
        if folder_name and folder_name.strip():
            folder_name = folder_name.strip()
            try:
                folder_path = os.path.join(base_folder, folder_name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    messagebox.showinfo("Success", f"Folder '{folder_name}' created!")
                    # Update categories dropdown without closing dialog
                    category_combo.configure(values=get_categories_func())
                else:
                    messagebox.showwarning("Warning", f"Folder '{folder_name}' already exists")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folder: {str(e)}")

    def _delete_folder(self, parent_window, base_folder, category_combo, get_categories_func):
        try:
            folders = [f for f in os.listdir(base_folder) 
                    if os.path.isdir(os.path.join(base_folder, f)) and not f.startswith('.')]
        except Exception as e:
            messagebox.showerror("Error", f"Could not list folders: {str(e)}")
            return
        
        if not folders:
            messagebox.showwarning("Warning", "No folders available to delete")
            return
        
        # Modern delete dialog
        dialog = ctk.CTkToplevel(parent_window)
        dialog.title("Delete Folder")
        dialog.geometry("400x280")
        dialog.transient(parent_window)
        dialog.grab_set()
        
        main_frame = ctk.CTkFrame(dialog, corner_radius=12)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        ctk.CTkLabel(main_frame, text="Delete Folder",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 20))
        
        # Folder selection
        ctk.CTkLabel(main_frame, text="Select folder to delete:").pack(pady=(0, 8))
        
        folder_var = ctk.StringVar(value=folders[0])
        folder_menu = ctk.CTkOptionMenu(main_frame, variable=folder_var, values=folders)
        folder_menu.pack(fill="x", padx=20, pady=(0, 15))
        
        # Force delete option
        force_var = ctk.BooleanVar(value=False)
        force_cb = ctk.CTkCheckBox(main_frame, text="Force delete (ignore errors)", variable=force_var)
        force_cb.pack(pady=(0, 20))
        
        def perform_delete():
            folder_name = folder_var.get()
            folder_path = os.path.join(base_folder, folder_name)
            
            try:
                if os.path.exists(folder_path):
                    if force_var.get():
                        import stat
                        def remove_readonly(func, path, _):
                            os.chmod(path, stat.S_IWRITE)
                            func(path)
                        shutil.rmtree(folder_path, onerror=remove_readonly)
                    else:
                        shutil.rmtree(folder_path)
                    
                    messagebox.showinfo("Success", f"Folder '{folder_name}' deleted!")
                    category_combo.configure(values=get_categories_func())
                else:
                    messagebox.showwarning("Warning", f"Folder '{folder_name}' doesn't exist")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting folder: {str(e)}")
            finally:
                dialog.destroy()
        
        # Action buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20)
        
        ctk.CTkButton(btn_frame, text="Cancel",
                    command=dialog.destroy).pack(side="right", padx=(8, 0))
        
        ctk.CTkButton(btn_frame, text="🗑️ Delete",
                    command=perform_delete,
                    fg_color="#FF5555",
                    hover_color="#FF0000").pack(side="right")

    def _create_bottom_actions(self, parent, window, manual_assignments, save_callback):
        """Create modern bottom action bar"""
        action_bar = ctk.CTkFrame(parent, corner_radius=8, border_width=1, border_color=("#DDDDDD", "#444444"))
        action_bar.pack(fill="x", pady=(15, 0))
        
        btn_content = ctk.CTkFrame(action_bar, fg_color="transparent")
        btn_content.pack(fill="x", padx=15, pady=12)
        
        # Left - destructive action
        ctk.CTkButton(btn_content, text="🗑️ Clear All",
                    command=lambda: self._clear_all_assignments(manual_assignments, window),
                    fg_color="#FF5555",
                    hover_color="#FF0000",
                    height=32).pack(side="left")
        
        # Right - primary actions
        ctk.CTkButton(btn_content, text="Cancel",
                    command=window.destroy,
                    height=32).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(btn_content, text="💾 Save & Close",
                    command=lambda: self._save_and_close(manual_assignments, save_callback, window),
                    fg_color="#4CAF50",
                    hover_color="#388E3C",
                    height=32).pack(side="right")

    def _clear_all_assignments(self, manual_assignments, window):
        if messagebox.askyesno("Confirm", "Clear all manual assignments?"):
            manual_assignments.clear()
            messagebox.showinfo("Cleared", "All assignments cleared!")
            window.destroy()

    def _save_and_close(self, manual_assignments, save_callback, window):
        save_callback(manual_assignments)
        window.destroy()
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