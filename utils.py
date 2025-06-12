
import requests
import pygame
import webbrowser

pygame.mixer.init()

TELEGRAM_BOT_TOKEN = '7825544870:AAGRD3iSQxWzZmfTNuBgLMYRTBsCmGbboVs'
TELEGRAM_CHAT_ID = '719446998'

def send_telegram_message(bot_token, chat_id, msg):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {'chat_id': chat_id, 'text': msg}
    requests.post(url, data=data)

def play_local_sound(path):
    if path:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()

def open_cartoon_video(url):
    if url:
        webbrowser.open(url)

def send_file(bot_token, chat_id, file_path, caption=""):
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    with open(file_path, 'rb') as file:
        files = {'document': file}
        data = {'chat_id': chat_id, 'caption': caption}
        requests.post(url, files=files, data=data)

def send_photo(token, chat_id, photo_path, caption=None):
    if caption is None:
        caption = "📸 Alert screenshot"
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    with open(photo_path, 'rb') as photo:
        files = {'photo': photo}
        data = {'chat_id': chat_id, 'caption': caption}
        requests.post(url, files=files, data=data)
