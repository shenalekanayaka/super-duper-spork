"""
Compression allocation screen with combined skill sorting
"""
import tkinter as tk
from tkinter import messagebox
from ui.screens.base_screen import BaseScreen
from data import get_combined_skill, get_worker_skill, get_product_skill


class CompressionAllocationScreen(BaseScreen):
    """Screen for allocating workers to compression machines"""
    
    def show(self, machine_name=None, slots=None, **kwargs):
        if not machine_name or not slots:
            return
        
        self.state.current_machine = (machine_name, slots)
        self.state.compression_vars = {}
        self.state.confirmed_workers = []
        self.state.compression_widgets = {}
        
        # Get selected product
        product = self.state.get_product_for_allocation(machine_name)
        
        title_text = f"Allocate Workers - {machine_name}"
        if product:
            title_text += f"\nProduct: {product}"
        
        title = self.create_title(title_text, 20)
        title.pack(pady=20)
        
        info_text = f"Assign {slots} worker(s) - Confirm each slot individually"
        if product:
            info_text += "\n(sorted by combined product + machine skills)"
        else:
            info_text += "\n(sorted by machine skills only)"
        
        info = self.create_subtitle(info_text, 12)
        info.pack(pady=5)
        
        # Create dropdown rows
        dropdown_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        dropdown_frame.pack(pady=20, expand=True)
        
        for i in range(slots):
            row_frame = tk.Frame(dropdown_frame, bg="#ffffff", relief=tk.RAISED, bd=2)
            row_frame.pack(pady=15, padx=20, fill=tk.X)
            
            label = tk.Label(
                row_frame,
                text=f"Slot {i+1}:",
                font=("Arial", 13, "bold"),
                bg="#ffffff",
                width=12
            )
            label.pack(side=tk.LEFT, padx=15, pady=15)
            
            var = tk.StringVar(value="-- Select Worker --")
            self.state.compression_vars[i] = var
            
            dropdown = tk.OptionMenu(row_frame, var, "")
            dropdown.config(font=("Arial", 11), bg="#ecf0f1", width=35)
            dropdown.pack(side=tk.LEFT, padx=15, pady=15)
            
            confirm_btn = tk.Button(
                row_frame,
                text="Confirm",
                font=("Arial", 12, "bold"),
                bg="#27ae60",
                fg="white",
                width=12,
                command=lambda idx=i: self.confirm_slot(idx)
            )
            confirm_btn.pack(side=tk.LEFT, padx=15, pady=15)
            
            self.state.compression_widgets[i] = {
                'dropdown': dropdown,
                'confirm_btn': confirm_btn,
                'var': var
            }
        
        self.refresh_dropdowns()
        
        # Bottom button
        button_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        button_frame.pack(side=tk.BOTTOM, pady=20, fill=tk.X, padx=20)
        
        back_btn = self.create_button(
            button_frame,
            "← Back to Menu",
            lambda: self.app.show_screen('main_menu'),
            bg="#95a5a6"
        )
        back_btn.pack(side=tk.LEFT, padx=10)
    
    def refresh_dropdowns(self):
        """Update dropdown options with workers sorted by combined skills"""
        machine_name = self.state.current_machine[0]
        product = self.state.get_product_for_allocation(machine_name)
        
        available = [w for w in self.state.available_workers 
                    if w not in self.state.confirmed_workers]
        
        # Sort by combined skill
        worker_skills = []
        for worker in available:
            combined = get_combined_skill(worker, machine_name, 'machine', product)
            worker_skills.append((worker, combined))
        
        # Sort by combined skill descending
        worker_skills.sort(key=lambda x: x[1], reverse=True)
        
        for i, widgets in self.state.compression_widgets.items():
            if i not in self.state.confirmed_workers:
                dropdown = widgets['dropdown']
                var = widgets['var']
                
                menu = dropdown['menu']
                menu.delete(0, 'end')
                
                if worker_skills:
                    for worker, skill in worker_skills:
                        display_name = self.state.get_worker_display_name(worker)
                        
                        # Show skill breakdown if product is selected
                        if product:
                            task_skill = get_worker_skill(worker, machine_name, 'machine')
                            prod_skill = get_product_skill(worker, product)
                            display_text = f"{display_name} | Total: {skill} (M:{task_skill} + Pr:{prod_skill})"
                        else:
                            display_text = f"{display_name} | Skill: {skill}"
                        
                        menu.add_command(
                            label=display_text,
                            command=lambda w=worker, v=var, d=display_text: v.set(d)
                        )
                else:
                    menu.add_command(label="No workers available")
    
    def confirm_slot(self, slot_idx):
        """Confirm a single slot allocation"""
        var = self.state.compression_vars[slot_idx]
        worker_text = var.get()
        
        if worker_text == "-- Select Worker --" or worker_text == "No workers available":
            messagebox.showwarning("No Selection", "Please select a worker first")
            return
        
        # Extract worker name (before the skill info)
        worker = worker_text.split(" |")[0].split(" (")[0]
        
        self.state.confirmed_workers.append(worker)
        self.state.available_workers.remove(worker)
        
        widgets = self.state.compression_widgets[slot_idx]
        widgets['dropdown'].config(state='disabled')
        widgets['confirm_btn'].config(state='disabled', bg="#95a5a6")
        
        machine_name = self.state.current_machine[0]
        if machine_name not in self.state.allocations:
            self.state.allocations[machine_name] = []
        self.state.allocations[machine_name].append(worker)
        
        self.refresh_dropdowns()