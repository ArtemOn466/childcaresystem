
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

LOG_PATH = "emotion_log.csv"

def log_emotion_to_csv(emotion, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now()
    df = pd.DataFrame([[timestamp.strftime("%Y-%m-%d %H:%M:%S"), emotion]], columns=["timestamp", "emotion"])
    df.to_csv(LOG_PATH, mode='a', header=not Path(LOG_PATH).exists(), index=False)

def generate_daily_report(csv_path="emotion_log.csv"):
    try:
        df = pd.read_csv(csv_path, parse_dates=["timestamp"])
        today = datetime.now().date()
        df = df[df["timestamp"].dt.date == today]

        if df.empty:
            return "📭 No emotion data for today."

        emotion_counts = df["emotion"].value_counts()
        total = emotion_counts.sum()

        report_lines = [f"📊 Emotion Report for {today}:"]
        for emotion, count in emotion_counts.items():
            percentage = (count / total) * 100
            report_lines.append(f"- {emotion}: {count} times ({percentage:.1f}%)")

        return "\n".join(report_lines)
    except Exception as e:
        return f"⚠️ Error generating report: {e}"


def get_last_24h_log():
    try:
        df = pd.read_csv(LOG_PATH, parse_dates=["timestamp"])
        now = datetime.now()
        day_ago = now - timedelta(hours=24)
        df_24h = df[df["timestamp"] >= day_ago]
        if df_24h.empty:
            return "⏱️ No emotion data in the last 24 hours."
        return "\n".join([f"{row['timestamp']} — {row['emotion']}" for _, row in df_24h.iterrows()])
    except Exception as e:
        return f"Error reading log: {e}"
