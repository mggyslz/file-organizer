import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Dict, List, Callable

from .ui_enhancements import UIEnhancements

class UIComponents:
    """Handles UI setup and window creation with CustomTkinter"""
    
    def __init__(self, root: ctk.CTk, ui_enhancements: UIEnhancements):
        self.root = root
        self.ui_enhancements = ui_enhancements
        self.setup_main_window()
    
    def setup_main_window(self):
        """Setup the main window"""
        self.root.title("File Organizer")
        self.root.geometry("930x690")  # Increased height for size filtering
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    
    def create_main_ui(self, folder_var: ctk.StringVar, create_folders_var: ctk.BooleanVar,
                      move_files_var: ctk.BooleanVar, organize_by_date_var: ctk.BooleanVar,
                      skip_hidden_var: ctk.BooleanVar, custom_tags_var: ctk.StringVar,
                      file_count_var: ctk.StringVar, status_var: ctk.StringVar,
                      progress: ctk.CTkProgressBar, min_size_var: ctk.StringVar,
                      max_size_var: ctk.StringVar, size_unit_var: ctk.StringVar,
                      callbacks: Dict[str, Callable]) -> None:
        """Create the main UI layout with CTk widgets"""
        
        # Main frame
        main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(main_frame, text="Welcome to File Organizer", 
                           font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=(0, 5))

        # Description label
        description_label = ctk.CTkLabel(
            main_frame, 
            text="A simple tool to organize your files automatically.",
            font=ctk.CTkFont(size=10), 
            text_color="gray70"
        )
        description_label.pack(anchor='center')

        # Folder selection
        self._create_folder_selection_frame(main_frame, folder_var, callbacks['browse_folder'])
        
        # Options
        self._create_options_frame(main_frame, create_folders_var, move_files_var, 
                                 organize_by_date_var, skip_hidden_var, custom_tags_var)
        
        # Size filtering
        self._create_size_filter_frame(main_frame, min_size_var, max_size_var, size_unit_var)
        
        # File count display
        count_label = ctk.CTkLabel(main_frame, textvariable=file_count_var, 
                                 font=ctk.CTkFont(size=12, slant="italic"))
        count_label.pack(pady=(10, 15))
        
        # Action buttons
        self._create_action_buttons(main_frame, callbacks)
        
        # Progress bar
        progress.pack(fill="x", pady=(10, 10), padx=10)
        
        # Status bar
        status_bar = ctk.CTkLabel(main_frame, textvariable=status_var, 
                                corner_radius=0, anchor="w")
        status_bar.pack(fill="x", pady=(0, 10))
        
        # Footer
        footer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        footer_frame.pack(fill="x", pady=(10, 0))
    
        footer_label = ctk.CTkLabel(footer_frame, 
                           text="© 2025 File Organizer | Version 1.0\n A project by mggyslz",
                           font=ctk.CTkFont(size=10), 
                           text_color="gray70")
        footer_label.pack(side="right")
    
    def _create_folder_selection_frame(self, parent: ctk.CTkFrame, folder_var: ctk.StringVar,
                                     browse_callback: Callable):
        """Create folder selection frame with CTk widgets"""
        folder_frame = ctk.CTkFrame(parent, corner_radius=5)
        folder_frame.pack(fill="x", pady=(0, 15), padx=5)
        
        ctk.CTkLabel(folder_frame, text="Select Folder:", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(5, 0))
        
        entry_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        entry_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        folder_entry = ctk.CTkEntry(entry_frame, textvariable=folder_var, 
                                  font=ctk.CTkFont(size=12), height=35)
        folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(entry_frame, text="Browse", command=browse_callback,
                                  font=ctk.CTkFont(size=12), height=35, width=90)
        browse_btn.pack(side="right")
    
    def _create_options_frame(self, parent: ctk.CTkFrame, create_folders_var: ctk.BooleanVar,
                            move_files_var: ctk.BooleanVar, organize_by_date_var: ctk.BooleanVar,
                            skip_hidden_var: ctk.BooleanVar, custom_tags_var: ctk.StringVar):
        """Create options frame with CTk widgets"""
        options_frame = ctk.CTkFrame(parent, corner_radius=5)
        options_frame.pack(fill="x", pady=(0, 15), padx=5)
        
        ctk.CTkLabel(options_frame, text="Options:", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(5, 0))
        
        # First row of options
        row1 = ctk.CTkFrame(options_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=(5, 0))
        
        ctk.CTkCheckBox(row1, text="Create category folders", 
                       variable=create_folders_var, font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 20))
        
        ctk.CTkCheckBox(row1, text="Move files (uncheck to copy)", 
                       variable=move_files_var, font=ctk.CTkFont(size=12)).pack(side="left")
        
        # Second row of options
        row2 = ctk.CTkFrame(options_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(10, 0))
        
        ctk.CTkCheckBox(row2, text="Organize by date (YYYY-MM)", 
                       variable=organize_by_date_var, font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 20))
        
        ctk.CTkCheckBox(row2, text="Skip hidden files", 
                       variable=skip_hidden_var, font=ctk.CTkFont(size=12)).pack(side="left")
        
        # Custom tags
        tags_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        tags_frame.pack(fill="x", padx=10, pady=(10, 10))
        
        ctk.CTkLabel(tags_frame, text="Custom tags (comma separated):",
                    font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkEntry(tags_frame, textvariable=custom_tags_var,
                    font=ctk.CTkFont(size=12), height=35).pack(fill="x", pady=(5, 0))
    
    def _create_size_filter_frame(self, parent: ctk.CTkFrame, min_size_var: ctk.StringVar,
                                max_size_var: ctk.StringVar, size_unit_var: ctk.StringVar):
        """Create size filtering frame with CTk widgets"""
        size_frame = ctk.CTkFrame(parent, corner_radius=5)
        size_frame.pack(fill="x", pady=(0, 15), padx=5)
        
        ctk.CTkLabel(size_frame, text="Size Filtering:", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(5, 0))
        
        # Size filter controls
        filter_row = ctk.CTkFrame(size_frame, fg_color="transparent")
        filter_row.pack(fill="x", padx=10, pady=(0, 10))
        
        # Minimum size
        ctk.CTkLabel(filter_row, text="Min size:", 
                    font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 5))
        min_entry = ctk.CTkEntry(filter_row, textvariable=min_size_var, 
                               font=ctk.CTkFont(size=12), width=80, height=30)
        min_entry.pack(side="left", padx=(0, 10))
        
        # Maximum size
        ctk.CTkLabel(filter_row, text="Max size:", 
                    font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 5))
        max_entry = ctk.CTkEntry(filter_row, textvariable=max_size_var, 
                               font=ctk.CTkFont(size=12), width=80, height=30)
        max_entry.pack(side="left", padx=(0, 10))
        
        # Size unit selector
        unit_combo = ctk.CTkOptionMenu(filter_row, variable=size_unit_var, 
                                     values=["B", "KB", "MB", "GB"], 
                                     font=ctk.CTkFont(size=12), width=60, height=30)
        unit_combo.pack(side="left", padx=(0, 10))
        
        # Info label
        ctk.CTkLabel(filter_row, text="(Leave empty for no limit)", 
                    font=ctk.CTkFont(size=10, slant="italic"), 
                    text_color="gray70").pack(side="left", padx=(10, 0))
    
    def _create_action_buttons(self, parent: ctk.CTkFrame, callbacks: Dict[str, Callable]):
        """Create action buttons for the main UI with CTk widgets"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 15))
        
        # First row of buttons
        row1 = ctk.CTkFrame(button_frame, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 5))
        
        preview_btn = ctk.CTkButton(row1, text="📋 Preview Organization", 
                                  command=callbacks['preview_organization'],
                                  font=ctk.CTkFont(size=12))
        preview_btn.pack(side="left", padx=(0, 10))
        
        organize_btn = ctk.CTkButton(row1, text="🚀 Organize Files", 
                                   command=callbacks['organize_files'],
                                   font=ctk.CTkFont(size=12, weight="bold"),
                                   fg_color="#2CC985", hover_color="#27AE60")
        organize_btn.pack(side="left", padx=(0, 10))
        
        # Store cancel button as instance variable
        self.cancel_btn = ctk.CTkButton(row1, text="❌ Cancel Operation", 
                                    command=callbacks['cancel_operation'],
                                    state="disabled",
                                    font=ctk.CTkFont(size=12))
        self.cancel_btn.pack(side="left", padx=(0, 10))
        
        stats_btn = ctk.CTkButton(row1, text="📊 Folder Statistics", 
                                 command=callbacks['get_folder_statistics'],
                                 font=ctk.CTkFont(size=12))
        stats_btn.pack(side="left", padx=(0, 10))
        
        duplicates_btn = ctk.CTkButton(row1, text="🔍 Find Duplicates", 
                                     command=callbacks['find_duplicates'],
                                     font=ctk.CTkFont(size=12))
        duplicates_btn.pack(side="left")
        
        # Second row of buttons
        row2 = ctk.CTkFrame(button_frame, fg_color="transparent")
        row2.pack(fill="x", pady=(5, 0))
        
        undo_btn = ctk.CTkButton(row2, text="↶ Undo Last", 
                                command=callbacks['undo_last_operation'],
                                font=ctk.CTkFont(size=12))
        undo_btn.pack(side="left", padx=(0, 10))
        
        file_types_btn = ctk.CTkButton(row2, text="🛠️ Edit File Types", 
                                      command=callbacks['open_file_types_editor'],
                                      font=ctk.CTkFont(size=12))
        file_types_btn.pack(side="left", padx=(0, 10))
        
        manual_btn = ctk.CTkButton(row2, text="✋ Manual File Assignment", 
                                  command=callbacks['open_manual_assignment_window'],
                                  font=ctk.CTkFont(size=12))
        manual_btn.pack(side="left")
    
    def set_operation_state(self, in_progress: bool):
        """Enable/disable UI elements based on operation state"""
        # Get all widgets from the main window
        for widget in self.root.winfo_children():
            if isinstance(widget, (ctk.CTkFrame, ctk.CTkScrollableFrame)):
                # Recursively handle widgets in frames
                self._set_widgets_state(widget, in_progress)
    
        # Always keep the cancel button enabled when operation is in progress
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.configure(state="normal" if in_progress else "disabled")

    def _set_widgets_state(self, parent, in_progress):
        """Recursively set state for all widgets in a container"""
        for widget in parent.winfo_children():
            if isinstance(widget, (ctk.CTkFrame, ctk.CTkScrollableFrame)):
                self._set_widgets_state(widget, in_progress)
            elif isinstance(widget, (ctk.CTkButton, ctk.CTkEntry, ctk.CTkOptionMenu, ctk.CTkCheckBox)):
                # Skip the cancel button - we handle it separately
                if widget == self.cancel_btn:
                    continue
                widget.configure(state="disabled" if in_progress else "normal")
    
    def show_folder_statistics(self, stats: Dict):
        """Show folder statistics in a popup window"""
        stats_window = ctk.CTkToplevel(self.root)
        stats_window.title("📊 Folder Statistics")
        stats_window.geometry("400x300")
        
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
    
    def create_preview_window(self, preview_data: Dict[str, List[str]]) -> None:
        """Create and show preview window with CTk widgets"""
        preview_window = ctk.CTkToplevel(self.root)
        preview_window.title("📋 Organization Preview")
        preview_window.geometry("600x400")
        
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
        content = "📋 File Organization Preview:\n\n"
        
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
    
    def create_file_types_editor(self, file_types: Dict[str, List[str]], 
                               save_callback: Callable) -> None:
        """Create file types editor window with CTk widgets"""
        editor = ctk.CTkToplevel(self.root)
        editor.title("🛠️ Edit File Type Categories")
        editor.geometry("600x500")

        main_frame = ctk.CTkFrame(editor, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Instructions
        ctk.CTkLabel(main_frame, text="Edit File Type Categories", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="Add extensions with dots (e.g., .pdf, .jpg)", 
                    font=ctk.CTkFont(size=10, slant="italic")).pack(pady=(0, 10))

        # Listbox with scrollbar
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))

        listbox = tk.Listbox(list_frame, width=70, height=15)  # Using tk.Listbox as CTk doesn't have one
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(list_frame, orientation="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)

        # Populate listbox
        def refresh_listbox():
            listbox.delete(0, tk.END)
            for category, extensions in file_types.items():
                listbox.insert(tk.END, f"{category}: {', '.join(extensions)}")

        refresh_listbox()

        # Entry fields
        entry_frame = ctk.CTkFrame(main_frame)
        entry_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(entry_frame, text="Category Name:").grid(row=0, column=0, sticky="w", pady=2)
        cat_var = ctk.StringVar()
        ctk.CTkEntry(entry_frame, textvariable=cat_var, width=25).grid(row=0, column=1, sticky="w", padx=(10, 0))

        ctk.CTkLabel(entry_frame, text="Extensions:").grid(row=1, column=0, sticky="w", pady=2)
        ext_var = ctk.StringVar()
        ctk.CTkEntry(entry_frame, textvariable=ext_var, width=50).grid(row=1, column=1, sticky="w", padx=(10, 0))

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
            refresh_listbox()
            save_callback()
            cat_var.set("")
            ext_var.set("")
            messagebox.showinfo("Success", f"Category '{category}' saved successfully!")

        ctk.CTkButton(button_frame, text="➕ Add/Update Category", 
                      command=add_edit_type).pack(side="left", padx=(0, 10))

        def remove_type():
            selected = listbox.curselection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a category to remove.")
                return
            line = listbox.get(selected[0])
            cat = line.split(":")[0]
            if messagebox.askyesno("Confirm", f"Remove category '{cat}'?"):
                file_types.pop(cat, None)
                refresh_listbox()
                save_callback()
                messagebox.showinfo("Success", f"Category '{cat}' removed successfully!")

        ctk.CTkButton(button_frame, text="🗑️ Remove Selected", 
                      command=remove_type).pack(side="left", padx=(0, 10))

        def load_selection():
            selected = listbox.curselection()
            if not selected:
                return
            line = listbox.get(selected[0])
            parts = line.split(": ", 1)
            if len(parts) == 2:
                cat_var.set(parts[0])
                ext_var.set(parts[1])

        ctk.CTkButton(button_frame, text="📝 Edit Selected", 
                      command=load_selection).pack(side="left")

        # Bind double-click to edit
        listbox.bind('<Double-1>', lambda e: load_selection())
    
    def create_manual_assignment_window(self, files: List[str], file_types: Dict[str, List[str]],
                                      custom_tags: str, manual_assignments: Dict[str, str],
                                      save_callback: Callable) -> None:
        """Create enhanced manual file assignment window with multi-select"""
        win = ctk.CTkToplevel(self.root)
        win.title("✋ Manual File Assignment")
        win.geometry("860x680")

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

        # Create multi-select interface
        self._create_multi_select_interface(multi_frame, files, file_types, custom_tags, 
                                          manual_assignments, save_callback)
        # Bottom buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))

        def save_and_close():
            save_callback(manual_assignments)
            win.destroy()

        ctk.CTkButton(button_frame, text="💾 Save & Close", 
                     command=save_and_close).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(button_frame, text="❌ Cancel", 
                     command=win.destroy).pack(side="right")

        def clear_all():
            if messagebox.askyesno("Confirm", "Clear all manual assignments?"):
                manual_assignments.clear()
                messagebox.showinfo("Cleared", "All manual assignments cleared!")
                win.destroy()

        ctk.CTkButton(button_frame, text="🗑️ Clear All", 
                     command=clear_all).pack(side="left")

    def _create_multi_select_interface(self, parent: ctk.CTkFrame, files: List[str], 
                                     file_types: Dict[str, List[str]], custom_tags: str,
                                     manual_assignments: Dict[str, str], save_callback: Callable):
        """Create multi-select assignment interface"""
        
        # Files listbox with multi-select (using tk.Listbox as CTk doesn't have one)
        files_frame = ctk.CTkFrame(parent)
        files_frame.pack(fill="both", expand=True, pady=(0, 10))

        listbox_frame = ctk.CTkFrame(files_frame)
        listbox_frame.pack(fill="both", expand=True)

        files_listbox = tk.Listbox(listbox_frame, selectmode=tk.EXTENDED, height=15)
        files_scrollbar = ctk.CTkScrollbar(listbox_frame, orientation="vertical", command=files_listbox.yview)
        files_listbox.configure(yscrollcommand=files_scrollbar.set)

        files_listbox.pack(side="left", fill="both", expand=True)
        files_scrollbar.pack(side="right", fill="y")

        # Populate files listbox
        for i, file in enumerate(files):
            current_assignment = manual_assignments.get(file, "None")
            display_text = f"{file} → {current_assignment}"
            files_listbox.insert(tk.END, display_text)

        # Category assignment frame
        assign_frame = ctk.CTkFrame(parent)
        assign_frame.pack(fill="x")

        # Create category list
        categories = list(file_types.keys()) + [tag.strip() for tag in custom_tags.split(",") if tag.strip()]
        categories.append("None")

        # Category selection
        ctk.CTkLabel(assign_frame, text="Select Category:").pack(anchor="w")
        
        category_var = ctk.StringVar(value="None")
        category_combo = ctk.CTkOptionMenu(assign_frame, variable=category_var, 
                                         values=categories)
        category_combo.pack(anchor="w", pady=(5, 10))

        def assign_to_selected():
            selected_indices = files_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("Warning", "Please select files to assign.")
                return

            category = category_var.get()
            assigned_files = []

            for index in selected_indices:
                file = files[index]
                if category == "None":
                    manual_assignments.pop(file, None)
                else:
                    manual_assignments[file] = category
                assigned_files.append(file)

                # Update display
                current_assignment = manual_assignments.get(file, "None")
                display_text = f"{file} → {current_assignment}"
                files_listbox.delete(index)
                files_listbox.insert(index, display_text)

            messagebox.showinfo("Success", 
                              f"Assigned {len(assigned_files)} files to '{category}'")

        # Assign button
        ctk.CTkButton(assign_frame, text="✅ Assign to Selected Files", 
                     command=assign_to_selected).pack(anchor="w", pady=(0, 5))

        # Selection info
        def update_selection_info():
            selected_count = len(files_listbox.curselection())
            selection_info.set(f"Selected: {selected_count} files")

        selection_info = ctk.StringVar(value="Selected: 0 files")
        ctk.CTkLabel(assign_frame, textvariable=selection_info, 
                    font=ctk.CTkFont(size=10, slant="italic")).pack(anchor="w")

        files_listbox.bind('<<ListboxSelect>>', lambda e: update_selection_info())

        # Filter buttons
        filter_frame = ctk.CTkFrame(assign_frame)
        filter_frame.pack(fill="x", pady=(10, 0))
        
        def select_unassigned():
            files_listbox.selection_clear(0, tk.END)
            for i, file in enumerate(files):
                if file not in manual_assignments:
                    files_listbox.selection_set(i)
            update_selection_info()

        def select_all():
            files_listbox.selection_set(0, tk.END)
            update_selection_info()

        def clear_selection():
            files_listbox.selection_clear(0, tk.END)
            update_selection_info()

        ctk.CTkButton(filter_frame, text="📝 Select Unassigned", 
                     command=select_unassigned).pack(side="left", padx=(0, 5))
        ctk.CTkButton(filter_frame, text="🔍 Select All", 
                     command=select_all).pack(side="left", padx=(0, 5))
        ctk.CTkButton(filter_frame, text="❌ Clear Selection", 
                     command=clear_selection).pack(side="left")

    
    @staticmethod
    def browse_folder() -> str:
        """Open folder browser dialog"""
        return filedialog.askdirectory()
    
    @staticmethod
    def show_info(title: str, message: str):
        """Show info message"""
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_warning(title: str, message: str):
        """Show warning message"""
        messagebox.showwarning(title, message)
    
    @staticmethod
    def show_error(title: str, message: str):
        """Show error message"""
        messagebox.showerror(title, message)
    
    @staticmethod
    def ask_yes_no(title: str, message: str) -> bool:
        """Ask yes/no question"""
        return messagebox.askyesno(title, message)