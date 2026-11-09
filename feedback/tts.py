import os
import sys
import threading
import queue
import time
import winsound

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class TTSManager:
    """Non-blocking Windows text-to-speech speaker & audio cue manager."""
    
    def __init__(self):
        self._queue = queue.Queue()
        self._running = True
        self._worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self._worker_thread.start()
        
    def _speech_worker(self):
        """Worker loop initializing COM in its own thread."""
        try:
            import pythoncom
            pythoncom.CoInitialize()
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
        except Exception as e:
            print(f"[TTS] Warning: COM SAPI could not be initialized: {e}")
            speaker = None
            
        while self._running:
            try:
                text = self._queue.get(timeout=0.5)
                if text is None:
                    break
                    
                settings = config.load_settings()
                if settings.get("tts_enabled", True) and speaker:
                    try:
                        # SAPI Speak flags: 0 = Synchronous (inside worker thread)
                        speaker.Speak(text)
                    except Exception as err:
                        print(f"[TTS] Speech error: {err}")
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[TTS] Worker loop error: {e}")
                
        try:
            if 'pythoncom' in sys.modules:
                import pythoncom
                pythoncom.CoUninitialize()
        except Exception:
            pass

    def speak(self, text):
        """Queues text to be spoken asynchronously."""
        if not text:
            return
        settings = config.load_settings()
        if settings.get("tts_enabled", True):
            self._queue.put(text)

    def play_chime(self, cue_type="listen"):
        """Plays a brief, pleasing system chime."""
        settings = config.load_settings()
        if not settings.get("sound_cues", True):
            return
            
        def _beep():
            try:
                if cue_type == "listen":
                    # Rising cheerful double tone
                    winsound.Beep(988, 70)   # B5
                    winsound.Beep(1318, 90)  # E6
                elif cue_type == "success":
                    winsound.Beep(1046, 60)  # C6
                    winsound.Beep(1318, 60)  # E6
                    winsound.Beep(1568, 80)  # G6
                elif cue_type == "error":
                    winsound.Beep(440, 120)
                elif cue_type == "stop":
                    winsound.Beep(1046, 70)
                    winsound.Beep(784, 80)
            except Exception:
                pass
                
        threading.Thread(target=_beep, daemon=True).start()

    def stop(self):
        """Stops worker thread cleanly."""
        self._running = False
        self._queue.put(None)

# Global singleton
tts_engine = TTSManager()

if __name__ == "__main__":
    print("Testing TTS and Audio Chimes...")
    tts_engine.play_chime("listen")
    time.sleep(0.3)
    tts_engine.speak("Voice listener ready")
    time.sleep(2)
    tts_engine.play_chime("success")
    time.sleep(0.5)
    print("TTS test completed.")
