"""
Overtime workers dialog
"""
import tkinter as tk
from utils.helpers import bind_mousewheel


class OvertimeDialog:
    """Dialog for adding overtime workers"""
    
    def __init__(self, root, state):
        self.root = root
        self.state = state
        self.window = None
        self.overtime_vars = {}
    
    def show(self):
        """Display the overtime workers dialog"""
        other_group = "Group B" if self.state.shift_group == "Group A" else "Group A"
        other_workers = self.state.GROUPS[other_group]
        
        self.window = tk.Toplevel(self.root)
        self.window.title(f"Add Overtime Workers from {other_group}")
        self.window.state('zoomed')
        self.window.configure(bg="#f0f0f0")
        
        title = tk.Label(
            self.window,
            text=f"Select Overtime Workers\nfrom {other_group}",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title.pack(pady=40)
        
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
        
        bind_mousewheel(canvas)
        
        # Checkboxes in 4 columns (sorted alphabetically)
        self.overtime_vars = {}
        col_count = 4
        row = 0
        col = 0
        
        for worker in sorted(other_workers):
            if worker not in self.state.overtime_workers:
                var = tk.BooleanVar(value=False)
                self.overtime_vars[worker] = var
                cb = tk.Checkbutton(
                    scrollable_frame,
                    text=f"{worker} (Overtime)",
                    variable=var,
                    font=("Arial", 14),
                    bg="#f0f0f0",
                    selectcolor="#ecf0f1",
                    anchor="w",
                    padx=10
                )
                cb.grid(row=row, column=col, sticky="w", padx=20, pady=10)
                
                col += 1
                if col >= col_count:
                    col = 0
                    row += 1
        
        canvas.pack(fill=tk.BOTH, expand=True, pady=20, padx=30)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=20)
        
        # Bottom buttons
        button_frame = tk.Frame(self.window, bg="#f0f0f0")
        button_frame.pack(side=tk.BOTTOM, pady=30)
        
        confirm_btn = tk.Button(
            button_frame,
            text="Add Selected Workers",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            width=22,
            height=2,
            command=self.confirm_overtime
        )
        confirm_btn.pack(pady=10)
        
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=("Arial", 12, "bold"),
            bg="#95a5a6",
            fg="white",
            width=22,
            height=2,
            command=self.window.destroy
        )
        close_btn.pack(pady=10)
    
    def confirm_overtime(self):
        """Confirm overtime worker selection"""
        selected = [w for w, var in self.overtime_vars.items() if var.get()]
        if selected:
            self.state.add_overtime(selected)
        self.window.destroy()