
import cv2
from datetime import datetime

def capture_screenshot(frame, emotion):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{emotion}_{timestamp}.jpg"
    path = f"screenshots/{filename}"
    cv2.imwrite(path, frame)
    return path
