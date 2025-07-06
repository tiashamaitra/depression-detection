def calculate_depression_score(is_voice_depressed: bool, dominant_emotion: str):
    voice_score = 1 if is_voice_depressed else 0
    video_score = 1 if dominant_emotion in ["sad", "fear", "angry"] else 0
    total_score = voice_score * 0.7 + video_score * 0.3
    return round(total_score, 2)