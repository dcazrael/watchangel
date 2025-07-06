import time
from typing import Sequence
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException

from watchangel.model.matched_video import MatchedVideo
from watchangel.rules.block_rules import BlockRuleEngine
from watchangel.watcher.video_handler import log_block_action


def clean_matched_videos(driver: WebDriver, matches: Sequence[MatchedVideo]) -> int:
    """
    Entfernt Videos aus dem Verlauf, die als blockwürdig bewertet wurden.

    - Zuerst von unten nach oben (stabil)
    - Optionaler zweiter Durchlauf bei Bedarf

    :param driver: Aktive WebDriver-Instanz
    :param matches: Liste blockwürdiger Videos mit DOM-Referenz
    :return: Anzahl gelöschter Videos
    """

    deleted = 0
    rules = BlockRuleEngine.from_logs()
    seen_channels: set[str] = set()

    print(f"[🧹] Bereinige {len(matches)} Videos aus dem Verlauf...")

    for match in reversed(matches):
        channel_name = match.block.channel_name
        channel_key = channel_name.lower()

        if channel_key in rules.whitelist_channels:
            print(f"[🛑] SKIP: '{channel_name}' steht auf Whitelist.")
            continue

        if remove_video_element(driver, match.block.element, channel_name):
            deleted += 1

            # Logging & Persistenz
            if channel_key not in rules.block_channels and channel_key not in seen_channels:
                log_block_action({
                    "channel_name": channel_name,
                    "channel_url": match.block.channel_url,
                    "title": match.block.title,
                    "video_id": match.block.video_id
                })
                seen_channels.add(channel_key)

            time.sleep(1)

    print(f"[✅] {deleted} Video(s) erfolgreich entfernt.")
    return deleted


def remove_video_element(driver: WebDriver, element: WebElement, channel_name: str) -> bool:
    """
    Klickt den Button „Aus Verlauf entfernen“ im gegebenen DOM-Element.

    :param driver: Aktiver WebDriver
    :param element: DOM-Element des Videos
    :param channel_name: Name für Logging
    :return: True bei Erfolg, sonst False
    """
    try:
        remove_btn = WebDriverWait(element, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Remove from watch history"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", element)
        remove_btn.click()
        print(f"[🗑️] Video von Kanal '{channel_name}' entfernt.")
        return True
    except TimeoutException:
        print(f"[⚠️] Entfernen bei '{channel_name}' nicht möglich (nicht klickbar)")
        return False
    except Exception as e:
        print(f"[⚠️] Fehler bei '{channel_name}': {e}")
        return False
