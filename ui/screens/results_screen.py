"""
Results screen with product information and edit mode
"""
import tkinter as tk
import os
from tkinter import messagebox
from ui.screens.base_screen import BaseScreen


class ResultsScreen(BaseScreen):
    """Screen displaying allocation results"""

    def save_changes(self):
        """Save changes to the allocation"""
        result = messagebox.askyesno(
            "Save Changes",
            "Are you sure you want to save these changes?\n\n"
            "This will update the allocation file."
        )
        
        if result:
            try:
                # Log the edit to audit trail
                try:
                    self.state.audit_trail.log_edit(
                        change_type='ALLOCATION_EDITED',
                        allocation_date=self.state.selected_date,
                        shift_time=self.state.shift_time,
                        details={
                            'allocations_count': len(self.state.allocations),
                            'allocations': {k: len(v) for k, v in self.state.allocations.items()},
                            'total_assigned_workers': sum(len(v) for v in self.state.allocations.values()),
                            'unassigned_workers_count': len(self.state.available_workers),
                            'overtime_workers': len(self.state.overtime_workers),
                            'temp_workers': len(self.state.temp_workers)
                        }
                    )
                except Exception as e:
                    print(f"Warning: Could not log to audit trail: {e}")
                
                # Save the allocation to JSON
                from export_results import ResultsExporter
                exporter = ResultsExporter(self.state)
                json_file = exporter.save_allocation_json(self.state.shift_time)
                
                # Also regenerate PDF
                pdf_file = exporter.export_to_pdf(self.state.shift_time)
                
                messagebox.showinfo(
                    "Changes Saved",
                    "Allocation has been successfully updated!\n\n"
                    f"Updated files:\n"
                    f"• {os.path.basename(json_file)}\n"
                    f"• {os.path.basename(pdf_file)}"
                )
                
                # Clear edit mode flags
                self.state.is_editing_history = False
                
                # Return to history viewer with the updated file
                self.app.show_screen('history_viewer', filepath=json_file)
                
            except Exception as e:
                messagebox.showerror(
                    "Save Error",
                    f"Failed to save changes:\n{str(e)}"
                )
            

    
    def show(self, **kwargs):
        # Check if we're in edit mode
        self.edit_mode = kwargs.get('edit_mode', False)
        
        # Title changes based on mode
        if self.edit_mode:
            title_text = f"✏️ Editing Allocation - {self.state.selected_date} - {self.state.shift_time}"
            title = self.create_title(title_text, 24)
            title.pack(pady=20)
            
            # Add edit mode warning
            warning_frame = tk.Frame(self.main_frame, bg="#fff3cd", relief=tk.RAISED, bd=2)
            warning_frame.pack(fill=tk.X, padx=30, pady=5)
            
            warning_label = tk.Label(
                warning_frame,
                text="⚠️ EDIT MODE: You can modify this allocation. Click 'Save Changes' when done.",
                font=("Arial", 12, "bold"),
                bg="#fff3cd",
                fg="#856404"
            )
            warning_label.pack(pady=10)
        else:
            title = self.create_title("Allocation Results", 26)
            title.pack(pady=20)
        
        # Two column layout
        content_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left column - Processes
        self.create_processes_results(content_frame)
        
        # Right column - Compression
        self.create_compression_results(content_frame)
        
        # Unassigned workers
        self.create_unassigned_section()
        
        # Bottom buttons (different for edit mode)
        self.create_bottom_buttons()
    
    def create_processes_results(self, parent):
        """Create processes results section"""
        left_frame = tk.Frame(parent, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        process_label = tk.Label(
            left_frame,
            text="Production Processes",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        process_label.pack(pady=10)
        
        if self.edit_mode:
            add_process_btn = tk.Button(
                left_frame,
                text="➕ Add New Process",
                font=("Arial", 11, "bold"),
                bg="#27ae60",
                fg="white",
                command=lambda: self.add_new_allocation('process')
            )
            add_process_btn.pack(pady=5)

        canvas, scrollbar, scrollable_frame = self.create_scrollable_frame(left_frame)
        
        # Create 3 column grid
        grid_frame = tk.Frame(scrollable_frame, bg="#ffffff")
        grid_frame.pack(padx=5, pady=5)
        
        process_found = False
        result_idx = 0
        for process_data in self.state.PROCESSES:
            process_name = process_data[0]
            if process_name in self.state.allocations:
                process_found = True
                workers = self.state.allocations[process_name]
                product = self.state.get_product_for_allocation(process_name)
                row = result_idx // 3
                col = result_idx % 3
                self.create_result_card(grid_frame, process_name, workers, product, row, col)
                result_idx += 1
        
        if not process_found:
            no_data = tk.Label(
                scrollable_frame,
                text="No processes allocated",
                font=("Arial", 12),
                bg="#ffffff",
                fg="#7f8c8d"
            )
            no_data.pack(pady=20)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_compression_results(self, parent):
        """Create compression results section"""
        right_frame = tk.Frame(parent, bg="#f0f0f0")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        comp_label = tk.Label(
            right_frame,
            text="Compression Machines",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        comp_label.pack(pady=10)
        

        if self.edit_mode:
            add_machine_btn = tk.Button(
                right_frame,
                text="➕ Add New Machine",
                font=("Arial", 11, "bold"),
                bg="#27ae60",
                fg="white",
                command=lambda: self.add_new_allocation('machine')
            )
            add_machine_btn.pack(pady=5)

        canvas, scrollbar, scrollable_frame = self.create_scrollable_frame(right_frame)
        
        # Create 3 column grid
        grid_frame = tk.Frame(scrollable_frame, bg="#ffffff")
        grid_frame.pack(padx=5, pady=5)
        
        comp_found = False
        result_idx = 0
        for machine_data in self.state.compression_machines:
            machine_name = machine_data[0]
            if machine_name in self.state.allocations:
                comp_found = True
                workers = self.state.allocations[machine_name]
                product = self.state.get_product_for_allocation(machine_name)
                row = result_idx // 3
                col = result_idx % 3
                self.create_result_card(grid_frame, machine_name, workers, product, row, col)
                result_idx += 1
        
        if not comp_found:
            no_data = tk.Label(
                scrollable_frame,
                text="No machines allocated",
                font=("Arial", 12),
                bg="#ffffff",
                fg="#7f8c8d"
            )
            no_data.pack(pady=20)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_result_card(self, parent, name, workers, product=None, row=0, col=0):
        """Create a result card in grid layout"""
        card_frame = tk.Frame(parent, bg="#ecf0f1", relief=tk.RAISED, bd=2)
        card_frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        
        parent.grid_columnconfigure(col, weight=1, minsize=200)
        
        # Add edit button in edit mode
        # THIS MUST BE HERE:
        if self.edit_mode:
            btn_container = tk.Frame(card_frame, bg="#ecf0f1")
            btn_container.pack(side=tk.TOP, anchor="e", padx=5, pady=2)
            
            edit_btn = tk.Button(
                btn_container,
                text="✏️",
                font=("Arial", 10, "bold"),
                bg="#f39c12",
                fg="white",
                width=3,
                command=lambda: self.edit_card(name)
            )
            edit_btn.pack(side=tk.LEFT, padx=2)
            
            delete_btn = tk.Button(
                btn_container,
                text="🗑️",
                font=("Arial", 10, "bold"),
                bg="#e74c3c",
                fg="white",
                width=3,
                command=lambda: self.delete_card(name)
            )
            delete_btn.pack(side=tk.LEFT, padx=2)
        
        name_label = tk.Label(
            card_frame,
            text=f"{name}:",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1"
        )
        name_label.pack(padx=10, pady=5, anchor="w")
        
        # Show product if available
        if product:
            display_product = product[:40] + "..." if len(product) > 40 else product
            product_label = tk.Label(
                card_frame,
                text=f"Product: {display_product}",
                font=("Arial", 9, "italic"),
                bg="#ecf0f1",
                fg="#3498db",
                wraplength=180,
                justify=tk.LEFT
            )
            product_label.pack(padx=10, pady=2, anchor="w")
        
        # Show lot number if available
        lot_number = self.state.get_lot_number_for_allocation(name)
        if lot_number:
            lot_label = tk.Label(
                card_frame,
                text=f"Lot: {lot_number}",
                font=("Arial", 9, "italic"),
                bg="#ecf0f1",
                fg="#e67e22",
                wraplength=180,
                justify=tk.LEFT
            )
            lot_label.pack(padx=10, pady=2, anchor="w")
        
        worker_displays = [self.state.get_worker_display_name(w) for w in workers]
        
        workers_label = tk.Label(
            card_frame,
            text=", ".join(worker_displays),
            font=("Arial", 9),
            bg="#ecf0f1",
            wraplength=180,
            justify=tk.LEFT
        )
        workers_label.pack(padx=15, pady=5, anchor="w")
    
    def edit_card(self, allocation_name):
        """Edit a specific allocation card"""
        from ui.dialogs.edit_allocation_dialog import EditAllocationDialog
        
        dialog = EditAllocationDialog(self.root, self.state, allocation_name)
        if dialog.show():
            # Refresh the screen to show changes
            self.app.show_screen('results', edit_mode=True)

    def delete_card(self, allocation_name):
        """Delete an allocation"""
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete:\n{allocation_name}?\n\nWorkers will be returned to unassigned pool.",
            parent=self.root
        )
        
        if result:
            # Get workers for logging
            workers = self.state.allocations.get(allocation_name, [])
            product = self.state.get_product_for_allocation(allocation_name)
            lot_number = self.state.get_lot_number_for_allocation(allocation_name)
            
            # Log the deletion
            self.state.audit_trail.log_edit(
                change_type='ALLOCATION_DELETED',
                allocation_date=self.state.selected_date,
                shift_time=self.state.shift_time,
                details={
                    'allocation_name': allocation_name,
                    'workers': workers,
                    'worker_count': len(workers),
                    'product': product or 'N/A',
                    'lot_number': lot_number or 'N/A'
                }
            )

            self.state.audit_trail.log_edit(
                change_type='WORKER_ASSIGNMENT_CHANGED',
                allocation_date=self.state.selected_date,
                shift_time=self.state.shift_time,
                details={
                    'allocation_name': self.allocation_name,
                    'previous_workers': previous_workers,  # Store this before changes
                    'new_workers': new_workers,
                    'workers_added': list(set(new_workers) - set(previous_workers)),
                    'workers_removed': list(set(previous_workers) - set(new_workers))
                }
            )
            
        


    def add_new_allocation(self, allocation_type):
        """Add new process or machine allocation"""
        from ui.dialogs.add_allocation_dialog import AddAllocationDialog
        
        dialog = AddAllocationDialog(self.root, self.state, allocation_type)
        if dialog.show():
            # Refresh the screen to show new allocation
            self.app.show_screen('results', edit_mode=True)
    
    def create_unassigned_section(self):
        """Create unassigned workers section"""
        if self.state.available_workers:
            unassigned_frame = tk.Frame(
                self.main_frame,
                bg="#ffe6e6",
                relief=tk.RAISED,
                bd=2
            )
            unassigned_frame.pack(fill=tk.X, padx=30, pady=10)
            
            unassigned_label = tk.Label(
                unassigned_frame,
                text="Unassigned Workers:",
                font=("Arial", 14, "bold"),
                bg="#ffe6e6"
            )
            unassigned_label.pack(padx=15, pady=10, anchor="w")
            
            unassigned_displays = [
                self.state.get_worker_display_name(w)
                for w in sorted(self.state.available_workers)
            ]
            
            workers_label = tk.Label(
                unassigned_frame,
                text=", ".join(unassigned_displays),
                font=("Arial", 11),
                bg="#ffe6e6",
                wraplength=900
            )
            workers_label.pack(padx=25, pady=10, anchor="w")
    
    def create_bottom_buttons(self):
            """Create bottom navigation buttons"""
            button_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
            button_frame.pack(side=tk.BOTTOM, pady=20, fill=tk.X, padx=20)
            
            if self.edit_mode:
                # Edit mode buttons
                back_btn = self.create_button(
                    button_frame,
                    "← Cancel Editing",
                    self.cancel_editing,
                    bg="#95a5a6",
                    width=20
                )
                back_btn.pack(side=tk.LEFT, padx=5)
                
                save_btn = self.create_button(
                    button_frame,
                    "💾 Save Changes",
                    self.save_changes,
                    bg="#27ae60",
                    width=20
                )
                save_btn.pack(side=tk.LEFT, padx=5)
                
                exit_btn = self.create_button(
                    button_frame,
                    "Exit",
                    self.root.destroy,
                    bg="#34495e",
                    width=20
                )
                exit_btn.pack(side=tk.RIGHT, padx=5)
            else:
                # Normal mode buttons
                back_btn = self.create_button(
                    button_frame,
                    "← Back to Menu",
                    lambda: self.app.show_screen('main_menu'),
                    bg="#3498db",
                    width=20
                )
                back_btn.pack(side=tk.LEFT, padx=5)
                
                export_btn = self.create_button(
                    button_frame,
                    "📊 Save",
                    self.export_results,
                    bg="#16a085",
                    width=20
                )
                export_btn.pack(side=tk.LEFT, padx=5)
                
                restart_btn = self.create_button(
                    button_frame,
                    "Restart",
                    self.app.restart,
                    bg="#e74c3c",
                    width=20
                )
                restart_btn.pack(side=tk.LEFT, padx=5)
                
                exit_btn = self.create_button(
                    button_frame,
                    "Exit",
                    self.root.destroy,
                    bg="#34495e",
                    width=20
                )
                exit_btn.pack(side=tk.LEFT, padx=5)
    
    def cancel_editing(self):
        """Cancel editing and return to history viewer"""
        result = messagebox.askyesno(
            "Cancel Editing",
            "Are you sure you want to cancel?\n\nAny unsaved changes will be lost."
        )
        
        if result:
            # Clear edit mode flags
            self.state.is_editing_history = False
            
            # Return to history viewer with the original file
            if hasattr(self.state, 'editing_filepath'):
                self.app.show_screen('history_viewer', filepath=self.state.editing_filepath)
            else:
                self.app.show_screen('date_shift')
    
    def save_changes(self):
        """Save changes to the allocation"""
        result = messagebox.askyesno(
            "Save Changes",
            "Are you sure you want to save these changes?\n\n"
            "This will update the allocation file."
        )
        
        if result:
            try:
                # Log the edit to audit trail
                try:
                    self.state.audit_trail.log_edit(
                        change_type='ALLOCATION_EDITED',
                        allocation_date=self.state.selected_date,
                        shift_time=self.state.shift_time,
                        details={
                            'allocations_count': len(self.state.allocations),
                            'allocations': {k: len(v) for k, v in self.state.allocations.items()},
                            'total_assigned_workers': sum(len(v) for v in self.state.allocations.values()),
                            'unassigned_workers_count': len(self.state.available_workers),
                            'overtime_workers': len(self.state.overtime_workers),
                            'temp_workers': len(self.state.temp_workers)
                        }
                    )
                except Exception as e:
                    print(f"Warning: Could not log to audit trail: {e}")
                
                # Save the allocation to JSON
                from export_results import ResultsExporter
                exporter = ResultsExporter(self.state)
                json_file = exporter.save_allocation_json(self.state.shift_time)
                
                # Also regenerate PDF
                pdf_file = exporter.export_to_pdf(self.state.shift_time)
                
                messagebox.showinfo(
                    "Changes Saved",
                    "Allocation has been successfully updated!\n\n"
                    f"Updated files:\n"
                    f"• {os.path.basename(json_file)}\n"
                    f"• {os.path.basename(pdf_file)}"
                )
                
                # Clear edit mode flags
                self.state.is_editing_history = False
                
                # Return to history viewer with the updated file
                self.app.show_screen('history_viewer', filepath=json_file)
                
            except Exception as e:
                messagebox.showerror(
                    "Save Error",
                    f"Failed to save changes:\n{str(e)}"
                )

    def export_results(self):
        """Export results to PDF and Excel"""
        from ui.dialogs.export_dialog import ExportDialog
        dialog = ExportDialog(self.root, self.state)
        dialog.show()