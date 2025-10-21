"""
Process allocation screen with combined skill sorting
"""
import tkinter as tk
from tkinter import messagebox
from ui.screens.base_screen import BaseScreen
from utils.helpers import sort_workers
from data import get_combined_skill


class ProcessAllocationScreen(BaseScreen):
    """Screen for allocating workers to processes"""
    
    def show(self, process_name=None, slots=None, **kwargs):
        if not process_name or not slots:
            return
        
        self.state.current_process = (process_name, slots)
        self.state.process_listboxes = []
        
        # Get selected product
        product = self.state.get_product_for_allocation(process_name)
        
        title_text = f"Allocate Workers - {process_name}"
        if product:
            title_text += f"\nProduct: {product}"
        
        title = self.create_title(title_text, 20)
        title.pack(pady=20)
        
        info_text = f"Select {slots} worker(s)"
        if product:
            info_text += " (sorted by combined product + process skills)"
        else:
            info_text += " (sorted by process skills only)"
        
        info = self.create_subtitle(info_text, 12)
        info.pack(pady=5)
        
        # Create listboxes for each slot
        listbox_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        listbox_frame.pack(pady=20, expand=True)
        
        for i in range(slots):
            slot_frame = tk.Frame(listbox_frame, bg="#f0f0f0")
            slot_frame.pack(side=tk.LEFT, padx=15)
            
            label = tk.Label(
                slot_frame,
                text=f"Slot {i+1}",
                font=("Arial", 14, "bold"),
                bg="#f0f0f0"
            )
            label.pack(pady=10)
            
            listbox = tk.Listbox(
                slot_frame,
                height=15,
                width=30,
                font=("Arial", 10),
                exportselection=False
            )
            listbox.pack()
            
            # Add scrollbar
            scrollbar = tk.Scrollbar(slot_frame, command=listbox.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            listbox.config(yscrollcommand=scrollbar.set)
            
            listbox.bind('<<ListboxSelect>>', lambda e, idx=i: self.update_listboxes(idx))
            
            self.state.process_listboxes.append(listbox)
        
        self.update_listboxes(-1)
        
        # Bottom buttons
        self.create_nav_buttons(
            back_command=lambda: self.app.show_screen('main_menu'),
            next_command=self.confirm_allocation,
            back_text="← Back to Menu",
            next_text="✓ Confirm Allocation"
        )
    
    def update_listboxes(self, changed_idx):
        """Update all listboxes with workers sorted by combined skills"""
        from data import get_worker_skill, get_product_skill, should_track_frequency
        from allocation_history import allocation_history
        
        process_name = self.state.current_process[0]
        product = self.state.get_product_for_allocation(process_name)
        
        # Check if frequency tracking is enabled
        track_frequency = should_track_frequency(process_name, 'process')
        
        selected_workers = []
        
        for lb in self.state.process_listboxes:
            selection = lb.curselection()
            if selection:
                worker_text = lb.get(selection[0])
                worker_name = worker_text.split(" |")[0].split(" (")[0]
                selected_workers.append(worker_name)
        
        for i, lb in enumerate(self.state.process_listboxes):
            current_selection = None
            if lb.curselection():
                worker_text = lb.get(lb.curselection()[0])
                current_selection = worker_text.split(" |")[0].split(" (")[0]
            
            exclude = [w for j, w in enumerate(selected_workers) if j != i]
            available = [w for w in self.state.available_workers if w not in exclude]
            
            # Sort by combined skill with frequency penalty
            worker_skills = []
            for worker in available:
                combined = get_combined_skill(worker, process_name, 'process', product)
                
                # Apply frequency penalty if tracking is enabled
                if track_frequency:
                    penalty = allocation_history.calculate_frequency_penalty(process_name, worker)
                    combined -= penalty

                    # DEBUG
                    if penalty > 0:
                        print(f"  {worker}: count={allocation_history.get_allocation_count(process_name, worker)}, penalty={penalty}")


                else:
                    penalty = 0
                
                worker_skills.append((worker, combined, penalty))

            print(f"\nDEBUG: Process '{process_name}' - Track frequency: {track_frequency}")
            if track_frequency:
                print(f"DEBUG: Applied frequency penalties for {len([w for w in worker_skills if w[2] > 0])} workers")
            
            # Sort by combined skill descending
            worker_skills.sort(key=lambda x: x[1], reverse=True)
            
            lb.delete(0, tk.END)
            for worker, skill, penalty in worker_skills:
                display_name = self.state.get_worker_display_name(worker)
                
                # Show skill breakdown
                lb.delete(0, tk.END)
                for worker, skill, penalty in worker_skills:
                    display_name = self.state.get_worker_display_name(worker)
                    
                    # Show skill breakdown
                    if product:
                        task_skill = get_worker_skill(worker, process_name, 'process')
                        prod_skill = get_product_skill(worker, product)
                        
                        if track_frequency and penalty > 0:
                            display_text = f"{display_name} | ⬇️ {skill:.1f} ({task_skill}+{prod_skill}-{penalty:.1f})"
                        else:
                            display_text = f"{display_name} | {skill} ({task_skill}+{prod_skill})"
                    else:
                        if track_frequency and penalty > 0:
                            display_text = f"{display_name} | ⬇️ {skill:.1f} (was {skill + penalty:.1f},-{penalty:.1f})"
                        else:
                            display_text = f"{display_name} | Skill: {skill}"
                    
                    lb.insert(tk.END, display_text)
            
            # Restore selection if it was there
            if current_selection:
                for idx, (worker, _, _) in enumerate(worker_skills):
                    if worker == current_selection:
                        lb.selection_set(idx)
                        lb.see(idx)
                        break

    def confirm_allocation(self):
        """Confirm worker allocation"""
        from allocation_history import allocation_history
        from data import should_track_frequency
        
        selected = []
        for lb in self.state.process_listboxes:
            selection = lb.curselection()
            if selection:
                worker_text = lb.get(selection[0])
                worker_name = worker_text.split(" |")[0].split(" (")[0]
                selected.append(worker_name)
        
        if len(selected) == 0:
            messagebox.showwarning("No Selection", "Please select at least one worker")
            return
        
        process_name = self.state.current_process[0]
        self.state.allocate_workers(process_name, selected)
        
        # Record allocation history if tracking is enabled
        if should_track_frequency(process_name, 'process'):
            for worker in selected:
                allocation_history.add_allocation(process_name, worker)
        
        self.app.show_screen('main_menu')

    
