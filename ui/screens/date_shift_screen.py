"""
Date and Shift Time selection screen
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from ui.screens.base_screen import BaseScreen


class DateShiftScreen(BaseScreen):
    """Screen for selecting date and shift time"""
    
    def show(self, **kwargs):
        # Main container
        main_container = tk.Frame(self.main_frame, bg="#f0f0f0")
        main_container.pack(fill=tk.BOTH, expand=True, padx=50, pady=30)
        
        # Title at top
        title = tk.Label(
            main_container,
            text="State Phamaceuticals Manufacturing Corporation",
            font=("Arial", 32, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title.pack(pady=(20, 10))
        
        subtitle = tk.Label(
            main_container,
            text="Select Date and Shift Time For Worker Allocation",
            font=("Arial", 18),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        subtitle.pack(pady=(0, 30))
        
        # Two column container
        columns_frame = tk.Frame(main_container, bg="#f0f0f0")
        columns_frame.pack(fill=tk.BOTH, expand=True)
        
        # LEFT COLUMN - Calendar
        left_frame = tk.Frame(columns_frame, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        calendar_label = tk.Label(
            left_frame,
            text="Select Date",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        calendar_label.pack(pady=20)
        
        # Import calendar widget
        from tkcalendar import Calendar
        
        # Create calendar
        self.calendar = Calendar(
            left_frame,
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            font=("Arial", 18),
            background='#3498db',
            foreground='white',
            headersbackground='#2c3e50',
            headersforeground='white',
            selectbackground='#e74c3c',
            selectforeground='white',
            normalbackground='#ecf0f1',
            normalforeground='black',
            weekendbackground='#bdc3c7',
            weekendforeground='black',
            othermonthbackground='#f0f0f0',
            othermonthforeground='#95a5a6',
            bordercolor='#34495e',
            showweeknumbers=False,
            mindate=None,
            maxdate=None,
            # Optionally adjust year span for larger display:
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day
        )

        self.calendar.pack(pady=30, padx=30, ipadx=35, ipady=35)
        
        # RIGHT COLUMN - Shift Selection
        right_frame = tk.Frame(columns_frame, bg="#f0f0f0")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0))
        
        shift_label = tk.Label(
            right_frame,
            text="Select Shift Time",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        shift_label.pack(pady=20)
        
        # Shift buttons container
        shift_buttons_frame = tk.Frame(right_frame, bg="#f0f0f0")
        shift_buttons_frame.pack(pady=40, expand=True)
        
        self.shift_var = tk.StringVar(value="")
        
        # Morning shift button
        morning_btn = tk.Radiobutton(
            shift_buttons_frame,
            text="Morning Shift\n(6:00 AM - 2:00 PM)",
            variable=self.shift_var,
            value="Morning",
            font=("Arial", 16, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            selectcolor="#2980b9",
            indicatoron=0,
            width=25,
            height=4,
            relief=tk.RAISED,
            bd=4,
            cursor="hand2"
        )
        morning_btn.pack(pady=15)
        
        # Evening shift button
        evening_btn = tk.Radiobutton(
            shift_buttons_frame,
            text="Evening Shift\n(2:00 PM - 10:00 PM)",
            variable=self.shift_var,
            value="Evening",
            font=("Arial", 16, "bold"),
            bg="#e67e22",
            fg="white",
            activebackground="#d35400",
            activeforeground="white",
            selectcolor="#d35400",
            indicatoron=0,
            width=25,
            height=4,
            relief=tk.RAISED,
            bd=4,
            cursor="hand2"
        )
        evening_btn.pack(pady=15)
        
        # Continue button at bottom
        continue_btn = tk.Button(
            main_container,
            text="Continue →",
            font=("Arial", 14, "bold"),
            bg="#27ae60",
            fg="white",
            width=30,
            height=2,
            command=self.validate_and_continue,
            cursor="hand2"
        )
        continue_btn.pack(pady=30)

    def validate_and_continue(self):
        """Validate selections and proceed"""
        from tkinter import messagebox
        from datetime import datetime
        
        # Validate shift selection
        if not self.shift_var.get():
            messagebox.showwarning("No Selection", "Please select a shift time")
            return
        
        # Get selected date from calendar
        selected_date_raw = self.calendar.get_date()

        
        # Parse the date to ensure correct format
        try:
            # tkcalendar might return date in different formats depending on system
            # Try parsing with the date_pattern we specified
            date_obj = datetime.strptime(selected_date_raw, "%Y-%m-%d")
            selected_date = date_obj.strftime("%Y-%m-%d")
        except:
            # If that fails, try getting the date object directly
            try:
                date_obj = self.calendar.selection_get()
                selected_date = date_obj.strftime("%Y-%m-%d")
            except:
                messagebox.showerror("Date Error", "Could not read selected date")
                return
        
        shift_time = self.shift_var.get()
        
        # Store in state
        self.state.selected_date = selected_date
        self.state.shift_time = shift_time
        
        # Check if JSON file exists for this date and shift
        exists, json_filepath = self.state.check_allocation_exists(selected_date, shift_time)
        
        if exists:
            # Ask user if they want to view history
            result = messagebox.askyesno(
                "Allocation Already Exists",
                f"Found existing allocation:\n\n"
                f"📅 Date: {selected_date}\n"
                f"🕐 Shift: {shift_time}\n\n"
                f"Do you want to view this allocation?"
            )
            
            if result:  # Yes - View history
                self.app.show_screen('history_viewer', filepath=json_filepath)
                return
            else:  # No - Go back to date selection
                return
        
        # Proceed to group selection (new allocation)
        self.app.show_screen('start')
    
    def load_allocation(self, filepath):
        """Load allocation from JSON file and show results"""
        from tkinter import messagebox
        
        success = self.state.load_allocation_from_json(filepath)
        
        if success:
            messagebox.showinfo(
                "Allocation Loaded",
                f"Successfully loaded allocation for:\n"
                f"Date: {self.state.selected_date}\n"
                f"Shift: {self.state.shift_time}\n"
                f"Group: {self.state.shift_group}"
            )
            # Go directly to results screen
            self.app.show_screen('results')
        else:
            messagebox.showerror(
                "Load Failed",
                "Failed to load allocation data.\n"
                "The JSON file may be corrupted."
            )