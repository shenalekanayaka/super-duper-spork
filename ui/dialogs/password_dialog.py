"""
Password dialog for protected actions
"""
import tkinter as tk
from tkinter import messagebox


class PasswordDialog:
    """Dialog for password authentication"""
    
    # Set your password here
    ADMIN_PASSWORD = "5kDk9o"  # For editing allocations
    USER_PASSWORD = "user123"    # For creating allocations and navigation
    
    def __init__(self, parent, password_type='admin'):
        self.parent = parent
        self.result = False
        self.dialog = None
        self.password_type = password_type  # 'admin' or 'user'
    
    def show(self):
        """Show password dialog and return True if authenticated"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Authentication Required")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg="#f0f0f0")
        
        # Center the dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Title
        title = tk.Label(
            self.dialog,
            text="🔒 Enter Password to Edit",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        # Password frame
        password_frame = tk.Frame(self.dialog, bg="#f0f0f0")
        password_frame.pack(pady=10)
        
        password_label = tk.Label(
            password_frame,
            text="Password:",
            font=("Arial", 12),
            bg="#f0f0f0"
        )
        password_label.pack(side=tk.LEFT, padx=5)
        
        self.password_entry = tk.Entry(
            password_frame,
            font=("Arial", 12),
            show="●",
            width=20
        )
        self.password_entry.pack(side=tk.LEFT, padx=5)
        self.password_entry.focus()
        
        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self.verify_password())
        
        # Buttons frame
        button_frame = tk.Frame(self.dialog, bg="#f0f0f0")
        button_frame.pack(pady=20)
        
        ok_btn = tk.Button(
            button_frame,
            text="✓ OK",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            width=10,
            command=self.verify_password,
            cursor="hand2"
        )
        ok_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(
            button_frame,
            text="✗ Cancel",
            font=("Arial", 11, "bold"),
            bg="#e74c3c",
            fg="white",
            width=10,
            command=self.cancel,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # Wait for dialog to close
        self.parent.wait_window(self.dialog)
        
        return self.result
    
    def verify_password(self):
        """Verify entered password"""
        entered_password = self.password_entry.get()
        
        # Check against the appropriate password
        correct_password = self.ADMIN_PASSWORD if self.password_type == 'admin' else self.USER_PASSWORD
        
        if entered_password == correct_password:
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror(
                "Authentication Failed",
                "Incorrect password. Please try again.",
                parent=self.dialog
            )
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()
    
    def cancel(self):
        """Cancel authentication"""
        self.result = False
        self.dialog.destroy()