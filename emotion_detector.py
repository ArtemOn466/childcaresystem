import cv2
import time
import pandas as pd
from deepface import DeepFace
from datetime import datetime
import mediapipe as mp
from report import log_emotion_to_csv, generate_daily_report
from utils import send_telegram_message, play_local_sound, open_cartoon_video
from screenshot_utils import capture_screenshot
from utils import send_photo, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# === CONFIG ===
reaction_threshold = 5
cooldown_period = 5

emotion_sounds = {
    "happy": "sounds/Pharrell Williams - Happy.mp3",
    "sad": "sounds/Marconi Union - Weightless (Official Video).mp3",
    "angry": "sounds/Marconi Union - Weightless (Official Video).mp3",
    "fear": "sounds/Marconi Union - Weightless (Official Video).mp3",
    "crying": "sounds/Marconi Union - Weightless (Official Video).mp3",
    "surprise_positive": "sounds/joyful_surprise.mp3",
    "surprise_negative": "sounds/alert.mp3",
    "surprise_neutral": None
}

emotion_videos = {
    "happy": "",
    "surprise_positive": "https://youtu.be/Ho5bQFMwT9Y?t=10",
    "surprise_negative": "https://www.youtube.com/watch?v=fzQ6gRAEoy0",
    "crying": "https://www.youtube.com/watch?v=tgbNymZ7vqY"
}

emotion_keys = [
    "happy", "sad", "angry", "fear", "crying",
    "surprise_positive", "surprise_negative", "surprise_neutral"
]

emotion_state = {
    key: {
        "start_time": None,
        "notified": False,
        "last_notify_time": 0,
        "video_played": False,
        "logged": False
    } for key in emotion_keys
}

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

def detect_crying(face_roi):
    results = face_mesh.process(cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB))
    if results.multi_face_landmarks:
        for landmarks in results.multi_face_landmarks:
            top = landmarks.landmark[13].y
            bottom = landmarks.landmark[14].y
            return (bottom - top) > 0.03
    return False

def classify_surprise(face_roi):
    results = face_mesh.process(cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB))
    if not results.multi_face_landmarks:
        return "neutral"
    landmarks = results.multi_face_landmarks[0].landmark
    brow_left = landmarks[65].y
    eye_left = landmarks[159].y
    mouth_top = landmarks[13].y
    mouth_bottom = landmarks[14].y
    lip_distance = mouth_bottom - mouth_top
    brow_eye_dist = eye_left - brow_left
    if brow_eye_dist > 0.015 and lip_distance > 0.03:
        return "positive"
    elif brow_eye_dist > 0.015:
        return "neutral"
    else:
        return "negative"

def main():
    print("🟢 Starting camera capture...")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    print("Emotion & surprise classifier running...")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        for (x, y, w, h) in faces:
            roi = frame[y:y + h, x:x + w]
            try:
                result = DeepFace.analyze(roi, actions=['emotion'], enforce_detection=False)
                emotion = result[0]['dominant_emotion']
                current_time = time.time()
                crying = emotion in ['sad', 'angry'] and detect_crying(roi)
                if emotion == 'surprise':
                    subtype = classify_surprise(roi)
                    actual_emotion = f"surprise_{subtype}"
                else:
                    actual_emotion = "crying" if crying else emotion
                for emo in emotion_state:
                    active = actual_emotion == emo
                    if active:
                        if emotion_state[emo]["start_time"] is None:
                            emotion_state[emo]["start_time"] = current_time
                        if not emotion_state[emo]["logged"] and (current_time - emotion_state[emo]["start_time"] >= 10):
                                log_emotion_to_csv(emo)
                                emotion_state[emo]["logged"] = True

                        if not emotion_state[emo]["notified"] and (current_time - emotion_state[emo]["start_time"] >= reaction_threshold):
                            if current_time - emotion_state[emo]["start_time"] >= 10:
                                send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, f"📢 Emotion: '{emo}' > 10s.")
                                play_local_sound(emotion_sounds.get(emo))
                                if not emotion_state[emo]['video_played']:
                                    open_cartoon_video(emotion_videos.get(emo))
                                    emotion_state[emo]['video_played'] = True
                                emotion_state[emo]["notified"] = True
                                if not emotion_state[emo]["logged"]:
                                    log_emotion_to_csv(emo)
                                    emotion_state[emo]["logged"] = True
                                emotion_state[emo]["last_notify_time"] = current_time
                            if current_time - emotion_state[emo]["start_time"] >= 5:
                                if actual_emotion in ["fear", "crying"]:
                                    screenshot_path = capture_screenshot(frame, actual_emotion)
                                    send_photo(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, screenshot_path, f"⚠️ Alert: {actual_emotion.upper()}")
                    else:
                        emotion_state[emo]["start_time"] = None
                        emotion_state[emo]["logged"] = False
                        if emotion_state[emo]["notified"] and (current_time - emotion_state[emo].get("last_notify_time", 0)) > cooldown_period:
                            emotion_state[emo]["notified"] = False
                            emotion_state[emo]["video_played"] = False
                            emotion_state[emo]["start_time"] = None
                        emotion_state[emo]["logged"] = False
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, actual_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)
            except Exception as e:
                print(f"DeepFace error: {e}")
        cv2.imshow('Emotion Response', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
