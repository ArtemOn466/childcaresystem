
import time
import datetime
import threading
import requests
from report import generate_daily_report
from report_weekly import generate_weekly_emotion_summary
from utils import send_file, send_photo, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
STREAM_URL = "http://localhost:5000/video"  # Замінити на ngrok або реальний IP для віддаленого доступу

def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {'timeout': 100, 'offset': offset}
    response = requests.get(url, params=params)
    return response.json()

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    data = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=data)

def auto_send_report():
    while True:
        now = datetime.datetime.now()
        if now.hour == 20 and now.minute == 0:
            report = generate_daily_report()
            send_message(TELEGRAM_CHAT_ID, "🕗 Автоматичний звіт о 20:00:" + report)
            send_file(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, "emotion_log.csv", "📄 CSV звіт")
            time.sleep(60)
        time.sleep(10)

def main():
    offset = None
    print("🤖 Telegram bot polling started.")
    threading.Thread(target=auto_send_report, daemon=True).start()

    while True:
        updates = get_updates(offset)
        if "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"]["text"].lower()

                    if text == "/report":
                        report = generate_daily_report()
                        send_message(chat_id, "🧾 Щоденний звіт:" + report)
                        send_file(TELEGRAM_BOT_TOKEN, chat_id, "emotion_log.csv", "📄 CSV звіт")
                    elif text == "/weekly":
                        send_file(TELEGRAM_BOT_TOKEN, chat_id, "emotion_log.csv", "📁 Дані за 7 днів")
                    elif text == "/weekly_graphic":
                        image_path = generate_weekly_emotion_summary("emotion_log.csv", "weekly_emotion_summary.png")
                        if image_path:
                            send_photo(TELEGRAM_BOT_TOKEN, chat_id, image_path, caption="📊 Weekly Emotion Report")
                        else:
                            send_message(chat_id, "📭 No data for the last 7 days.")

                    elif text == "/stream":
                        send_message(chat_id, f"🎥 Live stream: {STREAM_URL}")
        time.sleep(1)

if __name__ == "__main__":
    main()
