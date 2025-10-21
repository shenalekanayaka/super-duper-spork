"""
Absentee marking screen
"""
import tkinter as tk
from ui.screens.base_screen import BaseScreen


class AbsenteeScreen(BaseScreen):
    """Screen for marking absent workers"""
    
    def show(self, **kwargs):
        self.state.absentee_vars = {}
        
        title = self.create_title(f"Mark Absentees - {self.state.shift_group}")
        title.pack(pady=20)
        
        instruction = self.create_subtitle("Uncheck workers who are absent today")
        instruction.pack(pady=10)
        
        # Scrollable frame for checkboxes
        canvas, scrollbar, scrollable_frame = self.create_scrollable_frame(self.main_frame)
        
        # Create 4 columns
        workers_list = self.state.GROUPS[self.state.shift_group]
        workers_per_col = (len(workers_list) + 7) // 8
        
        columns_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
        columns_frame.pack(padx=20, pady=20)
        
        for col in range(8):
            col_frame = tk.Frame(columns_frame, bg="#f0f0f0")
            col_frame.grid(row=0, column=col, padx=15, pady=10, sticky="n")
            
            start_idx = col * workers_per_col
            end_idx = min(start_idx + workers_per_col, len(workers_list))
            
            for worker in workers_list[start_idx:end_idx]:
                var = tk.BooleanVar(value=True)
                self.state.absentee_vars[worker] = var
                cb = tk.Checkbutton(
                    col_frame,
                    text=worker,
                    variable=var,
                    font=("Arial", 13),
                    bg="#f0f0f0",
                    anchor="w",
                    selectcolor="#ecf0f1"
                )
                cb.pack(fill=tk.X, padx=5, pady=8)
        
        canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Navigation buttons
        self.create_nav_buttons(
            back_command=lambda: self.app.show_screen('start'),
            next_command=self.confirm_absentees
        )
    
    def confirm_absentees(self):
        """Confirm absentee selections and move to next screen"""
        self.state.confirm_absentees()
        self.app.show_screen('actions')