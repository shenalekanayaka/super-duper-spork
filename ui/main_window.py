"""
Main window and navigation controller
"""
import tkinter as tk
from models.state import ApplicationState
from ui.screens.start_screen import StartScreen
from ui.screens.absentee_screen import AbsenteeScreen
from ui.screens.actions_screen import ActionsScreen
from ui.screens.main_menu import MainMenuScreen
from ui.screens.process_allocation import ProcessAllocationScreen
from ui.screens.compression_allocation import CompressionAllocationScreen
from ui.screens.results_screen import ResultsScreen
from ui.screens.date_shift_screen import DateShiftScreen
from ui.screens.history_viewer_screen import HistoryViewerScreen
from ui.screens.audit_log_screen import AuditLogScreen

class WorkerAllocationSystem:
    """Main application controller"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Worker Allocation System")
        
        # Make window full screen
        self.root.state('zoomed')  # For Windows
        try:
            self.root.attributes('-zoomed', True)  # For Linux
        except:
            pass
        
        self.root.configure(bg="#f0f0f0")
        
        # Application state
        self.state = ApplicationState()
        
        # Main frame
        self.main_frame = tk.Frame(root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initialize screens
        self.screens = {
            'date_shift': DateShiftScreen(self),
            'start': StartScreen(self),
            'absentee': AbsenteeScreen(self),
            'actions': ActionsScreen(self),
            'main_menu': MainMenuScreen(self),
            'process_allocation': ProcessAllocationScreen(self),
            'compression_allocation': CompressionAllocationScreen(self),
            'results': ResultsScreen(self),
            'history_viewer': HistoryViewerScreen(self),
            'audit_log' : AuditLogScreen(self)
        }

        
        
        # Start screen
        self.show_screen('date_shift')
    
    def clear_frame(self):
        """Destroy all widgets in main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_screen(self, screen_name, **kwargs):
        """Display a specific screen"""
        self.clear_frame()
        if screen_name in self.screens:
            self.screens[screen_name].show(**kwargs)
    
    def restart(self):
        """Restart the application"""
        self.state.reset()
        self.show_screen('start')