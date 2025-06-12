
import threading
import subprocess
import time

def run_emotion_detector():
    subprocess.run(["python", "emotion_detector.py"])

def run_video_streamer():
    subprocess.run(["python", "video_streamer.py"])

def run_telegram_bot():
    subprocess.run(["python", "telegram_bot_polling.py"])

if __name__ == "__main__":
    print("🚀 Starting Emotion Monitoring System...")

    t1 = threading.Thread(target=run_emotion_detector)
    t2 = threading.Thread(target=run_video_streamer)
    t3 = threading.Thread(target=run_telegram_bot)

    t1.start()
    time.sleep(2)  # Невелика пауза для стабільності
    t2.start()
    time.sleep(2)
    t3.start()

    t1.join()
    t2.join()
    t3.join()
