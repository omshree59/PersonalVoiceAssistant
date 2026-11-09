import os
import sys
import speech_recognition as sr

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class SpeechTranscriber:
    """Handles speech-to-text conversion."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Tuning parameters for speech recognition
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        
    def transcribe(self, audio_data):
        """
        Transcribes speech_recognition.AudioData into text.
        Returns the recognized string, or empty string on error/silence.
        """
        if audio_data is None:
            return ""
            
        settings = config.load_settings()
        engine = settings.get("speech_engine", "hybrid").lower()
        
        # Primary recognition path
        try:
            # Google Web Speech API - fast, accurate, no keys needed
            text = self.recognizer.recognize_google(audio_data, language="en-US")
            return text.strip()
        except sr.UnknownValueError:
            print("[Recognizer] Speech was unintelligible.")
            return ""
        except sr.RequestError as e:
            print(f"[Recognizer] Network request failed ({e}); attempting local fallback...")
            return self._fallback_local(audio_data)
        except Exception as ex:
            print(f"[Recognizer] Transcription error: {ex}")
            return ""
            
    def _fallback_local(self, audio_data):
        """Attempts offline transcription if network is unreachable."""
        try:
            import vosk
            return self.recognizer.recognize_vosk(audio_data)
        except Exception as e:
            print(f"[Recognizer] Offline fallback error: {e}")
            return ""

# Global instance
transcriber = SpeechTranscriber()
