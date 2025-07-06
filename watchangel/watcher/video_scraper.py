import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver

from watchangel.utils.scrolling import scroll_to_end


def get_all_history_videos(driver: WebDriver, max_scrolls: int = 25) -> list[dict[str, str]]:
    """
    Scrollt durch den YouTube-Verlauf und extrahiert alle sichtbaren Videos.
    """
    driver.get("https://www.youtube.com/feed/history")
    scroll_to_end(driver, max_scrolls)

    # Nach dem Scrollen alle Videoelemente auslesen
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

def get_recent_history_videos(driver: WebDriver) -> list[dict[str, str]]:
    """
    Gibt nur die obersten Verlaufseinträge zurück (≈ 30 Videos).

    Wird im WatchLoop verwendet, da ältere Videos bereits gesäubert wurden.
    """
    return get_all_history_videos(driver, max_scrolls=1)
