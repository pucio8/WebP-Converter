import customtkinter as ctk
from tkinter import Toplevel, Widget, Event
from typing import Optional

# --- Helper class for creating tooltips ---
class Tooltip:
    """A helper class that creates and manages a tooltip for a widget."""

    def __init__(self, widget: Widget, text: str):
        self.widget = widget  # Reference to the widget that will show the tooltip
        self.text = text  # Reference to the text of the tooltip
        self.tooltip_window: Optional[Toplevel] = None  # Reference to the tooltip window, or None if hidden.
        # Binds the function to show the tooltip when the mouse enters the widget.
        self.widget.bind("<Enter>", self.show_tooltip)
        # Binds the function to hide the tooltip when the mouse leaves the widget.
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event: Event):
        """Creates and displays the tooltip window at the correct position."""
        # Get the widget's position relative to its parent. Returns (x, y, width, height).
        x, y, _, _ = self.widget.bbox("insert")
        # Convert the widget's local coordinates to absolute screen coordinates.
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        # Create a new, borderless pop-up window (Toplevel).
        self.tooltip_window = Toplevel(self.widget)
        # Override the window manager's default behavior.
        self.tooltip_window.wm_overrideredirect(True)
        # Set the window's geometry to the calculated position.
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        # Create a new label with the tooltip text.
        label = ctk.CTkLabel(
            self.tooltip_window,
            text=self.text,
            corner_radius=5,
            fg_color=("#333333", "#444444"),
            text_color="white",
            wraplength=200,
            justify="left",
            padx=10,
            pady=5,
        )
        # Pack the label into the window.
        label.pack()

    def hide_tooltip(self, event: Event):
        """Destroys the tooltip window if it exists and resets the state."""
        # Check if the tooltip window actually exists (is not None).
        if self.tooltip_window:
            # If it exists, destroy it completely.
            self.tooltip_window.destroy()
        self.tooltip_window = None  # Reset the tooltip window state to None.
