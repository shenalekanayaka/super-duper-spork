import csv
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import time

# Get the directory where the script/exe is located
if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

WORKERS_CSV = os.path.join(SCRIPT_DIR, "utils/workers.csv")
PRODUCTS_CSV = os.path.join(SCRIPT_DIR, "utils/products.csv")
TASKS_CSV = os.path.join(SCRIPT_DIR, "utils/tasks.csv")

class CSVManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Manager")
        self.root.geometry("1000x700")
        self.current_tree = None
        self.create_menu()
    
    def safe_write_csv(self, filepath, headers, rows, max_retries=3):
        """Safely write to CSV with retry logic and file lock detection."""
        for attempt in range(max_retries):
            try:
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(rows)
                return True
            except PermissionError:
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Wait before retry
                else:
                    filename = os.path.basename(filepath)
                    messagebox.showerror(
                        "File Access Error", 
                        f"Cannot access {filename}!\n\n"
                        f"The file is currently open in another program (like Excel).\n\n"
                        f"Please close the file and try again."
                    )
                    return False
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
                return False
        return False
    
    def safe_read_csv(self, filepath):
        """Safely read CSV with error handling."""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', newline='', encoding='utf-8') as f:
                    return list(csv.DictReader(f))
            return []
        except PermissionError:
            filename = os.path.basename(filepath)
            messagebox.showerror(
                "File Access Error", 
                f"Cannot read {filename}!\n\n"
                f"The file is currently open in another program.\n\n"
                f"Please close the file and try again."
            )
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {str(e)}")
            return None
    
    def create_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="CSV Manager", font=("Arial", 16)).pack(pady=20)
        
        tk.Button(frame, text="Manage Tasks", command=self.tasks_menu, width=20).pack(pady=5)
        tk.Button(frame, text="Manage Workers", command=self.workers_menu, width=20).pack(pady=5)
        tk.Button(frame, text="View/Edit Worker Skills", command=self.worker_skills_view, width=20).pack(pady=5)
        tk.Button(frame, text="Manage Products", command=self.products_menu, width=20).pack(pady=5)
        tk.Button(frame, text="View/Edit Product-Worker Skills", command=self.product_worker_skills_view, width=30).pack(pady=5)
        tk.Button(frame, text="Exit", command=self.root.quit, width=20).pack(pady=5)
    
    def load_tasks(self):
        data = self.safe_read_csv(TASKS_CSV)
        if data is None:
            return []
        
        tasks = []
        seen = set()
        for row in data:
            # Remove duplicates based on Type and Name
            key = (row.get('Type', '').strip(), row.get('Name', '').strip())
            if key not in seen and key[1]:  # Only add if name exists
                seen.add(key)
                tasks.append(row)
        return tasks
    
    def save_tasks(self, tasks):
        # Ensure utils directory exists
        os.makedirs(os.path.dirname(TASKS_CSV), exist_ok=True)
        
        if not self.safe_write_csv(TASKS_CSV, ["Type", "Name", "Workers_Needed"], tasks):
            return False
        
        # Sync worker skills with tasks
        self.sync_worker_skills_with_tasks()
        return True
    
    def tasks_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Button(frame, text="Back", command=self.create_menu).pack(anchor='w')
        tk.Label(frame, text="Tasks Management", font=("Arial", 14)).pack(pady=10)
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add", command=self.add_task).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Edit", command=self.edit_task).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Delete", command=self.delete_task).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Clean Duplicates", command=self.clean_duplicates, bg='#FF9800').pack(side=tk.LEFT, padx=2)
        
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        processes_frame = tk.Frame(notebook)
        notebook.add(processes_frame, text="Processes")
        
        machines_frame = tk.Frame(notebook)
        notebook.add(machines_frame, text="Machines")
        
        tasks = self.load_tasks()
        processes = [t for t in tasks if t.get('Type') == 'Process']
        machines = [t for t in tasks if t.get('Type') == 'Machine']
        
        self.processes_tree = self.create_tasks_tree(processes_frame, processes)
        self.machines_tree = self.create_tasks_tree(machines_frame, machines)
        
        notebook.bind("<<NotebookTabChanged>>", lambda e: self.update_current_tree(notebook))
        self.current_tree = self.processes_tree
    
    def clean_duplicates(self):
        """Remove duplicate tasks from the CSV"""
        tasks = self.load_tasks()
        original_count = len(tasks)
        
        # Load again to get clean list (already deduped by load_tasks)
        self.save_tasks(tasks)
        
        new_count = len(self.load_tasks())
        removed = original_count - new_count
        
        if removed > 0:
            messagebox.showinfo("Success", f"Removed {removed} duplicate task(s)")
        else:
            messagebox.showinfo("Info", "No duplicates found")
        
        self.tasks_menu()
    
    def update_current_tree(self, notebook):
        current_tab = notebook.index(notebook.select())
        self.current_tree = self.processes_tree if current_tab == 0 else self.machines_tree
    
    def create_tasks_tree(self, parent, tasks):
        tree = ttk.Treeview(parent, columns=("Name", "Workers"), show="headings")
        tree.heading("Name", text="Name")
        tree.heading("Workers", text="Workers Needed")
        tree.column("Name", width=400)
        tree.column("Workers", width=150)
        tree.pack(fill=tk.BOTH, expand=True)
        
        for task in tasks:
            tree.insert("", tk.END, values=(task.get('Name', ''), task.get('Workers_Needed', '')))
        
        return tree
    
    def add_task(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Task")
        dialog.geometry("400x250")
        
        tk.Label(dialog, text="Type:").pack(pady=5)
        task_type = tk.StringVar(value="Process")
        tk.Radiobutton(dialog, text="Process", variable=task_type, value="Process").pack()
        tk.Radiobutton(dialog, text="Machine", variable=task_type, value="Machine").pack()
        
        tk.Label(dialog, text="Name:").pack(pady=5)
        name_entry = tk.Entry(dialog, width=40)
        name_entry.pack()
        
        tk.Label(dialog, text="Workers Needed:").pack(pady=5)
        workers_entry = tk.Entry(dialog, width=40)
        workers_entry.pack()
        
        def save():
            name = name_entry.get().strip()
            workers = workers_entry.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Name required")
                return
            
            try:
                workers_needed = int(workers)
                if workers_needed < 1:
                    messagebox.showerror("Error", "Workers must be at least 1")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid number")
                return
            
            tasks = self.load_tasks()
            # Check for exact duplicate
            if any(t.get('Name', '').strip() == name and t.get('Type') == task_type.get() for t in tasks):
                messagebox.showerror("Error", "Task with this name and type already exists")
                return
            
            tasks.append({'Type': task_type.get(), 'Name': name, 'Workers_Needed': str(workers_needed)})
            self.save_tasks(tasks)
            messagebox.showinfo("Success", "Task added")
            dialog.destroy()
            self.tasks_menu()
        
        tk.Button(dialog, text="Save", command=save).pack(pady=10)
    
    def edit_task(self):
        if not self.current_tree or not self.current_tree.selection():
            messagebox.showwarning("Warning", "Select a task")
            return
        
        item = self.current_tree.item(self.current_tree.selection()[0])
        task_name = item['values'][0]
        current_workers = item['values'][1]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Task")
        dialog.geometry("400x200")
        
        tk.Label(dialog, text="Name:").pack(pady=5)
        name_entry = tk.Entry(dialog, width=40)
        name_entry.insert(0, task_name)
        name_entry.pack()
        
        tk.Label(dialog, text="Workers Needed:").pack(pady=5)
        workers_entry = tk.Entry(dialog, width=40)
        workers_entry.insert(0, str(current_workers))
        workers_entry.pack()
        
        def save():
            new_name = name_entry.get().strip()
            workers = workers_entry.get().strip()
            
            if not new_name:
                messagebox.showerror("Error", "Name required")
                return
            
            try:
                workers_needed = int(workers)
                if workers_needed < 1:
                    messagebox.showerror("Error", "Workers must be at least 1")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid number")
                return
            
            tasks = self.load_tasks()
            old_name = task_name
            for task in tasks:
                if task.get('Name') == old_name:
                    task['Name'] = new_name
                    task['Workers_Needed'] = str(workers_needed)
                    break
            
            self.save_tasks(tasks)
            
            # If name changed, update workers CSV column name
            if old_name != new_name:
                self.rename_worker_skill_column(old_name, new_name)
            
            messagebox.showinfo("Success", "Task updated")
            dialog.destroy()
            self.tasks_menu()
        
        tk.Button(dialog, text="Save", command=save).pack(pady=10)
    
    def delete_task(self):
        if not self.current_tree or not self.current_tree.selection():
            messagebox.showwarning("Warning", "Select a task")
            return
        
        item = self.current_tree.item(self.current_tree.selection()[0])
        task_name = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete '{task_name}'?"):
            tasks = self.load_tasks()
            tasks = [t for t in tasks if t.get('Name') != task_name]
            self.save_tasks(tasks)
            
            # Remove the skill column from workers CSV
            self.remove_skill_column(task_name)
            
            messagebox.showinfo("Success", "Task deleted")
            self.tasks_menu()
    
    # ==================== WORKER FUNCTIONS ====================
    
    def sync_worker_skills_with_tasks(self):
        """Sync worker skills columns with task names."""
        # Ensure utils directory exists
        os.makedirs(os.path.dirname(WORKERS_CSV), exist_ok=True)
        
        tasks = self.load_tasks()
        task_names = [t.get('Name', '').strip() for t in tasks if t.get('Name', '').strip()]
        
        if not os.path.exists(WORKERS_CSV):
            # Create initial workers.csv with headers
            headers = ['Group', 'Worker'] + task_names
            if not self.safe_write_csv(WORKERS_CSV, headers, []):
                return
            return
        
        workers = self.load_workers()
        if not workers:
            return
        
        headers = self.get_worker_headers()
        new_tasks = [task for task in task_names if task not in headers]
        
        if new_tasks:
            headers.extend(new_tasks)
            for worker in workers:
                for task in new_tasks:
                    worker[task] = '0'
            
            self.safe_write_csv(WORKERS_CSV, headers, workers)
    
    def rename_worker_skill_column(self, old_name, new_name):
        """Rename a skill column when a task name is changed."""
        if not os.path.exists(WORKERS_CSV):
            return
        
        workers = self.load_workers()
        if not workers:
            return
        
        headers = self.get_worker_headers()
        
        if old_name in headers:
            # Replace old name with new name in headers
            headers = [new_name if h == old_name else h for h in headers]
            
            # Update each worker's data
            for worker in workers:
                if old_name in worker:
                    worker[new_name] = worker[old_name]
                    del worker[old_name]
            
            self.safe_write_csv(WORKERS_CSV, headers, workers)
    
    def remove_skill_column(self, task_name):
        """Remove a skill column when a task is deleted."""
        if not os.path.exists(WORKERS_CSV):
            return
        
        workers = self.load_workers()
        if not workers:
            return
        
        headers = self.get_worker_headers()
        
        if task_name in headers:
            headers.remove(task_name)
            for worker in workers:
                if task_name in worker:
                    del worker[task_name]
            
            self.safe_write_csv(WORKERS_CSV, headers, workers)
    
    def load_workers(self):
        data = self.safe_read_csv(WORKERS_CSV)
        return data if data is not None else []
    
    def get_worker_headers(self):
        if os.path.exists(WORKERS_CSV):
            try:
                with open(WORKERS_CSV, 'r', newline='', encoding='utf-8') as f:
                    return next(csv.reader(f))
            except (PermissionError, Exception):
                return ["Group", "Worker"]
        return ["Group", "Worker"]
    
    def save_workers(self, workers):
        if not workers:
            return False
        headers = self.get_worker_headers()
        return self.safe_write_csv(WORKERS_CSV, headers, workers)
    
    def workers_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Button(frame, text="Back", command=self.create_menu).pack(anchor='w')
        tk.Label(frame, text="Workers Management", font=("Arial", 14)).pack(pady=10)
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add", command=self.add_worker).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Edit", command=self.edit_worker).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Delete", command=self.delete_worker).pack(side=tk.LEFT, padx=2)
        
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        group_a_frame = tk.Frame(notebook)
        notebook.add(group_a_frame, text="Group A")
        
        group_b_frame = tk.Frame(notebook)
        notebook.add(group_b_frame, text="Group B")
        
        workers = self.load_workers()
        group_a = [w for w in workers if w.get('Group') == 'Group A']
        group_b = [w for w in workers if w.get('Group') == 'Group B']
        
        self.group_a_tree = self.create_workers_tree(group_a_frame, group_a)
        self.group_b_tree = self.create_workers_tree(group_b_frame, group_b)
        
        notebook.bind("<<NotebookTabChanged>>", lambda e: self.update_current_worker_tree(notebook))
        self.current_tree = self.group_a_tree
    
    def update_current_worker_tree(self, notebook):
        current_tab = notebook.index(notebook.select())
        self.current_tree = self.group_a_tree if current_tab == 0 else self.group_b_tree
    
    def create_workers_tree(self, parent, workers):
        tree = ttk.Treeview(parent, columns=("Name",), show="headings")
        tree.heading("Name", text="Worker")
        tree.column("Name", width=400)
        tree.pack(fill=tk.BOTH, expand=True)
        
        for worker in workers:
            tree.insert("", tk.END, values=(worker.get('Worker', ''),))
        
        return tree
    
    def add_worker(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Worker")
        dialog.geometry("400x200")
        
        tk.Label(dialog, text="Group:").pack(pady=5)
        group = tk.StringVar(value="Group A")
        tk.Radiobutton(dialog, text="Group A", variable=group, value="Group A").pack()
        tk.Radiobutton(dialog, text="Group B", variable=group, value="Group B").pack()
        
        tk.Label(dialog, text="Name:").pack(pady=5)
        name_entry = tk.Entry(dialog, width=40)
        name_entry.pack()
        
        def save():
            name = name_entry.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Name required")
                return
            
            workers = self.load_workers()
            if any(w.get('Worker', '').strip() == name for w in workers):
                messagebox.showerror("Error", "Worker already exists")
                return
            
            headers = self.get_worker_headers()
            new_worker = {'Group': group.get(), 'Worker': name}
            for header in headers:
                if header not in ['Group', 'Worker']:
                    new_worker[header] = '0'
            
            workers.append(new_worker)
            if not self.save_workers(workers):
                return
            
            # Add this worker as a column in products CSV
            self.sync_product_workers_with_workers()
            
            messagebox.showinfo("Success", "Worker added")
            dialog.destroy()
            self.workers_menu()
        
        tk.Button(dialog, text="Save", command=save).pack(pady=10)
    
    def edit_worker(self):
        if not self.current_tree or not self.current_tree.selection():
            messagebox.showwarning("Warning", "Select a worker")
            return
        
        item = self.current_tree.item(self.current_tree.selection()[0])
        worker_name = item['values'][0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Worker")
        dialog.geometry("400x200")
        
        # Get current group
        workers = self.load_workers()
        current_worker = next((w for w in workers if w.get('Worker') == worker_name), None)
        if not current_worker:
            messagebox.showerror("Error", "Worker not found")
            return
        
        tk.Label(dialog, text="Group:").pack(pady=5)
        group = tk.StringVar(value=current_worker.get('Group', 'Group A'))
        tk.Radiobutton(dialog, text="Group A", variable=group, value="Group A").pack()
        tk.Radiobutton(dialog, text="Group B", variable=group, value="Group B").pack()
        
        tk.Label(dialog, text="Name:").pack(pady=5)
        name_entry = tk.Entry(dialog, width=40)
        name_entry.insert(0, worker_name)
        name_entry.pack()
        
        def save():
            new_name = name_entry.get().strip()
            
            if not new_name:
                messagebox.showerror("Error", "Name required")
                return
            
            # Check if new name already exists (excluding current worker)
            if new_name != worker_name and any(w.get('Worker', '').strip() == new_name for w in workers):
                messagebox.showerror("Error", "Worker with this name already exists")
                return
            
            # Update worker
            for worker in workers:
                if worker.get('Worker') == worker_name:
                    worker['Worker'] = new_name
                    worker['Group'] = group.get()
                    break
            
            if not self.save_workers(workers):
                return
            
            # If name changed, update products CSV column name
            if worker_name != new_name:
                self.rename_product_worker_column(worker_name, new_name)
            
            messagebox.showinfo("Success", "Worker updated")
            dialog.destroy()
            self.workers_menu()
        
        tk.Button(dialog, text="Save", command=save).pack(pady=10)
    
    def delete_worker(self):
        if not self.current_tree or not self.current_tree.selection():
            messagebox.showwarning("Warning", "Select a worker")
            return
        
        item = self.current_tree.item(self.current_tree.selection()[0])
        worker_name = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete '{worker_name}'?"):
            workers = self.load_workers()
            workers = [w for w in workers if w.get('Worker') != worker_name]
            if not self.save_workers(workers):
                return
            
            # Remove this worker column from products CSV
            self.remove_product_worker_column(worker_name)
            
            messagebox.showinfo("Success", "Worker deleted")
            self.workers_menu()
    
    def worker_skills_view(self):
        """View and edit all worker skills in a table format."""
        if not os.path.exists(WORKERS_CSV):
            messagebox.showerror("Error", f"Workers file not found!\n\nLooking for:\n{WORKERS_CSV}\n\nPlease ensure workers.csv exists in the utils folder.")
            return
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(top_frame, text="Back", command=self.create_menu, width=10).pack(side=tk.LEFT, padx=5)
        tk.Label(top_frame, text="Worker Skills Matrix", font=("Arial", 14)).pack(side=tk.LEFT, padx=20)
        tk.Button(top_frame, text="Save Changes", command=self.save_skills_changes, 
                 bg='#4CAF50', fg='white', width=15).pack(side=tk.RIGHT, padx=5)
        
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=5)
        tk.Label(info_frame, text="Rating: 0=No skill | 1=Basic | 2=Supervised | 3=Independent | 4=Proficient | 5=Expert", 
                font=("Arial", 9, "italic")).pack()
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        group_a_frame = tk.Frame(notebook)
        notebook.add(group_a_frame, text="Group A")
        
        group_b_frame = tk.Frame(notebook)
        notebook.add(group_b_frame, text="Group B")
        
        workers = self.load_workers()
        headers = self.get_worker_headers()
        skill_columns = [h for h in headers if h not in ['Group', 'Worker']]
        
        self.group_a_skills = self.create_skills_table(group_a_frame, workers, skill_columns, 'Group A')
        self.group_b_skills = self.create_skills_table(group_b_frame, workers, skill_columns, 'Group B')
    
    def create_skills_table(self, parent, all_workers, skill_columns, group_name):
        """Create a table showing workers and their skills with editable cells."""
        workers = [w for w in all_workers if w.get('Group') == group_name]
        
        if not workers:
            tk.Label(parent, text=f"No workers found in {group_name}", 
                    font=("Arial", 12)).pack(pady=50)
            return {}
        
        if not skill_columns:
            tk.Label(parent, text="No tasks defined. Please add tasks first.", 
                    font=("Arial", 12)).pack(pady=50)
            return {}
        
        container = tk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(container)
        v_scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        tk.Label(scrollable_frame, text="Worker", font=("Arial", 10, "bold"), 
                relief=tk.RIDGE, width=15, bg='#e0e0e0').grid(row=0, column=0, sticky='nsew', padx=1, pady=1)
        
        for col_idx, skill in enumerate(skill_columns, 1):
            tk.Label(scrollable_frame, text=skill, font=("Arial", 9, "bold"), 
                    relief=tk.RIDGE, width=12, bg='#e0e0e0', wraplength=100).grid(row=0, column=col_idx, sticky='nsew', padx=1, pady=1)
        
        entry_widgets = {}
        
        for row_idx, worker in enumerate(workers, 1):
            worker_name = worker.get('Worker', '')
            
            tk.Label(scrollable_frame, text=worker_name, font=("Arial", 9), 
                    relief=tk.RIDGE, width=15, anchor='w', padx=5).grid(row=row_idx, column=0, sticky='nsew', padx=1, pady=1)
            
            entry_widgets[worker_name] = {}
            for col_idx, skill in enumerate(skill_columns, 1):
                rating = worker.get(skill, '0')
                
                entry = tk.Entry(scrollable_frame, width=5, font=("Arial", 9), justify='center')
                entry.insert(0, rating)
                entry.grid(row=row_idx, column=col_idx, padx=1, pady=1)
                
                entry_widgets[worker_name][skill] = entry
        
        canvas.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        return entry_widgets
    
    def save_skills_changes(self):
        """Save all skill rating changes back to CSV."""
        try:
            workers = self.load_workers()
            
            for worker in workers:
                if worker.get('Group') == 'Group A':
                    worker_name = worker.get('Worker')
                    if worker_name in self.group_a_skills:
                        for skill, entry in self.group_a_skills[worker_name].items():
                            try:
                                rating = int(entry.get())
                                if rating < 0 or rating > 5:
                                    messagebox.showerror("Error", f"Rating for {worker_name} - {skill} must be 0-5!")
                                    return
                                worker[skill] = str(rating)
                            except ValueError:
                                messagebox.showerror("Error", f"Invalid rating for {worker_name} - {skill}!")
                                return
            
            for worker in workers:
                if worker.get('Group') == 'Group B':
                    worker_name = worker.get('Worker')
                    if worker_name in self.group_b_skills:
                        for skill, entry in self.group_b_skills[worker_name].items():
                            try:
                                rating = int(entry.get())
                                if rating < 0 or rating > 5:
                                    messagebox.showerror("Error", f"Rating for {worker_name} - {skill} must be 0-5!")
                                    return
                                worker[skill] = str(rating)
                            except ValueError:
                                messagebox.showerror("Error", f"Invalid rating for {worker_name} - {skill}!")
                                return
            
            if not self.save_workers(workers):
                return
            messagebox.showinfo("Success", "All skill ratings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    # ==================== PRODUCT FUNCTIONS ====================
    
    def sync_product_workers_with_workers(self):
        """Sync product-worker matrix columns with worker names."""
        # Ensure utils directory exists
        os.makedirs(os.path.dirname(PRODUCTS_CSV), exist_ok=True)
        
        workers = self.load_workers()
        worker_names = [w.get('Worker', '').strip() for w in workers if w.get('Worker', '').strip()]
        
        if not os.path.exists(PRODUCTS_CSV):
            # Create initial products.csv with headers
            headers = ['Product'] + worker_names
            self.safe_write_csv(PRODUCTS_CSV, headers, [])
            return
        
        products = self.load_products()
        if not products:
            return
        
        headers = self.get_product_headers()
        new_workers = [worker for worker in worker_names if worker not in headers]
        
        if new_workers:
            headers.extend(new_workers)
            for product in products:
                for worker in new_workers:
                    product[worker] = '0'
            
            self.safe_write_csv(PRODUCTS_CSV, headers, products)
    
    def rename_product_worker_column(self, old_name, new_name):
        """Rename a worker column when a worker name is changed."""
        if not os.path.exists(PRODUCTS_CSV):
            return
        
        products = self.load_products()
        if not products:
            return
        
        headers = self.get_product_headers()
        
        if old_name in headers:
            # Replace old name with new name in headers
            headers = [new_name if h == old_name else h for h in headers]
            
            # Update each product's data
            for product in products:
                if old_name in product:
                    product[new_name] = product[old_name]
                    del product[old_name]
            
            self.safe_write_csv(PRODUCTS_CSV, headers, products)
    
    def remove_product_worker_column(self, worker_name):
        """Remove a worker column when a worker is deleted."""
        if not os.path.exists(PRODUCTS_CSV):
            return
        
        products = self.load_products()
        if not products:
            return
        
        headers = self.get_product_headers()
        
        if worker_name in headers:
            headers.remove(worker_name)
            for product in products:
                if worker_name in product:
                    del product[worker_name]
            
            self.safe_write_csv(PRODUCTS_CSV, headers, products)
    
    def load_products(self):
        data = self.safe_read_csv(PRODUCTS_CSV)
        return data if data is not None else []
    
    def get_product_headers(self):
        if os.path.exists(PRODUCTS_CSV):
            try:
                with open(PRODUCTS_CSV, 'r', newline='', encoding='utf-8') as f:
                    return next(csv.reader(f))
            except (PermissionError, Exception):
                return ["Product"]
        return ["Product"]
    
    def save_products(self, products):
        if not products:
            return False
        headers = self.get_product_headers()
        return self.safe_write_csv(PRODUCTS_CSV, headers, products)
    
    def products_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Button(frame, text="Back", command=self.create_menu).pack(anchor='w')
        tk.Label(frame, text="Products Management", font=("Arial", 14)).pack(pady=10)
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add", command=self.add_product).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Edit", command=self.edit_product).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Delete", command=self.delete_product).pack(side=tk.LEFT, padx=2)
        
        # Single list view for all products
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        products = self.load_products()
        self.current_tree = self.create_products_tree(tree_frame, products)
    
    def create_products_tree(self, parent, products):
        tree = ttk.Treeview(parent, columns=("Name",), show="headings")
        tree.heading("Name", text="Product")
        tree.column("Name", width=400)
        tree.pack(fill=tk.BOTH, expand=True)
        
        for product in products:
            tree.insert("", tk.END, values=(product.get('Product', ''),))
        
        return tree
    
    def add_product(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Product")
        dialog.geometry("400x150")
        
        tk.Label(dialog, text="Product Name:").pack(pady=10)
        name_entry = tk.Entry(dialog, width=40)
        name_entry.pack()
        
        def save():
            name = name_entry.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Name required")
                return
            
            products = self.load_products()
            if any(p.get('Product', '').strip() == name for p in products):
                messagebox.showerror("Error", "Product already exists")
                return
            
            headers = self.get_product_headers()
            new_product = {'Product': name}
            for header in headers:
                if header != 'Product':
                    new_product[header] = '0'
            
            products.append(new_product)
            if not self.save_products(products):
                return
            messagebox.showinfo("Success", "Product added")
            dialog.destroy()
            self.products_menu()
        
        tk.Button(dialog, text="Save", command=save).pack(pady=10)
    
    def edit_product(self):
        if not self.current_tree or not self.current_tree.selection():
            messagebox.showwarning("Warning", "Select a product")
            return
        
        item = self.current_tree.item(self.current_tree.selection()[0])
        product_name = item['values'][0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Product")
        dialog.geometry("400x150")
        
        tk.Label(dialog, text="Product Name:").pack(pady=10)
        name_entry = tk.Entry(dialog, width=40)
        name_entry.insert(0, product_name)
        name_entry.pack()
        
        def save():
            new_name = name_entry.get().strip()
            
            if not new_name:
                messagebox.showerror("Error", "Name required")
                return
            
            products = self.load_products()
            
            # Check if new name already exists (excluding current product)
            if new_name != product_name and any(p.get('Product', '').strip() == new_name for p in products):
                messagebox.showerror("Error", "Product with this name already exists")
                return
            
            # Update product name
            for product in products:
                if product.get('Product') == product_name:
                    product['Product'] = new_name
                    break
            
            if not self.save_products(products):
                return
            messagebox.showinfo("Success", "Product updated")
            dialog.destroy()
            self.products_menu()
        
        tk.Button(dialog, text="Save", command=save).pack(pady=10)
    
    def delete_product(self):
        if not self.current_tree or not self.current_tree.selection():
            messagebox.showwarning("Warning", "Select a product")
            return
        
        item = self.current_tree.item(self.current_tree.selection()[0])
        product_name = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete '{product_name}'?"):
            products = self.load_products()
            products = [p for p in products if p.get('Product') != product_name]
            if not self.save_products(products):
                return
            messagebox.showinfo("Success", "Product deleted")
            self.products_menu()
    
    def product_worker_skills_view(self):
        """View and edit worker skill ratings for each product."""
        if not os.path.exists(PRODUCTS_CSV):
            messagebox.showerror("Error", f"Products file not found!\n\nLooking for:\n{PRODUCTS_CSV}\n\nPlease ensure products.csv exists in the utils folder.")
            return
        
        if not os.path.exists(WORKERS_CSV):
            messagebox.showerror("Error", f"Workers file not found!\n\nLooking for:\n{WORKERS_CSV}\n\nPlease add workers first.")
            return
        
        # Sync workers to products CSV before displaying
        self.sync_product_workers_with_workers()
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(top_frame, text="Back", command=self.create_menu, width=10).pack(side=tk.LEFT, padx=5)
        tk.Label(top_frame, text="Product-Worker Skills Matrix", font=("Arial", 14)).pack(side=tk.LEFT, padx=20)
        tk.Button(top_frame, text="Save Changes", command=self.save_product_worker_skills_changes, 
                 bg='#4CAF50', fg='white', width=15).pack(side=tk.RIGHT, padx=5)
        
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=5)
        tk.Label(info_frame, text="Rating: 0=No experience | 1=Basic | 2=Supervised | 3=Independent | 4=Proficient | 5=Expert", 
                font=("Arial", 9, "italic")).pack()
        
        # Create tabs for worker groups
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        group_a_frame = tk.Frame(notebook)
        notebook.add(group_a_frame, text="Group A")
        
        group_b_frame = tk.Frame(notebook)
        notebook.add(group_b_frame, text="Group B")
        
        products = self.load_products()
        
        if not products:
            tk.Label(group_a_frame, text="No products found. Please add products first.", 
                    font=("Arial", 12)).pack(pady=50)
            tk.Label(group_b_frame, text="No products found. Please add products first.", 
                    font=("Arial", 12)).pack(pady=50)
            return
        
        # Get workers by group
        workers = self.load_workers()
        group_a_workers = [w.get('Worker', '').strip() for w in workers if w.get('Group') == 'Group A' and w.get('Worker', '').strip()]
        group_b_workers = [w.get('Worker', '').strip() for w in workers if w.get('Group') == 'Group B' and w.get('Worker', '').strip()]
        
        if not group_a_workers and not group_b_workers:
            tk.Label(group_a_frame, text="No workers found. Please add workers first.", 
                    font=("Arial", 12)).pack(pady=50)
            tk.Label(group_b_frame, text="No workers found. Please add workers first.", 
                    font=("Arial", 12)).pack(pady=50)
            return
        
        # Create tables for each group
        self.group_a_product_worker_entries = self.create_product_worker_table(group_a_frame, products, group_a_workers) if group_a_workers else {}
        self.group_b_product_worker_entries = self.create_product_worker_table(group_b_frame, products, group_b_workers) if group_b_workers else {}
        
        if not group_a_workers:
            tk.Label(group_a_frame, text="No workers in Group A", 
                    font=("Arial", 12)).pack(pady=50)
        if not group_b_workers:
            tk.Label(group_b_frame, text="No workers in Group B", 
                    font=("Arial", 12)).pack(pady=50)
    
    def create_product_worker_table(self, parent, products, worker_columns):
        """Create a table showing products and worker skill ratings with editable cells."""
        if not products:
            tk.Label(parent, text="No products found", 
                    font=("Arial", 12)).pack(pady=50)
            return {}
        
        if not worker_columns:
            tk.Label(parent, text="No workers in this group", 
                    font=("Arial", 12)).pack(pady=50)
            return {}
        
        container = tk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(container)
        v_scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        tk.Label(scrollable_frame, text="Product", font=("Arial", 10, "bold"), 
                relief=tk.RIDGE, width=15, bg='#e0e0e0').grid(row=0, column=0, sticky='nsew', padx=1, pady=1)
        
        for col_idx, worker in enumerate(worker_columns, 1):
            tk.Label(scrollable_frame, text=worker, font=("Arial", 9, "bold"), 
                    relief=tk.RIDGE, width=12, bg='#e0e0e0', wraplength=100).grid(row=0, column=col_idx, sticky='nsew', padx=1, pady=1)
        
        entry_widgets = {}
        
        for row_idx, product in enumerate(products, 1):
            product_name = product.get('Product', '')
            
            tk.Label(scrollable_frame, text=product_name, font=("Arial", 9), 
                    relief=tk.RIDGE, width=15, anchor='w', padx=5).grid(row=row_idx, column=0, sticky='nsew', padx=1, pady=1)
            
            entry_widgets[product_name] = {}
            for col_idx, worker in enumerate(worker_columns, 1):
                rating = product.get(worker, '0')
                
                entry = tk.Entry(scrollable_frame, width=5, font=("Arial", 9), justify='center')
                entry.insert(0, rating)
                entry.grid(row=row_idx, column=col_idx, padx=1, pady=1)
                
                entry_widgets[product_name][worker] = entry
        
        canvas.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        return entry_widgets
    
    def save_product_worker_skills_changes(self):
        """Save all product-worker skill rating changes back to CSV."""
        try:
            products = self.load_products()
            
            # Update Group A workers
            for product in products:
                product_name = product.get('Product')
                if product_name in self.group_a_product_worker_entries:
                    for worker, entry in self.group_a_product_worker_entries[product_name].items():
                        try:
                            rating = int(entry.get())
                            if rating < 0 or rating > 5:
                                messagebox.showerror("Error", f"Rating for {product_name} - {worker} must be 0-5!")
                                return
                            product[worker] = str(rating)
                        except ValueError:
                            messagebox.showerror("Error", f"Invalid rating for {product_name} - {worker}!")
                            return
            
            # Update Group B workers
            for product in products:
                product_name = product.get('Product')
                if product_name in self.group_b_product_worker_entries:
                    for worker, entry in self.group_b_product_worker_entries[product_name].items():
                        try:
                            rating = int(entry.get())
                            if rating < 0 or rating > 5:
                                messagebox.showerror("Error", f"Rating for {product_name} - {worker} must be 0-5!")
                                return
                            product[worker] = str(rating)
                        except ValueError:
                            messagebox.showerror("Error", f"Invalid rating for {product_name} - {worker}!")
                            return
            
            if not self.save_products(products):
                return
            messagebox.showinfo("Success", "All product-worker skills saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")

def main():
    root = tk.Tk()
    app = CSVManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()