"""
Dialog for adding new allocation
"""
import tkinter as tk
from tkinter import ttk, messagebox


class AddAllocationDialog:
    """Dialog for adding a new process or machine allocation"""
    
    def __init__(self, parent, state, allocation_type):
        self.parent = parent
        self.state = state
        self.allocation_type = allocation_type  # 'process' or 'machine'
        self.result = False
        self.dialog = None
    
    def show(self):
        
        """Show add dialog and return True if allocation was created"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Add New {self.allocation_type.title()}")
        self.dialog.geometry("600x800")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg="#f0f0f0")
        
        # Center the dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Title
        title = tk.Label(
            self.dialog,
            text=f"➕ Add New {self.allocation_type.title()}",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        # Selection section
        selection_frame = tk.LabelFrame(
            self.dialog,
            text=f"Select {self.allocation_type.title()}",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50",
            padx=20,
            pady=10
        )
        selection_frame.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(
            selection_frame,
            text=f"{self.allocation_type.title()} Name:",
            font=("Arial", 11),
            bg="#f0f0f0"
        ).pack(anchor="w", pady=5)
        
        # Get available processes or machines
        if self.allocation_type == 'process':
            available_items = [process_data[0] for process_data in self.state.PROCESSES
                            if process_data[0] not in self.state.allocations]
        else:  # machine
            available_items = [machine_data[0] for machine_data in self.state.compression_machines
                            if machine_data[0] not in self.state.allocations]
        
        if not available_items:
            messagebox.showwarning(
                "No Available Items",
                f"All {self.allocation_type}s are already allocated!",
                parent=self.dialog
            )
            self.dialog.destroy()
            return False
        
        self.name_combo = ttk.Combobox(
            selection_frame,
            values=available_items,
            font=("Arial", 11),
            width=37,
            state="readonly"
        )
        self.name_combo.pack(pady=5)
        self.name_combo.current(0)  # Select first item by default
        
        # Product section
        product_frame = tk.LabelFrame(
            self.dialog,
            text="Product Information",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50",
            padx=20,
            pady=10
        )
        product_frame.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(
            product_frame,
            text="Product:",
            font=("Arial", 11),
            bg="#f0f0f0"
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        self.product_entry = tk.Entry(
            product_frame,
            font=("Arial", 11),
            width=40
        )
        self.product_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(
            product_frame,
            text="Lot Number:",
            font=("Arial", 11),
            bg="#f0f0f0"
        ).grid(row=1, column=0, sticky="w", pady=5)
        
        self.lot_entry = tk.Entry(
            product_frame,
            font=("Arial", 11),
            width=40
        )
        self.lot_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Workers section
        workers_frame = tk.LabelFrame(
            self.dialog,
            text="Assign Workers",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50",
            padx=20,
            pady=10
        )
        workers_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # Listbox with scrollbar for workers
        listbox_frame = tk.Frame(workers_frame, bg="#f0f0f0")
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.workers_listbox = tk.Listbox(
            listbox_frame,
            font=("Arial", 11),
            height=8,
            selectmode=tk.MULTIPLE,
            yscrollcommand=scrollbar.set
        )
        self.workers_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.workers_listbox.yview)
        
        # Populate listbox with available workers
        if hasattr(self.state, 'all_shift_workers'):
            # Use only unassigned workers
            all_workers = self.state.available_workers
        else:
            all_workers = self.state.available_workers
        
        self.worker_list = sorted(list(all_workers))
        
        for idx, worker in enumerate(self.worker_list):
            display_name = self.state.get_worker_display_name(worker)
            self.workers_listbox.insert(tk.END, display_name)
        
        # Instructions
        instructions = tk.Label(
            workers_frame,
            text="Select workers using Ctrl+Click (Cmd+Click on Mac)",
            font=("Arial", 9, "italic"),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        instructions.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.dialog, bg="#f0f0f0")
        button_frame.pack(pady=20)

        
        create_btn = tk.Button(
            button_frame,
            text="✓ Create Allocation",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            width=25,
            command=self.create_allocation,
            cursor="hand2"
        )
        create_btn.pack(side=tk.LEFT, padx=10, pady=15, ipady=10)
        
        cancel_btn = tk.Button(
            button_frame,
            text="✗ Cancel",
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            width=25,
            command=self.cancel,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=10, pady=15, ipady=10)
        
        # Wait for dialog to close
        self.parent.wait_window(self.dialog)
        
        return self.result
    
    def create_allocation(self):
        """Create the new allocation"""
        # Get allocation name
        allocation_name = self.name_combo.get()
        
        if not allocation_name:
            messagebox.showwarning(
                "No Selection",
                f"Please select a {self.allocation_type}.",
                parent=self.dialog
            )
            return
        
        # Get selected workers
        selected_indices = self.workers_listbox.curselection()
        selected_workers = [self.worker_list[i] for i in selected_indices]
        
        if not selected_workers:
            messagebox.showwarning(
                "No Workers",
                "Please select at least one worker for this allocation.",
                parent=self.dialog
            )
            return
        
        # Get product and lot
        product = self.product_entry.get().strip()
        lot_number = self.lot_entry.get().strip()
        
        # Create the allocation
        self.state.allocations[allocation_name] = selected_workers
        
        # Remove workers from available pool
        if isinstance(self.state.available_workers, list):
            for worker in selected_workers:
                if worker in self.state.available_workers:
                    self.state.available_workers.remove(worker)
        else:
            self.state.available_workers -= set(selected_workers)
        
        # Add product and lot if provided
        if product:
            self.state.allocation_products[allocation_name] = product
        
        if lot_number:
            self.state.allocation_lot_numbers[allocation_name] = lot_number
        
        # Auto-save
        try:
            from export_results import ResultsExporter
            exporter = ResultsExporter(self.state)
            exporter.save_allocation_json(self.state.shift_time)
            print(f"DEBUG: Created new allocation: {allocation_name}")
        except Exception as e:
            print(f"ERROR: Auto-save failed: {e}")
        
        self.result = True
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel creating allocation"""
        self.result = False
        self.dialog.destroy()