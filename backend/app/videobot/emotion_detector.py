import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from config import FACE_MODEL_PATH  # Add this import at the top

class EmotionDetector:
    def __init__(self):
        self.model = load_model(FACE_MODEL_PATH)  # Use from config.py
        self.class_names = ['Angry', 'Disgusted', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def detect_emotion(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        
        if len(faces) == 0:
            return "neutral"
        
        (x, y, w, h) = faces[0]  # Process only the first face
        face_roi = frame[y:y+h, x:x+w]
        
        # Preprocess for model
        face_img = cv2.resize(face_roi, (48, 48))
        face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        face_img = image.img_to_array(face_img)
        face_img = np.expand_dims(face_img, axis=0)
        
        predictions = self.model.predict(face_img)
        return self.class_names[np.argmax(predictions)].lower()  # Match your existing emotion format