import datetime
import json
import os
import time
from pathlib import Path
from typing import Any

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from .analyzer import save_thumbnail
from .block_filters import is_suspicious_title
from .blocker import block_channel
from .history_cleaner import remove_video_from_history

THUMBNAIL_DIR = Path(__file__).parent.parent / "thumbnails"
LOG_PATH = Path(__file__).parent.parent / "blocked_channels.json"
SEEN_VIDEO_IDS: set[str] = set()

os.makedirs(THUMBNAIL_DIR, exist_ok=True)


def get_all_history_videos(driver: WebDriver) -> list[dict[str, str]]:
    """
    Extrahiert Videoinformationen aus dem YouTube-Verlauf.

    :param driver: Aktive Chrome WebDriver-Instanz
    :return: Liste von Video-Dictionaries mit Titel, Video-ID, Channel-Name, Channel-URL
    """
    videos = []
    containers = driver.find_elements(By.TAG_NAME, "ytd-video-renderer")

    for container in containers:
        try:
            title_element = container.find_element(By.ID, "video-title")
            title = title_element.text.strip()
            url = title_element.get_attribute("href")
            video_id = url.split("v=")[-1].split("&")[0]

            channel_element = container.find_element(By.CSS_SELECTOR, "#channel-name a")
            channel_name = channel_element.text.strip()
            channel_url = channel_element.get_attribute("href")

            videos.append({
                "title": title,
                "video_id": video_id,
                "channel_name": channel_name,
                "channel_url": channel_url
            })
        except Exception:
            continue

    return videos


def countdown(seconds: int, label: str = "Wiederholung") -> None:
    """
    Führt einen Countdown mit optionalem Label aus (z. B. zur Warteschleife).

    :param seconds: Anzahl der Sekunden
    :param label: Beschreibung für den Countdown
    """
    for remaining in range(seconds, 0, -1):
        print(f"[{label}] {remaining} Sekunden verbleiben...", end="\r")
        time.sleep(1)
    print(" " * 50, end="\r")


def handle_suspicious_video(driver: WebDriver, video: dict[str, Any]) -> None:
    """
    Behandelt verdächtige Videos: Thumbnail speichern, Kanal blockieren, Verlauf bereinigen.

    :param driver: Aktive Chrome WebDriver-Instanz
    :param video: Dictionary mit Video-Daten
    """
    video_id = video["video_id"]
    title = video["title"]
    channel_name = video["channel_name"]

    print(f"[⚠️  BLOCK] Verdächtiges Video erkannt → Kanal: {channel_name}")

    thumbnail_path = THUMBNAIL_DIR / f"{video_id}.jpg"
    save_thumbnail(video_id, thumbnail_path)
    print(f"[🖼️ ] Thumbnail gespeichert: {thumbnail_path.name}")

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "channel_name": channel_name,
            "channel_url": video["channel_url"],
            "video_title": title,
            "video_id": video_id,
            "log_time": datetime.datetime.now().isoformat()
        }, ensure_ascii=False) + "\n")

    block_channel(driver, video["channel_url"])
    print(f"[📛] Kanal blockiert: {channel_name}")
    time.sleep(3)

    remove_video_from_history(driver, video_id)
    countdown(15)


def check_history_once(driver: WebDriver) -> None:
    """
    Durchsucht den YouTube-Verlauf einmalig und behandelt verdächtige Videos.

    :param driver: Aktive Chrome WebDriver-Instanz
    """
    driver.get("https://www.youtube.com/feed/history")
    time.sleep(3)

    print("[⏳] Lese Videos aus Verlauf...")
    videos = get_all_history_videos(driver)

    for video in videos:
        video_id = video["video_id"]
        title = video["title"]

        if video_id in SEEN_VIDEO_IDS:
            continue

        SEEN_VIDEO_IDS.add(video_id)
        print(f"[🔍] Prüfe Titel: {title}")

        if is_suspicious_title(title):
            handle_suspicious_video(driver, video)
        else:
            print("[✅] War kein Trash – alles in Ordnung")

    countdown(30)
