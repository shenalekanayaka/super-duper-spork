"""
Allocation card component with product selection
"""
import tkinter as tk
from ui.components.searchable_dropdown import SearchableDropdown


class AllocationCard:
    """Card component showing process/machine with workers and product"""
    
    def __init__(self, parent, name, slots, state, is_compression=False, 
                 on_allocate=None, on_reset=None):
        self.parent = parent
        self.name = name
        self.slots = slots
        self.state = state
        self.is_compression = is_compression
        self.on_allocate = on_allocate
        self.on_reset = on_reset

        
    
    def render(self, row=0, col=0):
        """Render the card in grid layout"""
        card_frame = tk.Frame(self.parent, bg="#ffffff", relief=tk.RAISED, bd=2)
        card_frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        
        # Configure grid weights for equal sizing
        self.parent.grid_columnconfigure(col, weight=1, minsize=220)
        
        # Check if workers are already allocated
        has_allocation = bool(self.state.allocations.get(self.name, []))
        
        # Title/Button
        btn_color = "#9b59b6" if self.is_compression else "#3498db"
        
        

        # Adjust font size based on name length
        if len(self.name) > 30:
            btn_font = ("Arial", 8, "bold")
        elif len(self.name) > 20:
            btn_font = ("Arial", 9, "bold")
        else:
            btn_font = ("Arial", 10, "bold")

        btn = tk.Button(
            card_frame,
            text=self.name,
            font=btn_font,
            bg=btn_color if not has_allocation else "#95a5a6",  # Gray if allocated
            fg="white",
            command=lambda: self._handle_allocate(),
            wraplength=180,
            state='normal' if not has_allocation else 'disabled'  # Disable if allocated
        )
        btn.pack(pady=5, padx=5, fill=tk.X, ipady=10)
        
        # Product dropdown (only if not compression machine)
# Product dropdown for all tasks
        if self.state.PRODUCTS:
            self._render_product_dropdown(card_frame)

        # Lot number entry
        self._render_lot_number_entry(card_frame)
        
        # Workers display
        if self.name in self.state.allocations and self.state.allocations[self.name]:
            self._render_allocated_workers(card_frame)
        else:
            self._render_empty_state(card_frame)
    
    def _render_product_dropdown(self, card_frame):
        
        if not self.state.PRODUCTS:
            return
        
        
        product_frame = tk.Frame(card_frame, bg="#ffffff")
        product_frame.pack(pady=5, padx=5, fill=tk.X)
        
        product_label = tk.Label(
            product_frame,
            text="Product:",
            font=("Arial", 9, "bold"),
            bg="#ffffff"
        )
        product_label.pack(anchor="w", padx=5)
        
        # Get current product selection
        current_product = self.state.get_product_for_allocation(self.name)
        
        try:
            # Create searchable dropdown
            dropdown = SearchableDropdown(
                product_frame,
                values=sorted(self.state.PRODUCTS),
                on_select=lambda p: self.state.set_product_for_allocation(self.name, p),
                width=18
            )
            
            # Set current value if exists
            if current_product:
                dropdown.set(current_product)
            
            dropdown.pack(pady=2, padx=5)
        except Exception as e:
            import traceback
            traceback.print_exc()

    def _render_lot_number_entry(self, card_frame):
        """Render lot number entry field"""
        lot_frame = tk.Frame(card_frame, bg="#ffffff")
        lot_frame.pack(pady=5, padx=5, fill=tk.X)
        
        lot_label = tk.Label(
            lot_frame,
            text="Lot Number:",
            font=("Arial", 9, "bold"),
            bg="#ffffff"
        )
        lot_label.pack(anchor="w", padx=5)
        
        # Get current lot number
        current_lot = self.state.get_lot_number_for_allocation(self.name)
        
        lot_var = tk.StringVar(value=current_lot if current_lot else "")
        
        lot_entry = tk.Entry(
            lot_frame,
            textvariable=lot_var,
            font=("Arial", 10),
            width=20
        )
        lot_entry.pack(pady=2, padx=5)
        
        # Save lot number when user types
        def save_lot_number(*args):
            self.state.set_lot_number_for_allocation(self.name, lot_var.get())
        
        lot_var.trace('w', save_lot_number)

    def _handle_allocate(self):
        """Handle allocate button click"""
        # Show product if selected
        product = self.state.get_product_for_allocation(self.name)
        if True:  # Show for all tasks
            if not product:
                from tkinter import messagebox
                result = messagebox.askyesno(
                    "No Product Selected",
                    f"No product selected for {self.name}.\n\nDo you want to continue without product selection?\n\n(Worker sorting will only use process/machine skills)"
                )
                if not result:
                    return
        
        if self.on_allocate:
            self.on_allocate()
    
    def _render_allocated_workers(self, card_frame):
        """Render allocated workers"""
        workers = self.state.allocations[self.name]
        
        status_label = tk.Label(
            card_frame,
            text=f"({len(workers)}/{self.slots}) Workers:",
            font=("Arial", 9, "bold"),
            bg="#ffffff",
            fg="#27ae60"
        )
        status_label.pack(pady=2)
        
        # Show product if selected
        product = self.state.get_product_for_allocation(self.name)
        if product:
            display_product = product[:25] + "..." if len(product) > 25 else product
            prod_label = tk.Label(
                card_frame,
                text=f"Product: {display_product}",
                font=("Arial", 8, "italic"),
                bg="#ffffff",
                fg="#3498db"
            )
            prod_label.pack()

        # Show lot number if entered
        lot_number = self.state.get_lot_number_for_allocation(self.name)
        if lot_number:
            lot_label = tk.Label(
                card_frame,
                text=f"Lot: {lot_number}",
                font=("Arial", 8, "italic"),
                bg="#ffffff",
                fg="#e67e22"
            )
            lot_label.pack()
        
        for worker in workers:
            display_name = self.state.get_worker_display_name(worker)
            
            worker_label = tk.Label(
                card_frame,
                text=f"- {display_name}",
                font=("Arial", 8),
                bg="#ffffff"
            )
            worker_label.pack()
        
        reset_btn = tk.Button(
            card_frame,
            text="Reset",
            font=("Arial", 9, "bold"),
            bg="#e74c3c",
            fg="white",
            width=12,
            command=lambda: self.on_reset(self.name)
        )
        reset_btn.pack(pady=5)
    
    def _render_empty_state(self, card_frame):
        """Render empty state"""
        empty_label = tk.Label(
            card_frame,
            text=f"(0/{self.slots}) No workers",
            font=("Arial", 9, "italic"),
            bg="#ffffff",
            fg="#95a5a6"
        )
        empty_label.pack(pady=5)