"""
Utility functions for the Worker Allocation System
"""
import sys
import os


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


def data_path(relative_path):
    """Get path for writable data files (exports, JSON, etc) - always relative to .exe location"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - use exe directory
        base_path = os.path.dirname(sys.executable)
    else:
        # Running as script - use project root (parent of utils)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    full_path = os.path.join(base_path, relative_path)
    
    # Create directory if it doesn't exist
    directory = os.path.dirname(full_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    return full_path



def sort_workers(workers, exclude=None):
    """Return sorted workers excluding specified list"""
    if exclude is None:
        exclude = []
    return sorted([w for w in workers if w not in exclude])


def bind_mousewheel(canvas):
    """Bind mousewheel to canvas for scrolling"""
    def on_mousewheel(event):
        # Check if canvas still exists before scrolling
        try:
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except Exception:
            # Widget has been destroyed, silently ignore
            pass
    
    def on_enter(event):
        # Only bind if canvas still exists
        try:
            if canvas.winfo_exists():
                canvas.bind_all("<MouseWheel>", on_mousewheel)
        except Exception:
            pass
    
    def on_leave(event):
        # Always try to unbind
        try:
            canvas.unbind_all("<MouseWheel>")
        except Exception:
            pass
    
    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)