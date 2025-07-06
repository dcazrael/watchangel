import time
from typing import Set
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException

from watchangel.model.scanned_video import ScannedVideo
from watchangel.utils.scrolling import scroll_to_end


def scan_watch_history(driver: WebDriver) -> list[ScannedVideo]:
    """
    Scrollt durch den Verlauf und extrahiert alle Videos.
    """
    driver.get("https://www.youtube.com/feed/history")
    time.sleep(2)

    scroll_to_end(driver)  # zentrale Scroll-Logik
    blocks = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")

    seen: Set[str] = set()
    videos: list[ScannedVideo] = []

    for block in blocks:
        key = block.get_attribute("outerHTML")
        if key in seen:
            continue
        seen.add(key)

        video = _extract_video_metadata(block)
        if video:
            videos.append(video)

    print(f"[📦] {len(videos)} Videos erfasst.")
    return videos


def _extract_video_metadata(block: WebElement) -> ScannedVideo | None:
    """
    Extrahiert die Metadaten aus einem einzelnen Video-Block.

    :param block: DOM-Element des Videos
    :return: ScannedVideo-Objekt oder None
    """
    try:
        title_el = block.find_element(By.CSS_SELECTOR, "#video-title")
        title = title_el.text.strip()

        channel_el = block.find_element(By.CSS_SELECTOR, "ytd-channel-name a")
        channel_name = channel_el.text.strip()

        hrefs = block.find_elements(By.CSS_SELECTOR, "a#thumbnail")
        video_id = None
        url: str | None = None
        for href in hrefs:
            url = href.get_attribute("href")
            if url and "watch?v=" in url:
                video_id = url.split("watch?v=")[-1].split("&")[0]
                break

        if not video_id:
            return None

        return ScannedVideo(
            title=title,
            channel_name=channel_name,
            channel_url=url,
            video_id=video_id,
            element=block,
        )
    except NoSuchElementException:
        return None
