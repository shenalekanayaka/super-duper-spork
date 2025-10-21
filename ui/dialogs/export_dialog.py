"""
Dialog for exporting results
"""
import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import platform
import subprocess


class ExportDialog:
    """Dialog for shift time input and export"""
    
    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self.shift_time = None
    
    def show(self):
        """Export results using already selected shift time"""
        # Use the shift time from state instead of asking
        shift_time = self.state.shift_time
        
        if not shift_time:
            messagebox.showwarning("No Shift Time", "Shift time not set!")
            return
        
        # Import here to avoid circular imports
        from export_results import ResultsExporter
        
        try:
            exporter = ResultsExporter(self.state)
            
            # Export to JSON and PDF
            json_file = exporter.save_allocation_json(shift_time)
            pdf_file = exporter.export_to_pdf(shift_time)
            
            # Show success message
            result = messagebox.askyesno(
                "Export Successful",
                f"Files created successfully!\n\n"
                f"JSON: {os.path.basename(json_file)}\n"
                f"PDF: {os.path.basename(pdf_file)}\n\n"
                f"Do you want to open the folder?"
            )
            
            if result:
                self.open_folder(os.path.dirname(pdf_file))
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export:\n{str(e)}")
    
    def open_folder(self, path):
        """Open folder in file explorer"""
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", path])
        else:  # Linux
            subprocess.Popen(["xdg-open", path])