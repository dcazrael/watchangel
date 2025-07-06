import datetime
import json
import time
from pathlib import Path
from selenium.webdriver.chrome.webdriver import WebDriver

from watchangel.analysis.analyzer import save_thumbnail, extract_video_id
from watchangel.blocker.actions import block_channel
from watchangel.utils.paths import log_path
from watchangel.cleaner.cleaner import remove_all_from_channel

THUMBNAIL_DIR = Path(__file__).parent.parent.parent / "thumbnails"
LOG_PATH = Path(__file__).parent.parent.parent / "blocked_channels.log"
THUMBNAIL_DIR.mkdir(exist_ok=True)


def handle_suspicious_video(driver: WebDriver, video: dict) -> None:
    video_id = extract_video_id(video["video_id"])
    title = video["title"]
    channel_name = video["channel_name"]

    print(f"[⚠️  BLOCK] Verdächtiges Video erkannt → Kanal: {channel_name}")

    thumbnail_path = THUMBNAIL_DIR / f"{video_id}.jpg"
    save_thumbnail(video_id, thumbnail_path)
    print(f"[🖼️ ] Thumbnail gespeichert: {thumbnail_path.name}")

    log_block_action(video)
    block_channel(driver, video["channel_url"])
    print(f"[📛] Kanal blockiert: {channel_name}")
    time.sleep(3)

    remove_all_from_channel(driver, video_id)


def log_block_action(video: dict) -> None:
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "channel_name": video["channel_name"],
            "channel_url": video["channel_url"],
            "video_title": video["title"],
            "video_id": video["video_id"],
            "log_time": datetime.datetime.now().isoformat()
        }, ensure_ascii=False) + "\n")
