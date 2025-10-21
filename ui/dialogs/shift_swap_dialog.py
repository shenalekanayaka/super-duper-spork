"""
Shift swap dialog
"""
import tkinter as tk
from tkinter import messagebox
from utils.helpers import bind_mousewheel


class ShiftSwapDialog:
    """Dialog for managing shift swaps"""
    
    def __init__(self, root, state):
        self.root = root
        self.state = state
        self.window = None
        self.swap_pairs = []
    
    def show(self):
        """Display the shift swap dialog"""
        other_group = "Group B" if self.state.shift_group == "Group A" else "Group A"
        
        self.window = tk.Toplevel(self.root)
        self.window.title(f"Shift Swap with {other_group}")
        self.window.state('zoomed')
        self.window.configure(bg="#f0f0f0")
        
        title = tk.Label(
            self.window,
            text=f"Shift Swap: {self.state.shift_group} ↔ {other_group}",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title.pack(pady=30)
        
        instruction = tk.Label(
            self.window,
            text="Select which worker to replace and who replaces them",
            font=("Arial", 14),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        instruction.pack(pady=10)
        
        # Scrollable frame
        canvas = tk.Canvas(self.window, bg="#f0f0f0", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=20)
        
        bind_mousewheel(canvas)
        
        self.scrollable_frame = scrollable_frame
        self.other_group = other_group
        self.swap_pairs = []
        
        # Add first row
        self.add_swap_row()
        
        # Bottom buttons
        self.create_bottom_buttons()
    
    def add_swap_row(self):
        """Add a new swap row"""
        row_frame = tk.Frame(
            self.scrollable_frame,
            bg="#ffffff",
            relief=tk.RAISED,
            bd=2
        )
        row_frame.pack(pady=10, padx=30, fill=tk.X)
        
        left_label = tk.Label(
            row_frame,
            text="Remove:",
            font=("Arial", 12, "bold"),
            bg="#ffffff"
        )
        left_label.pack(side=tk.LEFT, padx=15, pady=15)
        
        remove_var = tk.StringVar(value="-- Select --")
        remove_dropdown = tk.OptionMenu(
            row_frame,
            remove_var,
            *["-- Select --"] + sorted(self.state.GROUPS[self.state.shift_group])
        )
        remove_dropdown.config(font=("Arial", 11), bg="#ecf0f1", width=18)
        remove_dropdown.pack(side=tk.LEFT, padx=10, pady=15)
        
        arrow_label = tk.Label(
            row_frame,
            text="→",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#3498db"
        )
        arrow_label.pack(side=tk.LEFT, padx=15)
        
        right_label = tk.Label(
            row_frame,
            text="Replace with:",
            font=("Arial", 12, "bold"),
            bg="#ffffff"
        )
        right_label.pack(side=tk.LEFT, padx=15, pady=15)
        
        add_var = tk.StringVar(value="-- Select --")
        add_dropdown = tk.OptionMenu(
            row_frame,
            add_var,
            *["-- Select --"] + sorted(self.state.GROUPS[self.other_group])
        )
        add_dropdown.config(font=("Arial", 11), bg="#ecf0f1", width=18)
        add_dropdown.pack(side=tk.LEFT, padx=10, pady=15)
        
        def delete_row():
            self.swap_pairs.remove((remove_var, add_var))
            row_frame.destroy()
        
        delete_btn = tk.Button(
            row_frame,
            text="✕",
            font=("Arial", 11, "bold"),
            bg="#e74c3c",
            fg="white",
            width=4,
            command=delete_row
        )
        delete_btn.pack(side=tk.LEFT, padx=15, pady=15)
        
        self.swap_pairs.append((remove_var, add_var))
    
    def create_bottom_buttons(self):
        """Create bottom action buttons"""
        bottom_frame = tk.Frame(self.window, bg="#f0f0f0")
        bottom_frame.pack(side=tk.BOTTOM, pady=30, fill=tk.X, padx=30)
        
        add_row_btn = tk.Button(
            bottom_frame,
            text="+ Add Another Swap",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            width=22,
            height=2,
            command=self.add_swap_row
        )
        add_row_btn.pack(pady=10)
        
        confirm_btn = tk.Button(
            bottom_frame,
            text="Confirm Swap",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            width=22,
            height=2,
            command=self.confirm_swap
        )
        confirm_btn.pack(pady=10)
        
        close_btn = tk.Button(
            bottom_frame,
            text="Close",
            font=("Arial", 12, "bold"),
            bg="#95a5a6",
            fg="white",
            width=22,
            height=2,
            command=self.window.destroy
        )
        close_btn.pack(pady=10)
    
    def confirm_swap(self):
        """Confirm the shift swap"""
        removed = []
        added = []
        
        for remove_var, add_var in self.swap_pairs:
            remove_worker = remove_var.get()
            add_worker = add_var.get()
            
            if remove_worker != "-- Select --" and add_worker != "-- Select --":
                if remove_worker not in removed:
                    removed.append(remove_worker)
                if add_worker not in added:
                    added.append(add_worker)
        
        if not removed and not added:
            messagebox.showinfo("No Changes", "No valid swaps selected")
            return
        
        self.state.add_shift_swap(removed, added)
        self.window.destroy()