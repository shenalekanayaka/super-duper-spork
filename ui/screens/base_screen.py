"""
Base screen class with common functionality
"""
import tkinter as tk
from utils.helpers import bind_mousewheel


class BaseScreen:
    """Base class for all screens"""
    
    def __init__(self, app):
        self.app = app
        self.state = app.state
        self.main_frame = app.main_frame
        self.root = app.root
    
    def show(self, **kwargs):
        """Display the screen - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement show()")
    
    def create_title(self, text, font_size=24):
        """Create a title label"""
        return tk.Label(
            self.main_frame,
            text=text,
            font=("Arial", font_size, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
    
    def create_subtitle(self, text, font_size=14):
        """Create a subtitle label"""
        return tk.Label(
            self.main_frame,
            text=text,
            font=("Arial", font_size),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
    
    def create_button(self, parent, text, command, bg="#3498db", width=20, height=2):
        """Create a standard button"""
        return tk.Button(
            parent,
            text=text,
            font=("Arial", 12, "bold"),
            bg=bg,
            fg="white",
            width=width,
            height=height,
            command=command
        )
    
    def create_scrollable_frame(self, parent):
        """Create a canvas with scrollbar for scrollable content"""
        canvas = tk.Canvas(parent, bg="#f0f0f0", highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        bind_mousewheel(canvas)
        
        return canvas, scrollbar, scrollable_frame
    
    def create_nav_buttons(self, back_command=None, next_command=None, 
                          back_text="← Back", next_text="Next →"):
        """Create navigation buttons at the bottom"""
        button_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        button_frame.pack(side=tk.BOTTOM, pady=20, fill=tk.X, padx=20)
        
        if back_command:
            back_btn = self.create_button(
                button_frame,
                back_text,
                back_command,
                bg="#95a5a6"
            )
            back_btn.pack(side=tk.LEFT, padx=10)
        
        if next_command:
            next_btn = self.create_button(
                button_frame,
                next_text,
                next_command,
                bg="#27ae60"
            )
            next_btn.pack(side=tk.RIGHT, padx=10)
        
        return button_frame