"""
History viewer screen for viewing past allocations
"""
import tkinter as tk
from tkinter import messagebox
import os
import json
from datetime import datetime, timedelta
from ui.screens.base_screen import BaseScreen


class HistoryViewerScreen(BaseScreen):
    """Screen for viewing historical allocations with navigation"""
    
    def show(self, **kwargs):
        self.current_filepath = kwargs.get('filepath')
        self.edit_mode = False
        
        if not self.current_filepath or not os.path.exists(self.current_filepath):
            messagebox.showerror("Error", "Allocation file not found")
            self.app.show_screen('date_shift')
            return
        

        filename = os.path.basename(self.current_filepath)
        parts = filename.replace('Allocation_', '').replace('.json', '').split('_')
        intended_date = parts[0]  # 2025-10-14
        intended_shift = parts[1]  # Morning
        
        # Load the allocation data
        if not self.state.load_allocation_from_json(self.current_filepath):
            messagebox.showerror("Error", "Failed to load allocation data")
            self.app.show_screen('date_shift')
            return
        
        # Override with the intended date/shift from filename (not from JSON metadata)
        self.state.selected_date = intended_date
        self.state.shift_time = intended_shift
        
        # Title with date and shift info
        title_text = f"History: {self.state.selected_date} - {self.state.shift_time} Shift"
        title = self.create_title(title_text, 24)
        title.pack(pady=20)
        
        # Bottom buttons
        self.create_bottom_buttons()

        # Navigation bar
        self.create_navigation_bar()
        
        # Group info
        info_text = f"Group: {self.state.shift_group}"
        info = tk.Label(
            self.main_frame,
            text=info_text,
            font=("Arial", 13, "bold"),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        info.pack(pady=5)
        
        # Two column layout for results
        content_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left column - Processes
        self.create_processes_results(content_frame)
        
        # Right column - Compression
        self.create_compression_results(content_frame)
        
        # Unassigned workers
        self.create_unassigned_section()
        
    
    def create_navigation_bar(self):
        """Create navigation bar for switching between dates/shifts"""
        nav_frame = tk.Frame(self.main_frame, bg="#ffffff", relief=tk.RAISED, bd=2)
        nav_frame.pack(fill=tk.X, padx=30, pady=10)
        
        # Previous date button
        prev_date_btn = tk.Button(
            nav_frame,
            text="◄ Previous Date",
            font=("Arial", 11, "bold"),
            bg="#3498db",
            fg="white",
            width=15,
            height=2,
            command=self.navigate_previous_date
        )
        prev_date_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Previous shift button
        prev_shift_btn = tk.Button(
            nav_frame,
            text="◄ Previous Shift",
            font=("Arial", 11, "bold"),
            bg="#9b59b6",
            fg="white",
            width=15,
            height=2,
            command=self.navigate_previous_shift
        )
        prev_shift_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Current date/shift label (centered)
        current_label = tk.Label(
            nav_frame,
            text=f"{self.state.selected_date}\n{self.state.shift_time} Shift",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        )
        current_label.pack(side=tk.LEFT, expand=True, padx=20, pady=10)
        
        # Next shift button
        next_shift_btn = tk.Button(
            nav_frame,
            text="Next Shift ►",
            font=("Arial", 11, "bold"),
            bg="#9b59b6",
            fg="white",
            width=15,
            height=2,
            command=self.navigate_next_shift
        )
        next_shift_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Next date button
        next_date_btn = tk.Button(
            nav_frame,
            text="Next Date ►",
            font=("Arial", 11, "bold"),
            bg="#3498db",
            fg="white",
            width=15,
            height=2,
            command=self.navigate_next_date
        )
        next_date_btn.pack(side=tk.LEFT, padx=10, pady=10)
    
    def navigate_previous_date(self):
        """Navigate to previous date (same shift)"""
        current_date = datetime.strptime(self.state.selected_date, "%Y-%m-%d")
        previous_date = current_date - timedelta(days=1)
        new_date_str = previous_date.strftime("%Y-%m-%d")
        
        self.navigate_to_date_shift(new_date_str, self.state.shift_time)
    
    def navigate_next_date(self):
        """Navigate to next date (same shift)"""
        current_date = datetime.strptime(self.state.selected_date, "%Y-%m-%d")
        next_date = current_date + timedelta(days=1)
        new_date_str = next_date.strftime("%Y-%m-%d")
        
        self.navigate_to_date_shift(new_date_str, self.state.shift_time)
    
    def navigate_previous_shift(self):
        """Navigate to previous shift (same date)"""
        # Toggle between Morning and Evening
        new_shift = "Evening" if self.state.shift_time == "Morning" else "Morning"
        
        # If going from Morning to Evening, go to previous date
        if new_shift == "Evening":
            current_date = datetime.strptime(self.state.selected_date, "%Y-%m-%d")
            previous_date = current_date - timedelta(days=1)
            new_date_str = previous_date.strftime("%Y-%m-%d")
            self.navigate_to_date_shift(new_date_str, new_shift)
        else:
            self.navigate_to_date_shift(self.state.selected_date, new_shift)
    
    def navigate_next_shift(self):
        """Navigate to next shift (same date)"""
        # Toggle between Morning and Evening
        new_shift = "Evening" if self.state.shift_time == "Morning" else "Morning"
        
        # If going from Evening to Morning, go to next date
        if new_shift == "Morning":
            current_date = datetime.strptime(self.state.selected_date, "%Y-%m-%d")
            next_date = current_date + timedelta(days=1)
            new_date_str = next_date.strftime("%Y-%m-%d")
            self.navigate_to_date_shift(new_date_str, new_shift)
        else:
            self.navigate_to_date_shift(self.state.selected_date, new_shift)
    
    def navigate_to_date_shift(self, date, shift):
        """Navigate to a specific date and shift"""
        exists, filepath = self.state.check_allocation_exists(date, shift)
        
        if exists:
            self.app.show_screen('history_viewer', filepath=filepath)
        else:
            messagebox.showinfo(
                "No Allocation Found",
                f"No allocation found for:\n{date} - {shift} Shift"
            )
    
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

         # ADD THIS DEBUG:
        print("\n" + "="*60)
        print("DEBUG: create_processes_results")
        print("="*60)
        print(f"PROCESSES: {self.state.PROCESSES}")
        print(f"Allocations keys: {list(self.state.allocations.keys())}")

        # After process_label.pack(pady=10), add:
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

        # After process_label.pack(pady=10), add:
        if self.edit_mode:
            add_process_btn = tk.Button(
                text="➕ Add New Process",
                font=("Arial", 11, "bold"),
                bg="#27ae60",
                fg="white",
                command=lambda: self.add_new_allocation('process')
            )
            add_process_btn.pack(pady=5)
        
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
            button_frame.pack(side=tk.BOTTOM, pady=10, fill=tk.X, padx=20, before=self.main_frame.winfo_children()[0])
            
            back_btn = self.create_button(
                button_frame,
                "← Back to Date Selection",
                lambda: self.app.show_screen('date_shift'),
                bg="#95a5a6",
                height=2 
            )
            back_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # NEW: Edit button with password protection
            edit_btn = self.create_button(
                button_frame,
                "✏️ Edit Allocation",
                self.edit_allocation,
                bg="#f39c12",
                height=2
            )
            edit_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            export_btn = self.create_button(
                button_frame,
                "📄 Export PDF",
                self.export_current,
                bg="#16a085",
                height=2
            )
            export_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)


            # Add after the export button
            audit_btn = self.create_button(
                button_frame,
                "📋 View Audit Trail",
                lambda: self.app.show_screen('audit_log', 
                                            allocation_date=self.state.selected_date,
                                            shift_time=self.state.shift_time,
                                            filepath=self.current_filepath),
                bg="#9b59b6",
                height=2
            )
            audit_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            exit_btn = self.create_button(
                button_frame,
                "Exit",
                self.root.destroy,
                bg="#34495e",
                height=2
            )
            exit_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def edit_allocation(self):
        """Edit current allocation with password protection"""
        from ui.dialogs.password_dialog import PasswordDialog
        
        # Show password dialog
        password_dialog = PasswordDialog(self.root)
        authenticated = password_dialog.show()
        
        if authenticated:
            # Set edit mode flag in state
            self.state.is_editing_history = True
            self.state.editing_filepath = self.current_filepath
            
            # Go to results screen in edit mode
            self.app.show_screen('results', edit_mode=True)
        else:
            # User cancelled or wrong password
            pass
    
    def export_current(self):
        """Export current history view to PDF"""
        from export_results import ResultsExporter
        from tkinter import messagebox
        import platform
        import subprocess
        
        try:
            exporter = ResultsExporter(self.state)
            pdf_file = exporter.export_to_pdf(self.state.shift_time)
            
            result = messagebox.askyesno(
                "Export Successful",
                f"PDF created successfully!\n\n"
                f"{os.path.basename(pdf_file)}\n\n"
                f"Do you want to open the folder?"
            )
            
            if result:
                folder = os.path.dirname(pdf_file)
                if platform.system() == "Windows":
                    os.startfile(folder)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", folder])
                else:
                    subprocess.Popen(["xdg-open", folder])
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export:\n{str(e)}")