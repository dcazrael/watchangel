# watchangel/history_cleaner.py

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def remove_video_from_history(driver: WebDriver, video_id: str) -> None:
    """
    Entfernt ein Video anhand der YouTube-Video-ID aus dem Wiedergabeverlauf.

    :param driver: Aktive Chrome WebDriver-Instanz
    :param video_id: YouTube-Video-ID
    """
    try:
        driver.get("https://www.youtube.com/feed/history")
        time.sleep(3)

        video_blocks = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")
        for block in video_blocks:
            hrefs = block.find_elements(By.CSS_SELECTOR, "a#thumbnail")
            if any(video_id in (href.get_attribute("href") or "") for href in hrefs):
                try:
                    menu_button = block.find_element(By.ID, "button")
                    menu_button.click()
                    time.sleep(1)

                    try:
                        # Warte auf das spezifische "Remove from watch history"-Buttonelement
                        remove_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, "ytd-button-renderer button[aria-label='Remove from watch history']")
                            )
                        )
                        remove_button.click()
                        print(f"[🗑️] Entfernt aus Verlauf: {video_id}")
                        return

                    except TimeoutException:
                        print("[⚠️] Entfernen-Button nicht klickbar")
                        return

                except (NoSuchElementException, TimeoutException):
                    print("[⚠️] Fehler beim Öffnen des Menüs für Video")
                    return


        print("[⚠️] Video im Verlauf nicht gefunden")

    except Exception as e:
        print(f"[❌] Fehler beim Entfernen aus Verlauf: {e}")
