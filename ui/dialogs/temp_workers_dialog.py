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
                # Update usage dates for checked frequent workers
                self.update_worker_usage(checked_workers)
                
                # ADD NEW WORKERS TO FREQUENT LIST
                for worker in manual_names:
                    self.add_to_frequent_workers(worker)
                
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
        from datetime import datetime, timedelta
        
        preset_file = "utils/frequent_temp_workers.json"
        if os.path.exists(preset_file):
            with open(preset_file, 'r') as f:
                data = json.load(f)
                
                # Clean up old workers (not used in 30 days)
                today = datetime.now()
                active_workers = {}
                
                for worker, last_used in data.items():
                    last_used_date = datetime.strptime(last_used, "%Y-%m-%d")
                    days_since_used = (today - last_used_date).days
                    
                    if days_since_used <= 30:  # Keep if used within 30 days
                        active_workers[worker] = last_used
                
                # Save cleaned list back
                if len(active_workers) != len(data):
                    with open(preset_file, 'w') as f:
                        json.dump(active_workers, f, indent=2)
                
                return list(active_workers.keys())
        
        return []

    def update_worker_usage(self, workers):
        """Update last used date for selected workers"""
        from datetime import datetime
        
        preset_file = "utils/frequent_temp_workers.json"
        
        # Load existing data
        if os.path.exists(preset_file):
            with open(preset_file, 'r') as f:
                data = json.load(f)
        else:
            data = {}
        
        # Update dates for used workers
        today = datetime.now().strftime("%Y-%m-%d")
        for worker in workers:
            if worker in data:
                data[worker] = today
        
        # Save back
        os.makedirs("data", exist_ok=True)
        with open(preset_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_to_frequent_workers(self, worker_name):
        """Add a new worker to frequent list"""
        from datetime import datetime
        
        preset_file = "utils/frequent_temp_workers.json"
        
        if os.path.exists(preset_file):
            with open(preset_file, 'r') as f:
                data = json.load(f)
        else:
            data = {}
        
        today = datetime.now().strftime("%Y-%m-%d")
        data[worker_name] = today
        
        os.makedirs("data", exist_ok=True)
        with open(preset_file, 'w') as f:
            json.dump(data, f, indent=2)