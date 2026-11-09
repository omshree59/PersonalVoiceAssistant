import os
import sys

if sys.platform == "win32":
    try:
        if sys.stdout is not None:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr is not None:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import threading
import time

# Ensure project root is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import config
from audio.recorder import AudioRecorder
from audio.recognizer import transcriber
from automation.command_parser import parse_and_execute
from feedback.tts import tts_engine
from gui.floating_widget import FloatingWidget
from single_instance import SingleInstanceManager

class VoiceListenerApp:
    """Main Application Controller for the Desktop Voice Listener."""
    
    def __init__(self):
        # Enforce single instance: if another instance is launched, it wakes us up and exits
        self.single_instance = SingleInstanceManager(on_activate=self._on_remote_activate)
        self.single_instance.acquire_lock_or_wake_existing()
        
        self.recorder = AudioRecorder()
        self.widget = FloatingWidget(
            on_toggle_listen=self.toggle_listening,
            get_audio_energy=lambda: self.recorder.current_energy
        )
        self.listen_thread = None
        self._is_active = False

    def _on_remote_activate(self):
        """Called when user launches the app while it is already running."""
        print("[App] Wake-up ping received from secondary launch attempt.")
        self.widget.root.after(0, lambda: self.widget.show_in_bottom_right(smooth_wake=True))

    def toggle_listening(self):
        """Toggles between listening mode and idle."""
        if self._is_active:
            # Stop listening if clicked while active
            self.stop_listening()
        else:
            self.start_listening()

    def start_listening(self):
        """Activates listening state and starts audio capture in a background thread."""
        if self._is_active:
            return
            
        self._is_active = True
        self.widget.set_state(FloatingWidget.STATE_LISTENING)
        self.widget.show_feedback("🎙️ Listening...", "Speak now (e.g. 'open youtube', 'open chrome and click my profile')", color="#f87171", auto_hide=0)
        tts_engine.play_chime("listen")
        
        self.listen_thread = threading.Thread(target=self._listen_worker, daemon=True)
        self.listen_thread.start()

    def stop_listening(self):
        """Signals recorder to stop."""
        self.recorder.stop()
        self._is_active = False

    def _listen_worker(self):
        """Background worker recording and processing voice input."""
        try:
            # Capture speech with auto-silence detection
            audio_data = self.recorder.record_speech()
            self._is_active = False
            
            # Switch UI to Processing state
            self.widget.root.after(0, lambda: self.widget.set_state(FloatingWidget.STATE_PROCESSING))
            self.widget.root.after(0, lambda: self.widget.show_feedback("⏳ Processing...", "Transcribing speech...", color="#fbbf24", auto_hide=0))
            
            if audio_data is None:
                self.widget.root.after(0, lambda: self.widget.set_state(FloatingWidget.STATE_IDLE))
                self.widget.root.after(0, lambda: self.widget.show_feedback("🔇 Idle", "No speech detected.", color="#94a3b8", auto_hide=2.5))
                tts_engine.play_chime("stop")
                return
                
            # Transcribe audio
            transcript = transcriber.transcribe(audio_data)
            
            if not transcript or not transcript.strip():
                self.widget.root.after(0, lambda: self.widget.set_state(FloatingWidget.STATE_IDLE))
                self.widget.root.after(0, lambda: self.widget.show_feedback("❓ Unclear", "Could not understand audio. Please try again.", color="#fbbf24", auto_hide=3.0))
                tts_engine.play_chime("stop")
                return
                
            print(f"[VoiceListener] Recognized: '{transcript}'")

            # Commands run quietly. Only greetings and small talk are spoken back.
            result = parse_and_execute(transcript)
            reply = result.get("speak")
            bubble = result.get("text") or ""

            if reply:
                tts_engine.speak(reply)

            if bubble:
                color = "#10b981" if result.get("ok") else "#fbbf24"
                title = result.get("title") or ("Assistant" if reply else "Note")
                self.widget.root.after(
                    0,
                    lambda c=color, t=title, b=bubble: self.widget.show_feedback(t, b, color=c, auto_hide=4.0)
                )
                self.widget.root.after(
                    0,
                    lambda: self.widget.set_state(
                        FloatingWidget.STATE_SUCCESS if result.get("ok") else FloatingWidget.STATE_IDLE
                    )
                )
                if not result.get("ok"):
                    tts_engine.play_chime("error")
            elif result.get("ok"):
                # Action succeeded: no toast and no voice repeating the command.
                self.widget.root.after(0, lambda: self.widget.set_state(FloatingWidget.STATE_SUCCESS))
            else:
                self.widget.root.after(0, lambda: self.widget.set_state(FloatingWidget.STATE_IDLE))
                tts_engine.play_chime("error")

            time.sleep(1.2 if reply else 0.6)
            self.widget.root.after(0, lambda: self.widget.set_state(FloatingWidget.STATE_IDLE))
            
        except Exception as e:
            print(f"[VoiceListener] Error in listen worker: {e}")
            self.widget.root.after(0, lambda: self.widget.set_state(FloatingWidget.STATE_IDLE))
            self.widget.root.after(0, lambda: self.widget.show_feedback("⚠️ Error", str(e), color="#ef4444", auto_hide=3.5))
            tts_engine.play_chime("error")

    def run(self):
        """Starts the application."""
        print("=" * 60)
        print("  [Cat] DESKTOP CAT VOICE LISTENER")
        print("  Click the cat anytime to have it jump and listen.")
        print("  Right-click the cat for commands guide & options.")
        print("=" * 60)
        
        # Initial greeting toast
        self.widget.root.after(
            400,
            lambda: self.widget.show_feedback(
                "🐱 Cat Listener Ready!",
                "Click me anytime to give a command!",
                color="#fbbf24",
                auto_hide=4.0
            )
        )
        self.widget.run()

if __name__ == "__main__":
    app = VoiceListenerApp()
    app.run()
