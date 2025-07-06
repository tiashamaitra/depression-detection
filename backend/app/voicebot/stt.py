import whisper
import logging
import os
import wave
import numpy as np
import librosa
import base64
from pathlib import Path

logger = logging.getLogger(__name__)

class STT:
    def __init__(self):
        self.model = whisper.load_model("base")
        logger.info("Initializing Speech-to-Text engine...")

    def validate_audio_file(self, audio_path):
        if not os.path.exists(audio_path):
            return False, "Audio file does not exist"
        
        file_size = os.path.getsize(audio_path)
        if file_size == 0:
            return False, "Audio file is empty"

        try:
            with wave.open(audio_path, 'rb') as wav_file:
                params = wav_file.getparams()
                duration = wav_file.getnframes() / wav_file.getframerate()
                if duration < 0.5:
                    return False, f"Audio too short: {duration:.2f}s"
        except Exception as e:
            return False, f"Invalid WAV file: {e}"

        return True, ""

    def transcribe(self, audio_path):
        logger.info(f"Starting transcription for file: {audio_path}")
        is_valid, msg = self.validate_audio_file(audio_path)
        if not is_valid:
            logger.warning(f"Validation failed: {msg}")
            return "", msg

        result = self.model.transcribe(
            audio_path,
            language="en",
            task="transcribe",
            fp16=False,
            verbose=False
        )
        transcription = result["text"].strip()

        if not transcription:
            logger.warning("Whisper returned empty transcription")
            return "", "No speech detected"

        logger.info(f"Transcription successful: '{transcription}'")
        return transcription, None