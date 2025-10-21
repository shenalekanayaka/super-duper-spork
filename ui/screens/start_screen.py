"""
Start screen for group selection
"""
import tkinter as tk
from ui.screens.base_screen import BaseScreen


class StartScreen(BaseScreen):
    """Initial screen for selecting shift group"""
    
    def show(self, **kwargs):
        # Center container
        center_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        title = tk.Label(
            center_frame,
            text="Worker Allocation System",
            font=("Arial", 32, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title.pack(pady=40)
        
        subtitle = tk.Label(
            center_frame,
            text="Select Your Shift Group",
            font=("Arial", 18),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        subtitle.pack(pady=20)
        

        if self.state.selected_date and self.state.shift_time:
            info_label = tk.Label(
                center_frame,
                text=f"Date: {self.state.selected_date} | Shift: {self.state.shift_time}",
                font=("Arial", 12),
                bg="#f0f0f0",
                fg="#7f8c8d"
            )
            info_label.pack(pady=10)
        # ↑↑↑ END OF ADDITION

        button_frame = tk.Frame(center_frame, bg="#f0f0f0")
        button_frame.pack(pady=30)
        
        for group in self.state.GROUPS.keys():
            btn = tk.Button(
                button_frame,
                text=f"{group}\n({len(self.state.GROUPS[group])} workers)",
                font=("Arial", 16, "bold"),
                bg="#3498db",
                fg="white",
                width=25,
                height=4,
                relief=tk.RAISED,
                bd=3,
                command=lambda g=group: self.select_group(g)
            )
            btn.pack(pady=15)

        back_btn = tk.Button(
            center_frame,
            text="← Back to Date/Shift Selection",
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            width=30,
            height=2,
            command=lambda: self.app.show_screen('date_shift')
        )
        back_btn.pack(pady=20)
        # ↑↑↑ END OF ADDITION
    
    def select_group(self, group):
        """Handle group selection"""
        self.state.select_group(group)
        self.app.show_screen('absentee')