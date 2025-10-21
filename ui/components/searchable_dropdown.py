"""
Searchable dropdown component with a clear button
"""
import tkinter as tk
from tkinter import ttk

class SearchableDropdown:
    """A dropdown with search functionality, keyboard controls, and a clear button."""

    def __init__(self, parent, values, on_select=None, width=30, default_text="-- Select --", search_mode='startswith'):
        """
        Create a searchable dropdown.

        Args:
            parent: The parent widget.
            values: A list of values for the dropdown.
            on_select: A callback function to call when a selection is made.
            width: The width of the dropdown entry.
            default_text: Placeholder text when nothing is selected.
            search_mode: 'startswith' or 'contains' for filtering.
        """
        self.parent = parent
        self.values = sorted(values)
        self.on_select = on_select
        self.default_text = default_text
        self.search_mode = search_mode.lower()
        if self.search_mode not in ['startswith', 'contains']:
            raise ValueError("search_mode must be 'startswith' or 'contains'")

        self.selected_value = tk.StringVar()
        self.last_selected = None
        self._filter_after_id = None
        self.no_results_message = "No results found"
        self._placeholder_active = False

        # Main frame to hold the combobox and the clear button
        self.container = ttk.Frame(parent)
        self.container.grid_columnconfigure(0, weight=1)

        # Style for placeholder text
        self.style = ttk.Style(parent)
        self.style.configure('Placeholder.TCombobox', foreground='gray')
        
        # Create combobox
        self.combobox = ttk.Combobox(
            self.container,
            textvariable=self.selected_value,
            width=width,
            font=("Arial", 11)
        )
        self.combobox['values'] = self.values
        self.combobox.grid(row=0, column=0, sticky='ew')

        # Create the clear button
        self.clear_button = ttk.Button(
            self.container, text="×", width=2, command=self._clear_selection
        )
        
        # Bind events
        self.combobox.bind('<<ComboboxSelected>>', self._on_select)
        self.combobox.bind('<KeyRelease>', self._on_keyrelease)
        self.combobox.bind('<FocusIn>', self._on_focus)
        self.combobox.bind('<FocusOut>', self._on_focus_out)

        self.set(None)

    def _show_clear_button(self):
        self.clear_button.grid(row=0, column=1, padx=(2, 0))

    def _hide_clear_button(self):
        self.clear_button.grid_remove()

    def _clear_selection(self, event=None):
        self.set(None)
        if self.on_select:
            self.on_select(None)
        self.parent.focus()

    def _apply_placeholder(self):
        self.selected_value.set(self.default_text)
        self.combobox.configure(style='Placeholder.TCombobox')
        self._placeholder_active = True
        self._hide_clear_button()
        
    def _remove_placeholder(self):
        self.combobox.configure(style='TCombobox')
        self._placeholder_active = False
        if self.get() is not None:
             self._show_clear_button()

    def _on_focus(self, event=None):
        """Handle focus to remove placeholder on the first interaction."""
        if self._placeholder_active:
            self._remove_placeholder()
            self.combobox.set('')

    def _on_focus_out(self, event=None):
        self.parent.after(150, self._check_focus_out)
        
    def _check_focus_out(self):
        try:
            focused_widget = self.parent.focus_get()
            if focused_widget in (self.combobox, self.clear_button):
                return
        except KeyError:
            pass 

        if not self.get() and not self.selected_value.get().strip():
            self.set(self.last_selected)

    def _on_select(self, event=None):
        value = self.selected_value.get()
        if value == self.no_results_message:
            self.set(self.last_selected)
            return
            
        if value and value in self.values:
            self.last_selected = value
            self._remove_placeholder()
            if self.on_select:
                self.on_select(value)
            self.parent.focus()
            self.combobox.selection_clear()
            
    def _on_keyrelease(self, event):
        # When user starts typing, ensure placeholder is gone
        if self._placeholder_active:
            self._remove_placeholder()
            # Keep the typed character
            current_char = event.char
            if len(current_char) == 1 and current_char.isalnum():
                 self.selected_value.set(current_char)


        if event.keysym == 'Escape':
            self.set(self.last_selected)
            self.parent.focus()
            return
        if event.keysym == 'Return':
            if self.combobox['values']:
                top_match = self.combobox['values'][0]
                if top_match != self.no_results_message:
                    self.set(top_match)
                    self._on_select()
                    return
        if self._filter_after_id:
            self.parent.after_cancel(self._filter_after_id)
        self._filter_after_id = self.parent.after(250, self._filter_values)

    def _filter_values(self):
        typed = self.selected_value.get().lower()
        if not typed:
            filtered_values = self.values
        else:
            if self.search_mode == 'contains':
                filtered_values = [v for v in self.values if typed in v.lower()]
            else:
                filtered_values = [v for v in self.values if v.lower().startswith(typed)]
        self.combobox['values'] = filtered_values if filtered_values else [self.no_results_message]
        # Only open dropdown if there's text
        if typed:
            self.combobox.event_generate('<Down>')

    def get(self):
        return self.selected_value.get() if not self._placeholder_active and self.selected_value.get() in self.values else None

    def set(self, value):
        if value:
            correct_case_value = next((v for v in self.values if v.lower() == value.lower()), None)
            if correct_case_value:
                self.selected_value.set(correct_case_value)
                self.last_selected = correct_case_value
                self._remove_placeholder()
                return
        self._apply_placeholder()
        self.last_selected = None
    
    def update_values(self, new_values):
        self.values = sorted(new_values)
        self.combobox['values'] = self.values
        self.set(None)

    def pack(self, **kwargs):
        self.container.pack(**kwargs)
    
    def grid(self, **kwargs):
        self.container.grid(**kwargs)
    
    def place(self, **kwargs):
        self.container.place(**kwargs)