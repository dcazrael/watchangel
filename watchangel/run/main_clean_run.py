from selenium.webdriver.chrome.webdriver import WebDriver

from watchangel.model.scanned_video import ScannedVideo
from watchangel.analysis.scanner import scan_watch_history
from watchangel.cleaner.batch_cleaner import clean_matched_videos
from watchangel.model.matched_video import MatchedVideo
from watchangel.matching.matching import match_video
from watchangel.rules.block_rules import BlockRuleEngine


def run_cleanup_pipeline(driver: WebDriver) -> int:
    """
    Führt den kompletten Cleaning-Flow aus:
    1. Verlauf wird gescannt
    2. Alle Videos werden bewertet
    3. Blockierte Videos werden entfernt

    :param driver: Aktive WebDriver-Instanz
    :return: Anzahl gelöschter Videos
    """
    print("[🚀] Starte vollständige Verlauf-Bereinigung...")

    videos: list[ScannedVideo] = scan_watch_history(driver)
    print(f"[📦] {len(videos)} Videos im Verlauf gefunden.")

    rules = BlockRuleEngine.from_logs()

    seen_ids: set[str] = set()
    matches: list[MatchedVideo] = []

    for video in videos:
        if video.video_id in seen_ids:
            continue
        seen_ids.add(video.video_id)

        match = match_video(video, rules)
        if match:
            matches.append(match)

    print(f"[⚖️] {len(matches)} blockwürdige Videos erkannt.")

    return clean_matched_videos(driver, matches)
