import os
import csv
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# Initialize with your workers from products.csv
GROUPS = {
    "Group A": [],
    "Group B": [],
    "General Shift": []  # New group for 8-5 workers
}

# These will be loaded from CSV
PROCESSES = []
COMPRESSION_MACHINES = []
PRODUCTS = []  # New: List of products

# Use resource_path for reading CSV files
WORKERS_CSV = resource_path(os.path.join("utils", "workers.csv"))
TASKS_CSV = resource_path(os.path.join("utils", "tasks.csv"))
PRODUCTS_CSV = resource_path(os.path.join("utils", "products.csv"))
PROCESS_GROUPS_CSV = resource_path(os.path.join("utils", "process_groups.csv"))

# Dictionary to store worker skills
WORKER_SKILLS = {}
PRODUCT_SKILLS = {}  # New: Product skills dictionary
PROCESS_GROUPS = {}  # Maps process_name -> group_name



def load_process_groups():
    """Load process groupings from CSV"""
    global PROCESS_GROUPS
    
    if not os.path.exists(PROCESS_GROUPS_CSV):
        print(f"Warning: {PROCESS_GROUPS_CSV} not found. No process grouping.")
        return
    
    with open(PROCESS_GROUPS_CSV, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            process_name = row['Process_Name']
            group_name = row['Group_Name']
            PROCESS_GROUPS[process_name] = group_name
    
    print(f"Loaded {len(PROCESS_GROUPS)} process groupings")

def get_process_group(process_name):
    """Get the group name for a process (or return process name if no group)"""
    return PROCESS_GROUPS.get(process_name, process_name)

# Load at startup
load_process_groups()

def save_workers_to_csv():
    """Save current WORKER_SKILLS data back to CSV."""
    with open(WORKERS_CSV, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        header = ["Group", "Worker"]
        for process_data in PROCESSES:
            header.append(process_data[0])  # Get name from tuple
        for machine_data in COMPRESSION_MACHINES:
            header.append(machine_data[0])  # Get name from tuple
        
        writer.writerow(header)
        
        for worker, data in WORKER_SKILLS.items():
            row = [data['group'], worker]
            
            for process_data in PROCESSES:
                process_name = process_data[0]
                row.append(data['processes'].get(process_name, 0))
            
            for machine_data in COMPRESSION_MACHINES:
                machine_name = machine_data[0]
                row.append(data['machines'].get(machine_name, 0))
            
            writer.writerow(row)

def load_or_create_tasks_csv():
    """Load processes and compression machines from tasks CSV."""
    global PROCESSES, COMPRESSION_MACHINES
    
    if not os.path.exists(TASKS_CSV):
        print(f"Error: {TASKS_CSV} not found.")
        return
    
    processes = []
    machines = []
    
    with open(TASKS_CSV, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            task_type = row["Type"]
            name = row["Name"]
            try:
                workers_needed = int(row["Workers_Needed"])
            except (ValueError, KeyError):
                workers_needed = 1
            
            # Read Track_Frequency column - accept Yes/TRUE/True/1
            track_value = row.get("Track_Frequency", "").strip().upper()
            track_freq = track_value in ["YES", "TRUE", "1", "Y"]
            
            # DEBUG - Print every task's tracking status
            if track_freq:
                print(f"✓ TRACKING ENABLED: {name} (value='{track_value}')")
            
            if task_type == "Process":
                processes.append((name, workers_needed, track_freq))
            elif task_type == "Machine":
                machines.append((name, workers_needed, track_freq))
    
    PROCESSES = processes
    COMPRESSION_MACHINES = machines
    
    print(f"\nLoaded {len(PROCESSES)} processes and {len(COMPRESSION_MACHINES)} machines from {TASKS_CSV}")



def load_or_create_workers_csv():
    global GROUPS, WORKER_SKILLS
    
    if not os.path.exists(WORKERS_CSV):
        # Create the CSV file with headers for all processes and machines
        with open(WORKERS_CSV, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            header = ["Group", "Worker"]
            for process_data in PROCESSES:
                header.append(process_data[0])  # Get name from tuple
            for machine_data in COMPRESSION_MACHINES:
                header.append(machine_data[0])  # Get name from tuple
            
            writer.writerow(header)
            
            for group, workers in GROUPS.items():
                for worker in workers:
                    row = [group, worker]
                    row.extend([0] * len(PROCESSES))
                    row.extend([0] * len(COMPRESSION_MACHINES))
                    writer.writerow(row)
        
        print(f"Created {WORKERS_CSV} with default skill ratings (0-5 scale recommended)")
    
    new_groups = {"Group A": [], "Group B": [], "General Shift": []}
    new_skills = {}
    
    with open(WORKERS_CSV, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            group = row["Group"]
            worker = row["Worker"]
            
            if group in new_groups:
                new_groups[group].append(worker)
            
            worker_data = {
                'group': group,
                'processes': {},
                'machines': {}
            }
            
            for process_data in PROCESSES:
                process_name = process_data[0]  # Get name from tuple
                if process_name in row:
                    try:
                        rating = int(row[process_name])
                        worker_data['processes'][process_name] = rating
                    except (ValueError, KeyError):
                        worker_data['processes'][process_name] = 0
            
            for machine_data in COMPRESSION_MACHINES:
                machine_name = machine_data[0]  # Get name from tuple
                if machine_name in row:
                    try:
                        rating = int(row[machine_name])
                        worker_data['machines'][machine_name] = rating
                    except (ValueError, KeyError):
                        worker_data['machines'][machine_name] = 0
            
            new_skills[worker] = worker_data
    
    GROUPS = new_groups
    WORKER_SKILLS = new_skills
    print(f"Loaded {len(WORKER_SKILLS)} workers from {WORKERS_CSV}")

def get_worker_skill(worker_name, task_name, task_type='process'):
    """Get skill rating for a worker on a specific task."""
    if worker_name not in WORKER_SKILLS:
        return 0
    
    if task_type == 'process':
        return WORKER_SKILLS[worker_name]['processes'].get(task_name, 0)
    elif task_type == 'machine':
        return WORKER_SKILLS[worker_name]['machines'].get(task_name, 0)
    else:
        return 0

def get_product_skill(worker_name, product_name):
    """Get skill rating for a worker on a specific product."""
    if product_name not in PRODUCT_SKILLS:
        return 0
    return PRODUCT_SKILLS[product_name].get(worker_name, 0)

def get_combined_skill(worker_name, task_name, task_type='process', product_name=None):
    """
    Get combined skill rating (product + task).
    
    Args:
        worker_name: Name of the worker
        task_name: Name of the process or machine
        task_type: 'process' or 'machine'
        product_name: Name of the product (optional)
    
    Returns:
        Combined skill rating (task_skill + product_skill)
    """
    task_skill = get_worker_skill(worker_name, task_name, task_type)
    
    if product_name:
        product_skill = get_product_skill(worker_name, product_name)
        return task_skill + product_skill
    
    return task_skill

def get_skilled_workers(task_name, task_type='process', product_name=None, min_rating=1, group=None):
    """
    Get list of workers skilled in a specific task and product combination.
    
    Args:
        task_name: Name of the process or machine
        task_type: 'process' or 'machine'
        product_name: Name of the product (optional)
        min_rating: Minimum combined skill rating required
        group: Optional group filter ('Group A' or 'Group B')
    
    Returns:
        List of tuples: [(worker_name, combined_skill_rating, task_skill, product_skill), ...]
    """
    skilled = []
    
    for worker, data in WORKER_SKILLS.items():
        if group and data['group'] != group:
            continue
        
        task_skill = get_worker_skill(worker, task_name, task_type)
        product_skill = get_product_skill(worker, product_name) if product_name else 0
        combined_skill = task_skill + product_skill
        
        if combined_skill >= min_rating:
            skilled.append((worker, combined_skill, task_skill, product_skill))
    
    # Sort by combined skill rating (descending)
    skilled.sort(key=lambda x: x[1], reverse=True)
    return skilled

def get_task_workers_needed(task_name, task_type='process'):
    """Get the number of workers needed for a specific task."""
    if task_type == 'process':
        for name, workers_needed in PROCESSES:
            if name == task_name:
                return workers_needed
    elif task_type == 'machine':
        for name, workers_needed in COMPRESSION_MACHINES:
            if name == task_name:
                return workers_needed
    return 0

def update_worker_skill(worker_name, task_name, task_type, new_rating):
    """Update a worker's skill rating and save to CSV."""
    if worker_name not in WORKER_SKILLS:
        print(f"Worker {worker_name} not found!")
        return False
    
    if task_type == 'process':
        WORKER_SKILLS[worker_name]['processes'][task_name] = new_rating
    elif task_type == 'machine':
        WORKER_SKILLS[worker_name]['machines'][task_name] = new_rating
    else:
        print(f"Invalid task type: {task_type}")
        return False
    
    save_workers_to_csv()
    return True

def save_workers_to_csv():
    """Save current WORKER_SKILLS data back to CSV."""
    with open(WORKERS_CSV, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        header = ["Group", "Worker"]
        for process_data in PROCESSES:
            header.append(process_data[0])  # Get name from tuple
        for machine_data in COMPRESSION_MACHINES:
            header.append(machine_data[0])  # Get name from tuple
        
        writer.writerow(header)
        
        for worker, data in WORKER_SKILLS.items():
            row = [data['group'], worker]
            
            for process_data in PROCESSES:
                process_name = process_data[0]
                row.append(data['processes'].get(process_name, 0))
            
            for machine_data in COMPRESSION_MACHINES:
                machine_name = machine_data[0]
                row.append(data['machines'].get(machine_name, 0))
            
            writer.writerow(row)

def should_track_frequency(task_name, task_type='process'):
    """Check if frequency tracking is enabled for a task"""
    if task_type == 'process':
        for process_data in PROCESSES:
            name = process_data[0]
            if name == task_name:
                # Check if third element (track flag) exists and is True
                return len(process_data) > 2 and process_data[2]
    elif task_type == 'machine':
        for machine_data in COMPRESSION_MACHINES:
            name = machine_data[0]
            if name == task_name:
                # Check if third element (track flag) exists and is True
                return len(machine_data) > 2 and machine_data[2]
    return False

def load_or_create_products_csv():
    """Load products from products CSV."""
    global PRODUCTS
    
    if not os.path.exists(PRODUCTS_CSV):
        print(f"Warning: {PRODUCTS_CSV} not found. No products will be available.")
        PRODUCTS = []
        return
    
    products = []
    
    with open(PRODUCTS_CSV, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            if 'Product' in row and row['Product']:
                products.append(row['Product'])
    
    PRODUCTS = products
    print(f"Loaded {len(PRODUCTS)} products from {PRODUCTS_CSV}")

# Load data at startup
load_or_create_products_csv()  # Load products first
load_or_create_tasks_csv()  # Then load tasks
load_or_create_workers_csv()  # Finally load workers

if __name__ == "__main__":
    print("\n=== Products Summary ===")
    print(f"Products: {len(PRODUCTS)}")
    for product in PRODUCTS[:5]:
        print(f"  - {product}")
    
    print("\n=== Tasks Summary ===")
    print(f"Processes: {len(PROCESSES)}")
    for process_data in PROCESSES:
        name = process_data[0]
        workers = process_data[1]
        track = process_data[2] if len(process_data) > 2 else False
        print(f"  - {name}: {workers} workers needed (Track: {track})")
    
    print(f"\nMachines: {len(COMPRESSION_MACHINES)}")
    for machine_data in COMPRESSION_MACHINES:
        name = machine_data[0]
        workers = machine_data[1]
        track = machine_data[2] if len(machine_data) > 2 else False
        print(f"  - {name}: {workers} workers needed (Track: {track})")
    
    print("\n=== Example: Skilled workers for a product + process ===")
    if PROCESSES and PRODUCTS:
        process_name = PROCESSES[0][0]
        product_name = PRODUCTS[0]
        skilled = get_skilled_workers(process_name, 'process', product_name, min_rating=0)
        print(f"\nProduct: {product_name}")
        print(f"Process: {process_name}")
        for worker, combined, task_skill, prod_skill in skilled[:5]:
            print(f"  {worker}: Combined={combined} (Task={task_skill}, Product={prod_skill})")