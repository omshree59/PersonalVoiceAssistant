import os
import sys
import math
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from gui.feedback_bubble import FeedbackBubble
from automation.profile_helper import get_installed_chrome_profiles

TRANSPARENT_KEY = "#010101"

class FloatingWidget:
    """Cute animated desktop cat companion for the voice listener."""
    
    STATE_IDLE = "IDLE"
    STATE_LISTENING = "LISTENING"
    STATE_PROCESSING = "PROCESSING"
    STATE_SUCCESS = "SUCCESS"

    def __init__(self, on_toggle_listen=None, get_audio_energy=None):
        self.on_toggle_listen = on_toggle_listen
        self.get_audio_energy = get_audio_energy
        self.state = self.STATE_IDLE
        
        self.root = tk.Tk()
        self.root.title("Desktop Cat Voice Listener")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        # Transparent background key for Windows (only the cat is visible!)
        self.root.configure(bg=TRANSPARENT_KEY)
        self.root.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        
        # Application Icon
        ico_path = os.path.join(config.ASSETS_DIR, "icon.ico")
        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(ico_path)
            except Exception:
                pass
                
        # Widget Dimensions
        # Extra vertical space (160px) allows the cat to jump smoothly and show ear ripples
        self.win_w = 140
        self.win_h = 160
        self.base_cat_w = 96
        self.base_cat_h = 116
        self.ground_y = 152  # Feet baseline resting coordinate
        self.center_x = self.win_w // 2
        
        # Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.win_w,
            height=self.win_h,
            bg=TRANSPARENT_KEY,
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Load and prepare cat sprites
        self._load_sprites()
        
        # Restore saved desktop position
        self._init_position()
        
        # Dragging & click tracking
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._has_moved = False
        
        # Bindings
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.canvas.bind("<Button-3>", self._show_context_menu)
        
        # Feedback Toast Bubble
        self.bubble = FeedbackBubble(self.root)
        
        # Animation State Variables
        self._frame_count = 0
        self._jump_phase = 0.0
        self._blink_counter = 0
        self._is_blinking = False
        self._ear_wave_phase = 0.0
        self._photo_cache = {}
        self._current_photo = None
        
        # Start Animation Loop (~30 FPS)
        self._animate()

    def _load_sprites(self):
        """Loads and pre-resizes cat animation frames."""
        assets = config.ASSETS_DIR
        names = ["cat_neutral", "cat_ear_left", "cat_ear_right", "cat_ear_both", "cat_blink", "cat_happy"]
        self.pil_sprites = {}
        
        for name in names:
            p = os.path.join(assets, f"{name}.png")
            if os.path.exists(p):
                self.pil_sprites[name] = Image.open(p).convert("RGBA")
            else:
                fallback = os.path.join(assets, "cat_clean.png")
                self.pil_sprites[name] = Image.open(fallback).convert("RGBA")

    def _init_position(self):
        """Loads saved position or places cat neatly at bottom-right corner of screen."""
        settings = config.load_settings()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        
        saved_x = settings.get("window_x")
        saved_y = settings.get("window_y")
        
        if saved_x is not None and saved_y is not None:
            x = max(10, min(saved_x, screen_w - self.win_w - 10))
            y = max(10, min(saved_y, screen_h - self.win_h - 10))
        else:
            x = screen_w - self.win_w - 45
            y = screen_h - self.win_h - 90
            
        self.root.geometry(f"{self.win_w}x{self.win_h}+{x}+{y}")

    def _save_position(self):
        """Saves current desktop position."""
        settings = config.load_settings()
        settings["window_x"] = self.root.winfo_x()
        settings["window_y"] = self.root.winfo_y()
        config.save_settings(settings)

    def _on_mouse_down(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self._has_moved = False

    def _on_mouse_drag(self, event):
        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        if abs(dx) > 3 or abs(dy) > 3:
            self._has_moved = True
            new_x = self.root.winfo_x() + dx
            new_y = self.root.winfo_y() + dy
            self.root.geometry(f"+{new_x}+{new_y}")

    def _on_mouse_up(self, event):
        if self._has_moved:
            self._save_position()
        else:
            # Click detected -> Toggle Voice Listener!
            if self.on_toggle_listen:
                self.on_toggle_listen()

    def set_state(self, new_state):
        """Updates animation state: IDLE, LISTENING, PROCESSING, SUCCESS."""
        self.state = new_state
        self._jump_phase = 0.0

    def _get_scaled_photo(self, sprite_name, width, height):
        """Resizes and caches PhotoImage for smooth performance."""
        key = (sprite_name, int(width), int(height))
        if key in self._photo_cache:
            return self._photo_cache[key]
            
        base = self.pil_sprites.get(sprite_name, self.pil_sprites["cat_neutral"])
        resized = base.resize((max(10, int(width)), max(10, int(height))), Image.Resampling.BILINEAR)
        photo = ImageTk.PhotoImage(resized)
        
        # Keep cache manageable
        if len(self._photo_cache) > 40:
            self._photo_cache.clear()
            
        self._photo_cache[key] = photo
        return photo

    def _animate(self):
        """Main rendering loop running at ~30 FPS."""
        self._frame_count += 1
        self.canvas.delete("all")
        
        energy = 0.0
        if self.get_audio_energy:
            try:
                energy = float(self.get_audio_energy())
            except Exception:
                energy = 0.0

        current_sprite = "cat_neutral"
        scale_w = 1.0
        scale_h = 1.0
        y_offset = 0.0
        
        # --- 1. LISTENING STATE (Cat jumps and hears with ear listening ripples) ---
        if self.state == self.STATE_LISTENING:
            # Jump cycle: speed up slightly if user is actively speaking
            speed = 0.22 + (energy * 0.12)
            self._jump_phase += speed
            
            # Jump height: jumps higher when sound is heard
            jump_h = 22.0 + (energy * 14.0)
            # Parabolic hop: absolute sine curve
            hop = abs(math.sin(self._jump_phase))
            y_offset = -int(jump_h * hop)
            
            # Squash & stretch physics
            if hop > 0.6:
                # In the air: stretch upwards
                scale_h = 1.0 + (0.08 * hop)
                scale_w = 1.0 - (0.05 * hop)
            elif hop < 0.25:
                # Landing squish
                squish = (0.25 - hop) / 0.25
                scale_h = 1.0 - (0.08 * squish)
                scale_w = 1.0 + (0.08 * squish)
                
            # Ear animation selection
            ear_cycle = int(self._frame_count // 4) % 4
            if ear_cycle == 0:
                current_sprite = "cat_ear_left"
            elif ear_cycle == 1:
                current_sprite = "cat_ear_both"
            elif ear_cycle == 2:
                current_sprite = "cat_ear_right"
            else:
                current_sprite = "cat_ear_both"
                
            # Render Ear Listening Sound Waves / Ripples!
            self._draw_ear_listening_waves(y_offset, energy)

        # --- 2. PROCESSING STATE (Head tilted, curious ears, thinking sparkles) ---
        elif self.state == self.STATE_PROCESSING:
            current_sprite = "cat_ear_both"
            # Gentle curious bob
            y_offset = -int(3.0 * math.sin(self._frame_count * 0.18))
            self._draw_thinking_dots(y_offset)

        # --- 3. SUCCESS STATE (Happy celebratory bounce & blushed eyes) ---
        elif self.state == self.STATE_SUCCESS:
            current_sprite = "cat_happy"
            # Cheerful quick bounce
            hop = abs(math.sin(self._frame_count * 0.35))
            y_offset = -int(16.0 * hop)
            scale_h = 1.0 + (0.05 * hop)
            scale_w = 1.0 - (0.04 * hop)
            self._draw_success_sparkles(y_offset)

        # --- 4. IDLE STATE (Gentle breathing & natural blinking) ---
        else:
            # Subtle breathing cycle (period ~3s)
            breath = math.sin(self._frame_count * 0.07) * 0.02
            scale_h = 1.0 + breath
            scale_w = 1.0 - (breath * 0.5)
            
            # Blink logic
            self._blink_counter += 1
            if self._is_blinking:
                current_sprite = "cat_blink"
                if self._blink_counter > 5:
                    self._is_blinking = False
                    self._blink_counter = 0
            else:
                current_sprite = "cat_neutral"
                # Blink roughly every 100-140 frames (~3-4.5 seconds)
                if self._blink_counter > 110 and random.random() < 0.15:
                    self._is_blinking = True
                    self._blink_counter = 0

        # Compute dynamic cat dimensions and position
        draw_w = int(self.base_cat_w * scale_w)
        draw_h = int(self.base_cat_h * scale_h)
        
        # Center horizontally, place feet firmly on ground baseline
        draw_x = self.center_x - (draw_w // 2)
        draw_y = int(self.ground_y - draw_h + y_offset)
        
        # Draw the Cat Sprite!
        photo = self._get_scaled_photo(current_sprite, draw_w, draw_h)
        self._current_photo = photo  # Prevent garbage collection
        self.canvas.create_image(draw_x, draw_y, anchor="nw", image=photo)
        
        # Schedule next animation frame (~33ms = 30 FPS)
        self.root.after(33, self._animate)

    def _draw_ear_listening_waves(self, y_offset, energy):
        """Draws animated listening sound ripples emitting outward from cat ears."""
        self._ear_wave_phase = (self._ear_wave_phase + 0.12) % 1.0
        
        # Ear tip coordinates relative to canvas center
        head_top_y = (self.ground_y - self.base_cat_h + y_offset)
        left_ear_x = self.center_x - 22
        right_ear_x = self.center_x + 22
        ear_y = head_top_y + 8
        
        # Colors: Glowing electric cyan / vibrant gold
        colors = ["#38bdf8", "#06b6d4", "#fbbf24"]
        
        # Draw 3 expanding acoustic ripple arcs from each ear
        for i in range(3):
            wave_prog = (self._ear_wave_phase + (i * 0.33)) % 1.0
            r = 6 + (wave_prog * 24)
            color = colors[i % len(colors)]
            width = max(1, int(3 * (1.0 - wave_prog)))
            
            # Left ear listening arc (curving up and to the left)
            self.canvas.create_arc(
                left_ear_x - r, ear_y - r, left_ear_x + r, ear_y + r,
                start=90, extent=130, style=tk.ARC,
                outline=color, width=width
            )
            
            # Right ear listening arc (curving up and to the right)
            self.canvas.create_arc(
                right_ear_x - r, ear_y - r, right_ear_x + r, ear_y + r,
                start=-40, extent=130, style=tk.ARC,
                outline=color, width=width
            )

    def _draw_thinking_dots(self, y_offset):
        """Draws cute glowing thinking dots above cat head."""
        head_top_y = (self.ground_y - self.base_cat_h + y_offset) - 6
        
        for i in range(3):
            dot_x = self.center_x - 14 + (i * 14)
            dot_y = head_top_y - int(4 * math.sin((self._frame_count * 0.25) + (i * 0.9)))
            self.canvas.create_oval(
                dot_x - 3, dot_y - 3, dot_x + 3, dot_y + 3,
                fill="#fbbf24", outline="#fef08a", width=1
            )

    def _draw_success_sparkles(self, y_offset):
        """Draws cheerful celebration music notes / sparkles."""
        head_top_y = (self.ground_y - self.base_cat_h + y_offset) - 8
        
        # Note 1 (left)
        n1_y = head_top_y - (self._frame_count % 18)
        self.canvas.create_text(
            self.center_x - 30, n1_y,
            text="♪", fill="#10b981", font=("Segoe UI", 12, "bold")
        )
        
        # Note 2 (right)
        n2_y = head_top_y - ((self._frame_count + 8) % 18)
        self.canvas.create_text(
            self.center_x + 30, n2_y,
            text="♫", fill="#34d399", font=("Segoe UI", 11, "bold")
        )

    def show_feedback(self, title, message, color="#38bdf8", auto_hide=3.5):
        """Displays status toast bubble beside the cat."""
        self.bubble.show(title, message, status_color=color, auto_hide_seconds=auto_hide)

    def _show_context_menu(self, event):
        """Right-click menu for controls, cheatsheet, and options."""
        menu = tk.Menu(self.root, tearoff=0, bg="#0f172a", fg="#f8fafc", activebackground="#0284c7", activeforeground="#ffffff")
        
        menu.add_command(label="🎙️ Start Listening", command=self.on_toggle_listen)
        menu.add_separator()
        menu.add_command(label="📋 Voice Commands Guide...", command=self._show_cheat_sheet)
        menu.add_command(label="👤 Chrome Profiles...", command=self._show_profiles_dialog)
        
        # Always on Top toggle
        settings = config.load_settings()
        topmost = settings.get("always_on_top", True)
        top_text = "✓ Always on Top" if topmost else "  Always on Top"
        menu.add_command(label=top_text, command=self._toggle_topmost)
        
        menu.add_separator()
        menu.add_command(label="❌ Exit Cat Listener", command=self.root.destroy)
        
        menu.post(event.x_root, event.y_root)

    def _toggle_topmost(self):
        settings = config.load_settings()
        cur = settings.get("always_on_top", True)
        settings["always_on_top"] = not cur
        config.save_settings(settings)
        self.root.attributes("-topmost", not cur)

    def _show_cheat_sheet(self):
        """Pops up voice command cheat sheet."""
        sheet = tk.Toplevel(self.root)
        sheet.title("Voice Commands Guide")
        sheet.geometry("450x420")
        sheet.configure(bg="#0f172a")
        sheet.attributes("-topmost", True)
        
        title = tk.Label(sheet, text="🐱 Desktop Cat Voice Commands", font=("Segoe UI", 12, "bold"), fg="#fbbf24", bg="#0f172a", pady=12)
        title.pack()
        
        commands_text = (
            "▶ YouTube Commands:\n"
            "  • 'open youtube' (opens standalone YouTube app window)\n"
            "  • 'search [query] on youtube'\n\n"
            "▶ Chrome & Profile Commands:\n"
            "  • 'open chrome and then click my profile'\n"
            "  • 'open chrome and click my profile'\n"
            "  • 'click my profile' / 'open my profile'\n"
            "  • 'open vit profile' / 'open college profile'\n\n"
            "▶ Apps & Navigation:\n"
            "  • 'open calculator', 'open notepad', 'open cmd'\n"
            "  • 'open github', 'open chatgpt', 'open reddit'\n"
            "  • 'search [query] on google'\n\n"
            "▶ System Controls:\n"
            "  • 'volume up', 'volume down', 'mute'\n"
            "  • 'take screenshot' (opens snipping tool)\n"
            "  • 'show desktop' / 'minimize all'\n\n"
            "💡 Tip: Click the cat anytime to have it jump and listen!"
        )
        
        msg = tk.Label(sheet, text=commands_text, font=("Consolas", 9), fg="#e2e8f0", bg="#0f172a", justify="left", padx=16)
        msg.pack(anchor="w")
        
        btn = tk.Button(sheet, text="Got it", bg="#0284c7", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=16, pady=4, command=sheet.destroy)
        btn.pack(pady=12)

    def _show_profiles_dialog(self):
        """Displays detected Chrome profiles."""
        profs = get_installed_chrome_profiles()
        dialog = tk.Toplevel(self.root)
        dialog.title("Detected Chrome Profiles")
        dialog.geometry("420x280")
        dialog.configure(bg="#0f172a")
        dialog.attributes("-topmost", True)
        
        tk.Label(dialog, text="👤 Detected Chrome Profiles", font=("Segoe UI", 11, "bold"), fg="#38bdf8", bg="#0f172a", pady=10).pack()
        
        txt = ""
        for dir_name, p in profs.items():
            txt += f"• [{dir_name}]: {p['name']}\n  Email: {p['email']}\n\n"
            
        lbl = tk.Label(dialog, text=txt, font=("Consolas", 9), fg="#cbd5e1", bg="#0f172a", justify="left", padx=16)
        lbl.pack(anchor="w")

    def run(self):
        """Starts Tkinter main loop."""
        self.root.mainloop()
