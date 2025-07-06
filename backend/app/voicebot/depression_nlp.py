from .stt import STT
from .tts import TTS
from .llm import LLMProcessor
import logging

logger = logging.getLogger(__name__)

class VoiceBot:
    def __init__(self):
        self.stt = STT()
        self.tts = TTS()
        self.llm = LLMProcessor()
        self.confidence = 0.5  # Initialize confidence to neutral by default
        logger.info("VoiceBot initialized successfully")

    def process_audio_for_depression(self, audio_path):
        try:
            transcription, error = self.stt.transcribe(audio_path)
            if not transcription:
                return False, 0.5, "Audio could not be understood.", b""  # Default confidence=0.5 on error
            
            result = self.llm.analyze_depression(transcription)
            audio_response = self.tts.text_to_speech(result["response"])
            
            # Return confidence from LLM analysis
            return result["is_depressed"], result["confidence"], result["response"], audio_response
        except Exception as e:
            return False, 0.5, "Error analyzing depression status.", b""  # confidence=0.5 on exception