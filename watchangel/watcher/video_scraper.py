from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver


def get_all_history_videos(driver: WebDriver) -> list[dict[str, str]]:
    """
    Extrahiert Videoinformationen aus dem YouTube-Verlauf.
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
