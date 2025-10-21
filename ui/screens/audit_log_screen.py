"""
Audit log viewer screen
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ui.screens.base_screen import BaseScreen
import os


class AuditLogScreen(BaseScreen):
    """Screen for viewing allocation edit history/audit trail"""
    
    def show(self, **kwargs):
        allocation_date = kwargs.get('allocation_date')
        shift_time = kwargs.get('shift_time')
        self.return_filepath = kwargs.get('filepath')
        
        # Title
        if allocation_date and shift_time:
            title_text = f"📋 Audit Trail - {allocation_date} {shift_time}"
            history = self.state.audit_trail.get_allocation_audit_log(allocation_date, shift_time)
        else:
            title_text = "📋 Recent Audit Trail"
            history = self.state.audit_trail.get_recent_changes(100)
        
        title = self.create_title(title_text, 22)
        title.pack(pady=20)
        
        # Info bar
        info_frame = tk.Frame(self.main_frame, bg="#e8f4f8", relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.X, padx=30, pady=10)
        
        info_text = f"Total Entries: {len(history)}"
        if history:
            info_text += f" | Oldest: {history[0]['timestamp']} | Newest: {history[-1]['timestamp']}"
        
        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 10),
            bg="#e8f4f8",
            fg="#2c3e50"
        )
        info_label.pack(pady=8)
        
        if not history:
            no_history = tk.Label(
                self.main_frame,
                text="No audit trail entries found",
                font=("Arial", 14),
                bg="#f0f0f0",
                fg="#7f8c8d"
            )
            no_history.pack(pady=50)
        else:
            # Create table
            self.create_audit_table(history)
        
        # Bottom buttons
        button_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        button_frame.pack(side=tk.BOTTOM, pady=20, fill=tk.X, padx=20)
        
        back_btn = self.create_button(
            button_frame,
            "← Back",
            self.go_back,
            bg="#95a5a6"
        )
        back_btn.pack(side=tk.LEFT, padx=5)
        
        if history:
            export_btn = self.create_button(
                button_frame,
                "📄 Export Report",
                self.export_audit_report,
                bg="#16a085"
            )
            export_btn.pack(side=tk.LEFT, padx=5)
    
    def go_back(self):
        """Go back to previous screen"""
        if self.return_filepath:
            self.app.show_screen('history_viewer', filepath=self.return_filepath)
        else:
            self.app.show_screen('date_shift')
    
    def create_audit_table(self, history):
        """Create table showing audit entries"""
        # Frame for table with scrolling
        canvas_frame = tk.Frame(self.main_frame, bg="#ffffff")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create Treeview
        columns = ('timestamp', 'type', 'date', 'shift', 'details')
        tree = ttk.Treeview(canvas_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        tree.heading('timestamp', text='Timestamp')
        tree.heading('type', text='Change Type')
        tree.heading('date', text='Allocation Date')
        tree.heading('shift', text='Shift')
        tree.heading('details', text='Details')
        
        # Define column widths
        tree.column('timestamp', width=150, anchor='w')
        tree.column('type', width=180, anchor='w')
        tree.column('date', width=120, anchor='center')
        tree.column('shift', width=80, anchor='center')
        tree.column('details', width=350, anchor='w')
        
        # Color tags for different change types
        tree.tag_configure('created', background='#d4edda')
        tree.tag_configure('edited', background='#fff3cd')
        tree.tag_configure('deleted', background='#f8d7da')
        tree.tag_configure('normal', background='#ffffff')
        
        # Add data (newest first)
        for entry in reversed(history):
            details_str = self.format_details(entry['details'])
            
            # Determine tag based on change type
            if 'CREATED' in entry['change_type']:
                tag = 'created'
            elif 'DELETED' in entry['change_type']:
                tag = 'deleted'
            elif 'EDITED' in entry['change_type'] or 'CHANGED' in entry['change_type']:
                tag = 'edited'
            else:
                tag = 'normal'
            
            tree.insert('', tk.END, values=(
                entry['timestamp'],
                self.format_change_type(entry['change_type']),
                entry['allocation_date'],
                entry['shift_time'],
                details_str
            ), tags=(tag,))
        
        # Add scrollbars
        vsb = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=tree.yview)
        hsb = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click to show details
        tree.bind('<Double-1>', lambda e: self.show_entry_details(tree))
    
    def format_change_type(self, change_type):
        """Format change type for display"""
        return change_type.replace('_', ' ').title()
    
    def format_details(self, details):
        """Format details dictionary as string"""
        if isinstance(details, dict):
            parts = []
            for key, value in details.items():
                if isinstance(value, list):
                    if len(value) <= 3:
                        parts.append(f"{key}: {', '.join(map(str, value))}")
                    else:
                        parts.append(f"{key}: {len(value)} items")
                elif isinstance(value, dict):
                    parts.append(f"{key}: {len(value)} entries")
                else:
                    parts.append(f"{key}: {value}")
            return " | ".join(parts[:3])  # Limit to 3 items for display
        return str(details)
    
    def show_entry_details(self, tree):
        """Show full details of selected audit entry"""
        selection = tree.selection()
        if not selection:
            return
        
        item = tree.item(selection[0])
        values = item['values']
        
        # Find the full entry
        timestamp = values[0]
        history = self.state.audit_trail.load_audit_log()
        
        entry = None
        for e in history:
            if e['timestamp'] == timestamp:
                entry = e
                break
        
        if not entry:
            return
        
        # Create detail window
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Audit Entry Details")
        detail_window.geometry("600x400")
        detail_window.configure(bg="#f0f0f0")
        
        # Title
        title = tk.Label(
            detail_window,
            text="Audit Entry Details",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0"
        )
        title.pack(pady=10)
        
        # Scrollable text
        text_frame = tk.Frame(detail_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        text = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
        scrollbar = tk.Scrollbar(text_frame, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Format and insert details
        text.insert('1.0', f"Entry ID: {entry['id']}\n")
        text.insert('end', f"Timestamp: {entry['timestamp']}\n")
        text.insert('end', f"Change Type: {self.format_change_type(entry['change_type'])}\n")
        text.insert('end', f"Allocation Date: {entry['allocation_date']}\n")
        text.insert('end', f"Shift Time: {entry['shift_time']}\n")
        text.insert('end', f"User: {entry['user']}\n")
        text.insert('end', "\nDetails:\n")
        text.insert('end', "=" * 50 + "\n")
        
        import json
        details_json = json.dumps(entry['details'], indent=2, ensure_ascii=False)
        text.insert('end', details_json)
        
        text.configure(state='disabled')
        
        # Close button
        close_btn = tk.Button(
            detail_window,
            text="Close",
            font=("Arial", 11, "bold"),
            bg="#95a5a6",
            fg="white",
            width=15,
            command=detail_window.destroy
        )
        close_btn.pack(pady=10)
    
    def export_audit_report(self):
        """Export audit trail to text file"""
        try:
            report_file = self.state.audit_trail.export_audit_report()
            
            result = messagebox.askyesno(
                "Report Exported",
                f"Audit report exported successfully!\n\n"
                f"{os.path.basename(report_file)}\n\n"
                f"Do you want to open the folder?"
            )
            
            if result:
                import platform
                import subprocess
                folder = os.path.dirname(report_file)
                if platform.system() == "Windows":
                    os.startfile(folder)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", folder])
                else:
                    subprocess.Popen(["xdg-open", folder])
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report:\n{str(e)}")