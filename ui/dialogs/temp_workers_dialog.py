"""
Temporary workers dialog
"""
import tkinter as tk
from tkinter import messagebox


class TempWorkersDialog:
    """Dialog for adding temporary workers"""


    
    def __init__(self, root, state):
        self.root = root
        self.state = state
        self.window = None
    
    def show(self):
        """Display the temporary workers dialog"""
        self.window = tk.Toplevel(self.root)
        self.window.title("Add Temporary Workers")
        self.window.state('zoomed')
        self.window.configure(bg="#f0f0f0")
        
        title = tk.Label(
            self.window,
            text="Add Temporary Workers",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title.pack(pady=40)
        
        instruction = tk.Label(
            self.window,
            text="Enter worker names (one per line):",
            font=("Arial", 14),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        instruction.pack(pady=20)
        
        text_frame = tk.Frame(self.window, bg="#f0f0f0")
        text_frame.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(text_frame, height=10, width=20, font=("Arial", 13))
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        def confirm_temp():
            names = text_widget.get("1.0", tk.END).strip().split("\n")
            names = [n.strip() for n in names if n.strip()]
            
            if names:
                self.state.add_temp(names)
                messagebox.showinfo("Success", f"Added {len(names)} temporary worker(s)")
                self.window.destroy()
            else:
                messagebox.showwarning("No Input", "You have not added any temporary workers")
        
        # Bottom buttons
        button_frame = tk.Frame(self.window, bg="#f0f0f0")
        button_frame.pack(side=tk.BOTTOM, pady=30)

        btn_padx = 60  # horizontal padding in pixels
        btn_pady = 8   # vertical padding in pixels
        
        confirm_btn = tk.Button(
            button_frame,
            text="Add Workers",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            width=22,
            padx=btn_padx,  # Use pixel padding
            pady=btn_pady,   # Use pixel padding
            command=confirm_temp
        )
        confirm_btn.pack(pady=10)
        
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=("Arial", 12, "bold"),
            bg="#95a5a6",
            fg="white",
            width=22,
            padx=btn_padx,  # Use pixel padding
            pady=btn_pady,   # Use pixel padding
            command=self.window.destroy
        )
        close_btn.pack(pady=10)