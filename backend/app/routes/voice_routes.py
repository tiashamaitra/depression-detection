from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.logger import logger
import tempfile
import os
import base64
import json
from app.voicebot.depression_nlp import VoiceBot

router = APIRouter()
voice_bot = VoiceBot()

@router.websocket("/ws/conversation/{session_id}")
async def websocket_conversation(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connected for session: {session_id}")
    
    while True:
        try:
            data = await websocket.receive_json()
            logger.info(f"Received WebSocket message: {data.get('type')}")
            
            if data.get("type") == "audio":
                transcription = data.get("transcription", "")
                logger.info(f"User said: '{transcription}'")
                
                # Save audio to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                    wav_path = tmpfile.name
                
                decoded_audio = base64.b64decode(data.get("audio", ""))
                if not decoded_audio:
                    logger.warning("No audio data received")
                    continue
                
                with open(wav_path, "wb") as f:
                    f.write(decoded_audio)
                
                # Process audio
                is_depressed, confidence, response_text, audio_response = voice_bot.process_audio_for_depression(wav_path)
                os.unlink(wav_path)
                
                if audio_response:
                    await websocket.send_json({
                        "type": "ai_response",
                        "text_response": response_text,
                        "audio_response": base64.b64encode(audio_response).decode(),
                        "is_depressed": is_depressed,
                        "confidence_score": confidence,
                        "transcription": transcription
                    })
                else:
                    await websocket.send_json({
                        "type": "transcription_failed",
                        "message": "Could not understand the audio. Please speak clearly and try again."
                    })
                    
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for session: {session_id}")
            break
        except Exception as e:
            logger.error(f"WebSocket error: {e}", exc_info=True)
            await websocket.send_json({"type": "error", "message": "Internal server error"})