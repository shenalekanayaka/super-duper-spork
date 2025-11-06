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
    
    def create_scrollable_frame(self, parent, horizontal=False):
        """Create a canvas with scrollbar for scrollable content"""
        canvas = tk.Canvas(parent, bg="#f0f0f0", highlightthickness=0)
        v_scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        bind_mousewheel(canvas)
        
        if horizontal:
            h_scrollbar = tk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
            canvas.configure(xscrollcommand=h_scrollbar.set)
            return canvas, v_scrollbar, h_scrollbar, scrollable_frame
        
        return canvas, v_scrollbar, scrollable_frame
    
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
    
    def create_result_card(self, parent, name, workers, product=None, row=0, col=0, edit_mode=False, edit_callback=None, delete_callback=None):
        """Create a result card in grid layout"""
        card_frame = tk.Frame(parent, bg="#ecf0f1", relief=tk.RAISED, bd=2)
        card_frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        
        parent.grid_columnconfigure(col, weight=1, minsize=200)
        
        # Add edit and delete buttons in edit mode
        if edit_mode:
            btn_container = tk.Frame(card_frame, bg="#ecf0f1")
            btn_container.pack(side=tk.TOP, anchor="e", padx=5, pady=2)
            
            edit_btn = tk.Button(
                btn_container,
                text="✏️",
                font=("Arial", 10, "bold"),
                bg="#f39c12",
                fg="white",
                width=3,
                command=lambda: edit_callback(name) if edit_callback else None
            )
            edit_btn.pack(side=tk.LEFT, padx=2)
            
            delete_btn = tk.Button(
                btn_container,
                text="🗑️",
                font=("Arial", 10, "bold"),
                bg="#e74c3c",
                fg="white",
                width=3,
                command=lambda: delete_callback(name) if delete_callback else None
            )
            delete_btn.pack(side=tk.LEFT, padx=2)
        
        # Adjust font size for long names
        if len(name) > 30:
            name_font = ("Arial", 9, "bold")
        elif len(name) > 20:
            name_font = ("Arial", 10, "bold")
        else:
            name_font = ("Arial", 11, "bold")
        
        name_label = tk.Label(
            card_frame,
            text=f"{name}:",
            font=name_font,
            bg="#ecf0f1",
            wraplength=180,
            justify=tk.LEFT
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