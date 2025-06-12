import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def generate_weekly_emotion_summary(csv_path="emotion_log.csv", output_path="weekly_emotion_summary.png"):
    try:
        df = pd.read_csv(csv_path, parse_dates=["timestamp"])
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        df = df[df["timestamp"] >= week_ago]

        if df.empty:
            return None

        df["date"] = df["timestamp"].dt.date
        summary = df.groupby(["date", "emotion"]).size().unstack(fill_value=0)

        summary.plot(kind="bar", stacked=True, figsize=(10, 5))
        plt.title("Emotion Summary Over the Last 7 Days")
        plt.ylabel("Occurrences")
        plt.xlabel("Date")
        plt.tight_layout()
        plt.savefig(output_path)
        return output_path
    except Exception as e:
        print(f"[Error] Weekly summary generation: {e}")
        return None
