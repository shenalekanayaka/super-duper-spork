"""
Temporary workers dialog
"""
import tkinter as tk
import json
import os
from tkinter import messagebox, simpledialog

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

        # Frequent workers section
        frequent_workers = self.load_frequent_workers()

        if frequent_workers:
            frequent_frame = tk.Frame(self.window, bg="#e8f4f8", relief=tk.RAISED, bd=2)
            frequent_frame.pack(pady=10, padx=40, fill=tk.X)
            
            frequent_label = tk.Label(
                frequent_frame,
                text="⚡ Quick Add Frequent Temp Workers:",
                font=("Arial", 12, "bold"),
                bg="#e8f4f8"
            )
            frequent_label.pack(pady=5)
            
            # Checkboxes for frequent workers
            self.frequent_vars = {}
            checkbox_container = tk.Frame(frequent_frame, bg="#e8f4f8")
            checkbox_container.pack(pady=10, padx=20)
            
            for i, worker in enumerate(frequent_workers):
                var = tk.BooleanVar()
                self.frequent_vars[worker] = var
                
                cb = tk.Checkbutton(
                    checkbox_container,
                    text=worker,
                    variable=var,
                    font=("Arial", 11),
                    bg="#e8f4f8",
                    activebackground="#e8f4f8"
                )
                # Arrange in 3 columns
                cb.grid(row=i//3, column=i%3, sticky="w", padx=20, pady=5)
        else:
            self.frequent_vars = {}

        
        
        text_frame = tk.Frame(self.window, bg="#f0f0f0")
        text_frame.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(text_frame, height=10, width=20, font=("Arial", 13))
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        def confirm_temp():
            # Get manually entered names
            manual_names = text_widget.get("1.0", tk.END).strip().split("\n")
            manual_names = [n.strip() for n in manual_names if n.strip()]
            
            # Get checked frequent workers
            checked_workers = [name for name, var in self.frequent_vars.items() if var.get()]
            
            # Combine both lists (remove duplicates)
            all_names = list(set(checked_workers + manual_names))
            
            if all_names:
                self.state.add_temp(all_names)
                messagebox.showinfo("Success", f"Added {len(all_names)} temporary worker(s)")
                self.window.destroy()
            else:
                messagebox.showwarning("No Input", "Please select or enter temporary workers")
        
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

    def load_frequent_workers(self):
        """Load list of frequent temp workers"""
        preset_file = "data/frequent_temp_workers.json"
        if os.path.exists(preset_file):
            with open(preset_file, 'r') as f:
                return json.load(f)
        return []

