import time
from typing import Callable, Optional, Set
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from watchangel.model.scanned_video import ScannedVideo
from watchangel.rules.block_rules import BlockRuleEngine

from watchangel.matching.matching import match_video
from watchangel.model.matched_video import MatchedVideo

def try_match_element(element: WebElement, rules: BlockRuleEngine) -> Optional[MatchedVideo]:
    """
    Erstellt ein ScannedVideo aus einem WebElement und führt ein Matching durch.
    Gibt ein MatchedVideo zurück, wenn blockwürdig – sonst None.
    """
    try:
        channel_element = element.find_element(By.CSS_SELECTOR, "ytd-channel-name a")
        title_element = element.find_element(By.ID, "video-title")
        href = title_element.get_attribute("href") or ""
        channel_url = channel_element.get_attribute("href") or ""

        scanned = ScannedVideo(
            video_id=href.split("v=")[-1],
            title=title_element.text.strip(),
            channel_name=channel_element.text.strip(),
            channel_url=channel_url,
            element=element
        )
        return match_video(scanned, rules)
    except Exception:
        return None


def remove_all_from_channel(driver: WebDriver, video_id: str) -> None:
    """
    Entfernt ein Zielvideo sowie alle Videos desselben Kanals, sofern blockiert.
    """
    rules: BlockRuleEngine = BlockRuleEngine.from_logs()
    print(f"[📺] Ermittle Kanal zu Video {video_id} ...")
    channel_name: Optional[str] = find_channel_name(driver, video_id)

    if channel_name is None:
        print("[⚠️] Kanal nicht gefunden – keine Löschung")
        return

    deleted_count: int = 0

    def processor(block: WebElement) -> bool:
        nonlocal deleted_count
        try:
            current_name: str = block.find_element(By.CSS_SELECTOR, "ytd-channel-name a").text.strip()
        except NoSuchElementException:
            return False

        if current_name != channel_name:
            return False

        match = try_match_element(block, rules)
        if not match:
            return False

        if click_remove_from_history(driver, block, current_name):
            deleted_count += 1
        return False

    scroll_and_process(driver, processor)
    print_result(deleted_count, prefix=channel_name)


def find_channel_name(driver: WebDriver, video_id: str) -> Optional[str]:
    """
    Findet den Kanalnamen eines bestimmten Videos im Verlauf.

    :param driver: WebDriver-Instanz
    :param video_id: YouTube-Video-ID
    :return: Kanalname oder None
    """
    result: Optional[str] = None

    def finder(block: WebElement) -> bool:
        nonlocal result
        hrefs = block.find_elements(By.CSS_SELECTOR, "a#thumbnail")
        urls = [href.get_attribute("href") for href in hrefs]
        if any(video_id in (url or "") for url in urls):
            try:
                result = block.find_element(By.CSS_SELECTOR, "ytd-channel-name a").text.strip()
                return True
            except NoSuchElementException:
                return False
        return False

    scroll_and_process(driver, finder)
    return result


def scroll_and_process(driver: WebDriver, processor: Callable[[WebElement], bool], max_scrolls: int = 50) -> None:
    """
    Scrollt durch die Verlaufseite und ruft eine Callback-Funktion für jeden neuen Block auf.
    """
    seen: Set[str] = set()
    driver.get("https://www.youtube.com/feed/history")
    time.sleep(2)

    scroll_round: int = 0
    idle_rounds: int = 0
    MAX_IDLE: int = 3

    print("[📜] Scanne Verlauf ...")

    while scroll_round < max_scrolls:
        blocks = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")
        new_blocks = 0

        for block in blocks:
            key = block.get_attribute("outerHTML")
            if key in seen:
                continue
            seen.add(key)
            new_blocks += 1

            if processor(block):
                print("[✅] Ziel erreicht – Vorgang abgeschlossen.")
                return

        if new_blocks == 0:
            idle_rounds += 1
            print(f"[⏳] Keine neuen Einträge – Versuch {idle_rounds}/{MAX_IDLE} ...")
        else:
            idle_rounds = 0
            print(f"[🔍] {new_blocks} neue Blöcke analysiert (gesamt: {len(seen)})")

        if idle_rounds >= MAX_IDLE:
            print("[🛑] Keine neuen Inhalte mehr – Abbruch.")
            break

        if blocks:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'end'});", blocks[-1])
        time.sleep(2.0)
        scroll_round += 1


def click_remove_from_history(driver: WebDriver, block: WebElement, channel_name: str) -> bool:
    """
    Klickt den Button „Aus Verlauf entfernen“ im angegebenen Block.

    :param driver: Aktiver WebDriver
    :param block: DOM-Element mit dem Zielvideo
    :param channel_name: Kanalname für Logging
    :return: True bei Erfolg, sonst False
    """
    try:
        button: WebElement = block.find_element(By.CSS_SELECTOR, 'button[aria-label="Remove from watch history"]')
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", block)
        time.sleep(0.5)
        WebDriverWait(block.parent, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Remove from watch history"]'))
        )
        ActionChains(block.parent).move_to_element(button).click().perform()
        print(f"[🗑️] Video von Kanal '{channel_name}' wurde entfernt.")
        return True
    except Exception as e:
        print(f"[⚠️] Entfernen fehlgeschlagen bei '{channel_name}': {e}")
        return False


def print_result(count: int, prefix: str = "") -> None:
    """
    Gibt das Ergebnis der Löschung aus.

    :param count: Anzahl gelöschter Videos
    :param prefix: Optionaler Zusatz (z.B. Kanalname)
    """
    if count == 0:
        print(f"[ℹ️] Keine passenden Videos entfernt{f' von {prefix!r}' if prefix else ''}.")
    else:
        print(f"[✅] {count} Video(s) entfernt{f' von {prefix!r}' if prefix else ''}.")
