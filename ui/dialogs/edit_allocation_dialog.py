"""
Dialog for editing allocation details
"""
import tkinter as tk
from tkinter import ttk, messagebox


class EditAllocationDialog:
    """Dialog for editing a specific allocation"""
    
    def __init__(self, parent, state, allocation_name):
        self.parent = parent
        self.state = state
        self.allocation_name = allocation_name
        self.result = False
        self.dialog = None
    
    def show(self):
        """Show edit dialog and return True if changes were made"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Edit: {self.allocation_name}")
        self.dialog.geometry("600x650")  # Increased height
        self.dialog.resizable(False, False)
        self.dialog.configure(bg="#f0f0f0")
        
        # Center the dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Title
        title = tk.Label(
            self.dialog,
            text=f"✏️ Editing: {self.allocation_name}",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        # Get current allocation data
        current_workers = self.state.allocations.get(self.allocation_name, [])
        current_product = self.state.get_product_for_allocation(self.allocation_name) or ""
        current_lot = self.state.get_lot_number_for_allocation(self.allocation_name) or ""

        
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
        self.product_entry.insert(0, current_product)
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
        self.lot_entry.insert(0, current_lot)
        self.lot_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Workers section
        workers_frame = tk.LabelFrame(
            self.dialog,
            text="Assigned Workers",
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
        
        # Populate listbox with all workers
        all_workers = set(current_workers) | set(self.state.available_workers)
        if hasattr(self.state, 'all_shift_workers'):
            all_workers = self.state.all_shift_workers

        self.worker_list = sorted(all_workers)

        for idx, worker in enumerate(self.worker_list):
            display_name = self.state.get_worker_display_name(worker)
            self.workers_listbox.insert(tk.END, display_name)
            
            # Select currently assigned workers
            if worker in current_workers:
                self.workers_listbox.selection_set(idx)
        
        # Instructions
        instructions = tk.Label(
            workers_frame,
            text="Select/deselect workers using Ctrl+Click (Cmd+Click on Mac)",
            font=("Arial", 9, "italic"),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        instructions.pack(pady=5)
        
        # Buttons at BOTTOM - pack with side=BOTTOM
        button_frame = tk.Frame(self.dialog, bg="#f0f0f0")
        button_frame.pack(side=tk.BOTTOM, pady=20, fill=tk.X)
        
        save_btn = tk.Button(
            button_frame,
            text="💾 Save Changes",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            width=20,
            command=self.save_changes,
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, padx=10, pady=5, ipady=10)
        
        cancel_btn = tk.Button(
            button_frame,
            text="✗ Cancel",
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            width=20,
            command=self.cancel,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=10, pady=5, ipady=10)
        
        # Wait for dialog to close
        self.parent.wait_window(self.dialog)
        
        return self.result

    def save_changes(self):
        """Save changes to the allocation"""
        # Get selected workers
        selected_indices = self.workers_listbox.curselection()
        new_workers = [self.worker_list[i] for i in selected_indices]
        
        if not new_workers:
            messagebox.showwarning(
                "No Workers",
                "Please select at least one worker for this allocation.",
                parent=self.dialog
            )
            return
        
        # Get product and lot
        new_product = self.product_entry.get().strip()
        new_lot = self.lot_entry.get().strip()
        
        # Get old workers to return them to available pool
        old_workers = set(self.state.allocations.get(self.allocation_name, []))
        new_workers_set = set(new_workers)
        
        # Workers being removed from this allocation
        removed_workers = old_workers - new_workers_set
        
        # Workers being added to this allocation
        added_workers = new_workers_set - old_workers
        
        # Update allocations
        self.state.allocations[self.allocation_name] = new_workers
        
        # Update available workers
        # Update available workers
        # Convert to set if it's a list
        if isinstance(self.state.available_workers, list):
            available_set = set(self.state.available_workers)
        else:
            available_set = self.state.available_workers

        # Add removed workers back
        available_set.update(removed_workers)

        # Remove added workers
        available_set -= added_workers

        # Convert back to list if needed
        if isinstance(self.state.available_workers, list):
            self.state.available_workers = list(available_set)
        else:
            self.state.available_workers = available_set
        
        # Update product and lot number
        if new_product:
            self.state.allocation_products[self.allocation_name] = new_product
        elif self.allocation_name in self.state.allocation_products:
            del self.state.allocation_products[self.allocation_name]
        
        if new_lot:
            self.state.allocation_lot_numbers[self.allocation_name] = new_lot
        elif self.allocation_name in self.state.allocation_lot_numbers:
            del self.state.allocation_lot_numbers[self.allocation_name]
        
        self.result = True
        self.dialog.destroy()

        try:
            from export_results import ResultsExporter
            exporter = ResultsExporter(self.state)
            exporter.save_allocation_json(self.state.shift_time)
            print("DEBUG: Auto-saved changes to JSON")
        except Exception as e:
            print(f"ERROR: Auto-save failed: {e}")
    
    def cancel(self):
        """Cancel editing"""
        self.result = False
        self.dialog.destroy()

    def delete_card(self, allocation_name):
        """Delete an allocation"""
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete:\n{allocation_name}?\n\nWorkers will be returned to unassigned pool.",
            parent=self.root
        )
        
        if result:
            # Get workers from this allocation
            workers = self.state.allocations.get(allocation_name, [])
            
            # Return workers to available pool
            if isinstance(self.state.available_workers, list):
                self.state.available_workers.extend(workers)
            else:
                self.state.available_workers.update(workers)
            
            # Remove allocation
            del self.state.allocations[allocation_name]
            
            # Remove product/lot if exists
            if allocation_name in self.state.allocation_products:
                del self.state.allocation_products[allocation_name]
            if allocation_name in self.state.allocation_lot_numbers:
                del self.state.allocation_lot_numbers[allocation_name]
            
            # Refresh screen
            self.app.show_screen('results', edit_mode=True)

    def add_new_allocation(self, allocation_type):
        """Add new process or machine allocation"""
        from ui.dialogs.add_allocation_dialog import AddAllocationDialog
        
        dialog = AddAllocationDialog(self.root, self.state, allocation_type)
        if dialog.show():
            # Refresh the screen to show new allocation
            self.app.show_screen('results', edit_mode=True)