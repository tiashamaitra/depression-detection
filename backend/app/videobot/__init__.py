def __init__(self):
    self.emotion_detector = EmotionDetector()
    self.emotion_history = []
    self.running = False
    self.cap = None
    self.camera_index = 0
    self.thread = None
    self.effective_duration = self.MAX_DURATION