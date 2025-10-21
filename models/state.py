"""
Application state management
"""
from data import GROUPS, PROCESSES, COMPRESSION_MACHINES, PRODUCTS
from audit_trail import audit_trail

class ApplicationState:
    """Manages application state"""
    
    def __init__(self):
        self.GROUPS = GROUPS
        self.PROCESSES = PROCESSES
        self.compression_machines = COMPRESSION_MACHINES
        self.PRODUCTS = PRODUCTS  # New: Available products

        # NEW: Date and shift time
        self.selected_date = None
        self.shift_time = None
        
        # State variables
        self.shift_group = None
        self.available_workers = []
        self.absentee_vars = {}
        self.overtime_workers = []
        self.temp_workers = []
        self.allocations = {}
        
        # Product selection per allocation
        self.allocation_products = {}  # Maps task_name -> product_name
        self.lot_numbers = {}  # Store lot numbers for each allocation
        
        # Process allocation state
        self.current_process = None
        self.process_listboxes = []
        
        # Compression allocation state
        self.current_machine = None
        self.compression_vars = {}
        self.confirmed_workers = []
        self.compression_widgets = {}

        self.audit_trail = audit_trail
    
    def select_group(self, group):
        """Select shift group"""
        self.shift_group = group
        self.available_workers = self.GROUPS[group].copy()
    
    def confirm_absentees(self):
        """Remove absent workers from available pool"""
        absent = [w for w, var in self.absentee_vars.items() if not var.get()]
        self.available_workers = [w for w in self.available_workers if w not in absent]
    
    def add_shift_swap(self, removed, added):
        """Handle shift swap"""
        for worker in removed:
            if worker in self.available_workers:
                self.available_workers.remove(worker)
        
        self.available_workers.extend(added)
    
    def add_overtime(self, workers):
        """Add overtime workers"""
        for worker in workers:
            if worker not in self.overtime_workers:
                self.overtime_workers.append(worker)
                if worker not in self.available_workers:
                    self.available_workers.append(worker)
    
    def add_temp(self, workers):
        """Add temporary workers"""
        for worker in workers:
            if worker not in self.temp_workers:
                self.temp_workers.append(worker)
                if worker not in self.available_workers:
                    self.available_workers.append(worker)
    
    def allocate_workers(self, task_name, workers):
        """Allocate workers to a task"""
        self.allocations[task_name] = workers
        for worker in workers:
            if worker in self.available_workers:
                self.available_workers.remove(worker)
    
    def set_product_for_allocation(self, task_name, product_name):
        """Set the selected product for a task allocation"""
        if product_name and product_name != "-- Select Product --":
            self.allocation_products[task_name] = product_name
    
    def get_product_for_allocation(self, task_name):
        """Get the selected product for a task allocation"""
        return self.allocation_products.get(task_name, None)
    
    def set_lot_number_for_allocation(self, allocation_name, lot_number):
        """Set lot number for an allocation"""
        if lot_number and lot_number.strip():
            self.lot_numbers[allocation_name] = lot_number.strip()
        elif allocation_name in self.lot_numbers:
            del self.lot_numbers[allocation_name]

    def get_lot_number_for_allocation(self, allocation_name):
        """Get lot number for an allocation"""
        return self.lot_numbers.get(allocation_name, None)
    
    def reset_process(self, process_name):
        """Reset a specific process allocation"""
        if process_name in self.allocations:
            workers = self.allocations[process_name]
            self.available_workers.extend(workers)
            del self.allocations[process_name]
            
            # Also remove product selection
            if process_name in self.allocation_products:
                del self.allocation_products[process_name]
            # Clear lot number
            if process_name in self.lot_numbers:
                del self.lot_numbers[process_name]
            
    
    def reset_all_allocations(self):
        """Reset all allocations"""
        for workers in self.allocations.values():
            self.available_workers.extend(workers)
        
        self.allocations = {}
        self.allocation_products = {}
        self.lot_numbers = {}
    
    def get_worker_display_name(self, worker):
        """Get display name with markers for overtime/temp workers"""
        if worker in self.overtime_workers:
            return f"{worker} (OT)"
        elif worker in self.temp_workers:
            return f"{worker} (Temp)"
        return worker
    
    def reset(self):
        """Reset entire state"""
        self.selected_date = None
        self.shift_time = None
        self.shift_group = None
        self.available_workers = []
        self.absentee_vars = {}
        self.overtime_workers = []
        self.temp_workers = []
        self.allocations = {}
        self.allocation_products = {}
        self.current_process = None
        self.process_listboxes = []
        self.current_machine = None
        self.compression_vars = {}
        self.confirmed_workers = []
        self.compression_widgets = {}


    def load_allocation_from_json(self, filepath):
        """Load allocation data from JSON file"""
        print(f"\nDEBUG: load_allocation_from_json called with: {filepath}")
        import json
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load metadata
            metadata = data.get('metadata', {})
            self.selected_date = metadata.get('date')
            self.shift_time = metadata.get('shift_time')
            self.shift_group = metadata.get('shift_group')
            
            # Clear current state
            self.allocations = {}
            self.allocation_products = {}
            self.allocation_lot_numbers = {}
            self.overtime_workers = []
            self.temp_workers = []
            self.available_workers = []
            
            # Load processes
            for process in data.get('processes', []):
                process_name = process['name']
                workers = [w['name'] for w in process['workers']]
                
                self.allocations[process_name] = workers
                
                if process['product'] != "N/A":
                    self.allocation_products[process_name] = process['product']
                
                if process['lot_number'] != "N/A":
                    self.allocation_lot_numbers[process_name] = process['lot_number']
                
                # Track overtime and temp workers
                for worker_data in process['workers']:
                    if worker_data['is_overtime'] and worker_data['name'] not in self.overtime_workers:
                        self.overtime_workers.append(worker_data['name'])
                    if worker_data['is_temp'] and worker_data['name'] not in self.temp_workers:
                        self.temp_workers.append(worker_data['name'])
            
            # Load machines
            for machine in data.get('machines', []):
                machine_name = machine['name']
                workers = [w['name'] for w in machine['workers']]
                
                self.allocations[machine_name] = workers
                
                if machine['product'] != "N/A":
                    self.allocation_products[machine_name] = machine['product']
                
                if machine['lot_number'] != "N/A":
                    self.allocation_lot_numbers[machine_name] = machine['lot_number']
                
                # Track overtime and temp workers
                for worker_data in machine['workers']:
                    if worker_data['is_overtime'] and worker_data['name'] not in self.overtime_workers:
                        self.overtime_workers.append(worker_data['name'])
                    if worker_data['is_temp'] and worker_data['name'] not in self.temp_workers:
                        self.temp_workers.append(worker_data['name'])
            
            # Load unassigned workers
            for worker_data in data.get('unassigned_workers', []):
                self.available_workers.append(worker_data['name'])
                
                if worker_data['is_overtime'] and worker_data['name'] not in self.overtime_workers:
                    self.overtime_workers.append(worker_data['name'])
                if worker_data['is_temp'] and worker_data['name'] not in self.temp_workers:
                    self.temp_workers.append(worker_data['name'])
            

            # Create all_shift_workers for editing
            self.all_shift_workers = set()

            # Add all currently assigned workers
            for allocation_name, workers in self.allocations.items():
                self.all_shift_workers.update(workers)

            # Add all unassigned workers
            self.all_shift_workers.update(self.available_workers)

            print(f"DEBUG: Created all_shift_workers with {len(self.all_shift_workers)} workers")   
    
            # Mark as loaded allocation
            self._is_loaded_allocation = True
            
            print(f"DEBUG: Finished loading. Allocations: {self.allocations}")
            print(f"DEBUG: Available workers: {len(self.available_workers)}")
            
            return True
            
        except Exception as e:
            print(f"Error loading JSON allocation: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # ============ DEBUG: Reconstruct all_shift_workers ============


    def check_allocation_exists(self, date, shift_time):
        """Check if JSON allocation file exists for given date and shift"""
        import os
        import sys
        
        # Use data_path helper
        def data_path(relative_path):
            """Get path for writable data files"""
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(base_path, relative_path)
        
        filename = f"Allocation_{date}_{shift_time}.json"
        filepath = data_path(os.path.join("allocations_json", filename))
        
        return os.path.exists(filepath), filepath
    
