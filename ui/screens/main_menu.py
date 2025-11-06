"""
Main menu screen with allocation options
"""
import tkinter as tk
from tkinter import messagebox
from ui.screens.base_screen import BaseScreen
from ui.components.allocation_card import AllocationCard


class MainMenuScreen(BaseScreen):
    """Main menu for allocation"""
    
    def show(self, **kwargs):
        title = self.create_title("Allocation Menu", 26)
        title.pack(pady=20)
        
        # Info
        total_workers = len(self.state.available_workers)
        overtime_count = len(self.state.overtime_workers)
        temp_count = len(self.state.temp_workers)
        
        info_text = f"Group: {self.state.shift_group} | Available Workers: {total_workers}"
        if overtime_count > 0:
            info_text += f" (includes {overtime_count} overtime)"
        if temp_count > 0:
            info_text += f" (includes {temp_count} temp)"
        
        info = tk.Label(
            self.main_frame,
            text=info_text,
            font=("Arial", 13),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        info.pack(pady=5)
        
        # Two column layout
        content_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left column - Processes
        self.create_processes_section(content_frame)
        
        # Right column - Compression
        self.create_compression_section(content_frame)
        
        # Bottom buttons
        self.create_bottom_buttons()
    
    def create_processes_section(self, parent):
        """Create the processes section"""
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
        
        canvas, v_scrollbar, h_scrollbar, scrollable_frame = self.create_scrollable_frame(left_frame, horizontal=True)
        
        # Create 3 column grid
        grid_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
        grid_frame.pack(padx=5, pady=5)
        
        # Sort processes: unfilled first, then filled
        sorted_processes = sorted(
            self.state.PROCESSES,
            key=lambda p: (
                bool(self.state.allocations.get(p[0], [])),
                p[0]
            )
        )
        
        for idx, process_data in enumerate(sorted_processes):
            process_name = process_data[0]
            slots = process_data[1]
            row = idx // 3
            col = idx % 3
            card = AllocationCard(
                grid_frame,
                process_name,
                slots,
                self.state,
                is_compression=False,
                on_allocate=lambda p=process_name, s=slots: self.app.show_screen(
                    'process_allocation',
                    process_name=p,
                    slots=s
                ),
                on_reset=self.reset_process
            )
            card.render(row, col)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, before=canvas)
    
    def create_compression_section(self, parent):
        """Create the compression section"""
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
        
        canvas, v_scrollbar, h_scrollbar, scrollable_frame = self.create_scrollable_frame(right_frame, horizontal=True)
        
        # Create 3 column grid
        grid_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
        grid_frame.pack(padx=5, pady=5)
        
        # Sort machines: unfilled first, then filled
        sorted_machines = sorted(
            self.state.compression_machines,
            key=lambda m: (
                bool(self.state.allocations.get(m[0], [])),
                m[0]
            )
        )
        
        for idx, machine_data in enumerate(sorted_machines):
            machine_name = machine_data[0]
            slots = machine_data[1]
            row = idx // 3
            col = idx % 3
            card = AllocationCard(
                grid_frame,
                machine_name,
                slots,
                self.state,
                is_compression=True,
                on_allocate=lambda m=machine_name, s=slots: self.app.show_screen(
                    'compression_allocation',
                    machine_name=m,
                    slots=s
                ),
                on_reset=self.reset_process
            )
            card.render(row, col)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, before=canvas)
    
    def create_bottom_buttons(self):
        """Create bottom navigation buttons"""
        button_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        button_frame.pack(side=tk.BOTTOM, pady=20, fill=tk.X, padx=20)
        
        back_btn = self.create_button(
            button_frame,
            "← Back",
            lambda: self.app.show_screen('actions'),
            bg="#95a5a6",
            width=15
        )
        back_btn.pack(side=tk.LEFT, padx=5)
        
        results_btn = self.create_button(
            button_frame,
            "View Results",
            lambda: self.app.show_screen('results'),
            bg="#16a085",
            width=15
        )
        results_btn.pack(side=tk.LEFT, padx=5)
        
        reset_all_btn = self.create_button(
            button_frame,
            "Reset Everything",
            self.reset_all_allocations,
            bg="#e67e22",
            width=15
        )
        reset_all_btn.pack(side=tk.LEFT, padx=5)
        
        restart_btn = self.create_button(
            button_frame,
            "Restart",
            self.app.restart,
            bg="#e74c3c",
            width=15
        )
        restart_btn.pack(side=tk.LEFT, padx=5)
    
    def reset_process(self, process_name):
        """Reset a specific process"""
        workers = self.state.allocations.get(process_name, [])
        if workers:
            confirm = messagebox.askyesno(
                "Confirm Reset",
                f"Reset {process_name}?\n\nThis will return {len(workers)} worker(s) to the available pool."
            )
            if confirm:
                self.state.reset_process(process_name)
                messagebox.showinfo("Reset Complete", f"{process_name} has been reset")
                self.app.show_screen('main_menu')
    
    def reset_all_allocations(self):
        """Reset all allocations"""
        if not self.state.allocations:
            messagebox.showinfo("No Allocations", "No allocations to reset")
            return
        
        confirm = messagebox.askyesno(
            "Confirm Reset",
            "Are you sure you want to reset all allocations?\nAll workers will return to the available pool."
        )
        if confirm:
            self.state.reset_all_allocations()
            messagebox.showinfo("Reset Complete", "All allocations have been reset")
            self.app.show_screen('main_menu')