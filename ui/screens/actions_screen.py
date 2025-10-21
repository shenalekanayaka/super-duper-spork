"""
Additional actions screen
"""
import tkinter as tk
from ui.screens.base_screen import BaseScreen
from ui.dialogs.shift_swap_dialog import ShiftSwapDialog
from ui.dialogs.overtime_dialog import OvertimeDialog
from ui.dialogs.temp_workers_dialog import TempWorkersDialog


class ActionsScreen(BaseScreen):
    """Screen for additional actions like shift swaps, overtime, temp workers"""
    
    def show(self, **kwargs):
        title = self.create_title("Additional Actions", 26)
        title.pack(pady=40)
        
        subtitle = self.create_subtitle("Add Shift Swaps, Overtime, or Temporary Workers")
        subtitle.pack(pady=10)
        
        # Center button container
        button_container = tk.Frame(self.main_frame, bg="#f0f0f0")
        button_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Shift swap button
        shift_swap_btn = tk.Button(
            button_container,
            text="Shift Swap",
            font=("Arial", 14, "bold"),
            bg="#e67e22",
            fg="white",
            width=30,
            height=3,
            command=self.shift_swap
        )
        shift_swap_btn.pack(pady=15)
        
        # Add overtime workers button
        overtime_btn = tk.Button(
            button_container,
            text="Add Overtime Workers",
            font=("Arial", 14, "bold"),
            bg="#f39c12",
            fg="white",
            width=30,
            height=3,
            command=self.add_overtime_workers
        )
        overtime_btn.pack(pady=15)
        
        # Add temporary workers button
        temp_btn = tk.Button(
            button_container,
            text="Add Temp Workers",
            font=("Arial", 14, "bold"),
            bg="#16a085",
            fg="white",
            width=30,
            height=3,
            command=self.add_temp_workers
        )
        temp_btn.pack(pady=15)
        
        # Navigation buttons
        nav_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        nav_frame.pack(side=tk.BOTTOM, pady=30, fill=tk.X, padx=20)
        
        back_btn = self.create_button(
            nav_frame,
            "← Back",
            lambda: self.app.show_screen('absentee'),
            bg="#95a5a6"
        )
        back_btn.pack(side=tk.LEFT, padx=10)
        
        next_btn = self.create_button(
            nav_frame,
            "Next →",
            lambda: self.app.show_screen('main_menu'),
            bg="#27ae60"
        )
        next_btn.pack(side=tk.RIGHT, padx=10)
    
    def shift_swap(self):
        """Open shift swap dialog"""
        dialog = ShiftSwapDialog(self.root, self.state)
        dialog.show()
    
    def add_overtime_workers(self):
        """Open overtime workers dialog"""
        dialog = OvertimeDialog(self.root, self.state)
        dialog.show()
    
    def add_temp_workers(self):
        """Open temp workers dialog"""
        dialog = TempWorkersDialog(self.root, self.state)
        dialog.show()