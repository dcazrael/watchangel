import json
import time
from pathlib import Path
from selenium.webdriver.chrome.webdriver import WebDriver
from .video_scraper import get_all_history_videos
from .video_checker import is_video_blockworthy
from .video_handler import handle_suspicious_video
from ..history.cleaner import remove_all_from_channel
from ..rules.block_rules import BlockRuleEngine

SEEN_VIDEO_IDS: set[str] = set()


def countdown(seconds: int, label: str = "Wiederholung") -> None:
    for remaining in range(seconds, 0, -1):
        print(f"[{label}] {remaining} Sekunden verbleiben...", end="\r")
        time.sleep(1)
    print(" " * 50, end="\r")


def check_history_once(driver: WebDriver) -> None:
    driver.get("https://www.youtube.com/feed/history")
    time.sleep(3)

    print("[⏳] Lese Videos aus Verlauf...")
    videos = get_all_history_videos(driver)

    engine = BlockRuleEngine.from_logs()
    already_blocked = engine.blocked_channels  # ⬅️ bereinigt um undo_channels

    for video in videos:
        video_id = video["video_id"]
        title = video["title"]
        channel_name = video["channel_name"].strip()

        if video_id in SEEN_VIDEO_IDS:
            continue

        SEEN_VIDEO_IDS.add(video_id)

        if channel_name.lower() in already_blocked:
            print(f"[♻️] Kanal bereits blockiert: {channel_name} → Verlauf bereinigen")
            remove_all_from_channel(driver, video_id)
            continue

        print(f"[🔍] Prüfe Titel: {title}")

        if is_video_blockworthy(title, channel_name):
            handle_suspicious_video(driver, video)
            already_blocked.add(channel_name.lower())  # Nur lowercase speichern
        else:
            print("[✅] War kein Trash – alles in Ordnung")

    countdown(10)
