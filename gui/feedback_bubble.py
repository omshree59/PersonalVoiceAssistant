import tkinter as tk
import time

class FeedbackBubble:
    """Floating notification toast bubble displaying recognized speech and status."""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", False)
        self.window.attributes("-alpha", 0.0) # Start invisible
        
        # Windows transparent background setup
        bg_color = "#0f172a"
        self.window.configure(bg=bg_color)
        
        # Container frame with border
        self.frame = tk.Frame(
            self.window,
            bg=bg_color,
            highlightbackground="#38bdf8",
            highlightthickness=1,
            padx=14,
            pady=10
        )
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Title / Status Label
        self.status_label = tk.Label(
            self.frame,
            text="Voice Listener",
            font=("Segoe UI", 9, "bold"),
            fg="#38bdf8",
            bg=bg_color
        )
        self.status_label.pack(anchor="w")
        
        # Detail / Command Label
        self.message_label = tk.Label(
            self.frame,
            text="",
            font=("Segoe UI", 9),
            fg="#f1f5f9",
            bg=bg_color,
            wraplength=280,
            justify="left"
        )
        self.message_label.pack(anchor="w", pady=(3, 0))
        
        self._fade_job = None
        self._hide_job = None

    def show(self, status, message, status_color="#38bdf8", auto_hide_seconds=3.5):
        """Displays the bubble with given status and message near parent widget."""
        if self._hide_job:
            self.parent.after_cancel(self._hide_job)
            self._hide_job = None
            
        self.status_label.configure(text=status, fg=status_color)
        self.frame.configure(highlightbackground=status_color)
        self.message_label.configure(text=message)
        
        # Position bubble right next to the floating widget
        self.window.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        widget_w = self.parent.winfo_width()
        
        bubble_w = self.window.winfo_reqwidth()
        bubble_h = self.window.winfo_reqheight()
        
        screen_w = self.parent.winfo_screenwidth()
        
        # If widget is near right edge, place bubble to the left; otherwise to the right
        if parent_x + widget_w + bubble_w + 20 > screen_w:
            pos_x = parent_x - bubble_w - 12
        else:
            pos_x = parent_x + widget_w + 12
            
        pos_y = parent_y + (self.parent.winfo_height() - bubble_h) // 2
        
        self.window.geometry(f"+{pos_x}+{pos_y}")
        self.window.attributes("-alpha", 0.96)
        self.window.deiconify()
        self.window.lift()
        
        if auto_hide_seconds and auto_hide_seconds > 0:
            self._hide_job = self.parent.after(int(auto_hide_seconds * 1000), self.hide)

    def hide(self):
        """Fades out and hides the bubble."""
        self.window.attributes("-alpha", 0.0)
        self.window.withdraw()
