"""
Main entry point for the Worker Allocation System
"""
import tkinter as tk
from ui.main_window import WorkerAllocationSystem


def main():
    """Initialize and run the application"""
    root = tk.Tk()
    app = WorkerAllocationSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()