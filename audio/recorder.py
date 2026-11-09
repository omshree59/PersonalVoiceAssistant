import os
import sys
import time
import io
import wave
import threading
import numpy as np
import sounddevice as sd
import speech_recognition as sr

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class AudioRecorder:
    """Microphone audio recorder with automatic voice activity and silence detection."""
    
    def __init__(self):
        self.is_recording = False
        self._frames = []
        self._stream = None
        self._stop_event = threading.Event()
        self.has_speech_started = False
        self.silence_start_time = None
        self.current_energy = 0.0
        self.is_speaking_now = False
        
    def _audio_callback(self, indata, frames, time_info, status):
        """Streaming callback receiving 16kHz audio chunks."""
        if not self.is_recording:
            self.current_energy = 0.0
            self.is_speaking_now = False
            return
            
        chunk = indata.copy()
        self._frames.append(chunk)
        
        # Calculate RMS energy for Voice Activity Detection
        rms = np.sqrt(np.mean(chunk**2))
        settings = config.load_settings()
        threshold = settings.get("silence_threshold", 0.015)
        silence_limit = settings.get("silence_duration_seconds", 1.2)
        
        # Real-time responsiveness indicator
        self.current_energy = float(np.clip(rms * 18.0, 0.0, 1.0))
        
        if rms > threshold:
            self.has_speech_started = True
            self.is_speaking_now = True
            self.silence_start_time = None
        else:
            self.is_speaking_now = False
            if self.has_speech_started:
                if self.silence_start_time is None:
                    self.silence_start_time = time.time()
                elif (time.time() - self.silence_start_time) >= silence_limit:
                    # User stopped talking; auto-stop recording
                    self._stop_event.set()

    def record_speech(self, on_speech_start=None, timeout=None):
        """
        Records speech until silence is detected or timeout is reached.
        Returns speech_recognition.AudioData or None if cancelled/empty.
        """
        settings = config.load_settings()
        sample_rate = settings.get("sample_rate", 16000)
        max_duration = timeout or settings.get("max_listen_seconds", 9.0)
        
        self._frames = []
        self._stop_event.clear()
        self.has_speech_started = False
        self.silence_start_time = None
        self.is_recording = True
        
        start_wall_time = time.time()
        
        try:
            with sd.InputStream(
                samplerate=sample_rate,
                channels=1,
                dtype="float32",
                blocksize=1024,
                callback=self._audio_callback
            ):
                while self.is_recording and not self._stop_event.is_set():
                    # Check overall timeout
                    if (time.time() - start_wall_time) > max_duration:
                        break
                    time.sleep(0.04)
        except Exception as e:
            print(f"[Recorder] Recording stream error: {e}")
            self.is_recording = False
            return None
            
        self.is_recording = False
        
        if not self._frames:
            return None
            
        # Combine chunks
        audio_data = np.concatenate(self._frames, axis=0)
        
        # Check if minimum audio was captured
        if len(audio_data) < sample_rate * 0.4:
            return None
            
        # Convert float32 [-1.0, 1.0] to int16 PCM
        int16_data = np.clip(audio_data * 32767, -32768, 32767).astype(np.int16)
        
        # Package into standard speech_recognition.AudioData
        raw_bytes = int16_data.tobytes()
        return sr.AudioData(raw_bytes, sample_rate, 2)

    def stop(self):
        """Explicitly stops recording."""
        self.is_recording = False
        self._stop_event.set()
