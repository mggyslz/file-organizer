# ui_enhancements.py
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Callable, Tuple

class UIEnhancements:
    """Enhanced UI components and utilities"""
    

    @staticmethod
    def create_filter_panel(parent: ttk.Frame, filters: Dict[str, List[str]], 
                          apply_callback: Callable) -> Dict[str, tk.Variable]:
        """
        Create a filter panel with checkboxes for each filter option
        Returns: Dictionary of filter variables {filter_name: variable}
        """
        filter_vars = {}
        panel = ttk.LabelFrame(parent, text="Filters", padding=10)
        panel.pack(fill=tk.X, pady=5)
        
        for filter_name, options in filters.items():
            frame = ttk.Frame(panel)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=f"{filter_name}:").pack(side=tk.LEFT)
            
            var = tk.StringVar(value="All")
            filter_vars[filter_name] = var
            
            for option in ["All"] + options:
                rb = ttk.Radiobutton(frame, text=option, value=option, variable=var,
                                    command=lambda: apply_callback(filter_vars))
                rb.pack(side=tk.LEFT, padx=5)
        
        return filter_vars

    @staticmethod
    def create_modern_button(parent: ttk.Frame, text: str, command: Callable, 
                           icon: str = None, style: str = None) -> ttk.Button:
        """Create a modern-looking button with optional icon"""
        btn = ttk.Button(parent, text=text, command=command, style=style)
        
        if icon:
            btn.image = tk.PhotoImage(data=icon)  # In real app, would load from file
            btn.config(image=btn.image, compound=tk.LEFT)
            
        return btn

    @staticmethod
    def create_progress_panel(parent: ttk.Frame) -> Tuple[ttk.Progressbar, ttk.Label]:
        """Create an enhanced progress panel with percentage label"""
        panel = ttk.Frame(parent)
        panel.pack(fill=tk.X, pady=5)
        
        progress = ttk.Progressbar(panel, mode='determinate')
        progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        percent_label = ttk.Label(panel, text="0%")
        percent_label.pack(side=tk.RIGHT)
        
        return progress, percent_label