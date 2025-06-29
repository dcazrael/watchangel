import time
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement


from watchangel.rules.block_rules import BlockRuleEngine


def remove_video_from_history(driver: WebDriver, video_id: str, max_scrolls: int = 5) -> None:
    """
    Entfernt ein einzelnes Video anhand der ID aus dem YouTube-Verlauf durch Scrollen.

    :param driver: Aktive WebDriver-Instanz
    :param video_id: YouTube-Video-ID
    :param max_scrolls: Wie oft gescrollt wird, um das Video zu finden
    """
    try:
        driver.get("https://www.youtube.com/feed/history")
        time.sleep(2)

        seen_blocks = set()
        for scroll_round in range(max_scrolls):
            blocks = _get_history_blocks(driver)

            for block in blocks:
                block_id = block.get_attribute("outerHTML")
                if block_id in seen_blocks:
                    continue
                seen_blocks.add(block_id)

                hrefs = block.find_elements(By.CSS_SELECTOR, "a#thumbnail")
                if any(video_id in (href.get_attribute("href") or "") for href in hrefs):
                    # NEU – RICHTIG
                    if _click_remove_from_history(driver, block, "Zielvideo"):
                        return

            print(f"[🔄] Scroll-Versuch {scroll_round + 1}/{max_scrolls}: Video {video_id} nicht gefunden")
            driver.execute_script("window.scrollBy(0, 2000);")
            time.sleep(2.0)

        print(f"[⚠️] Video {video_id} konnte nicht entfernt werden")

    except Exception as e:
        print(f"[❌] Fehler beim Entfernen: {e}")


def remove_all_from_channel(driver: WebDriver, video_id: str) -> None:
    """
    Entfernt ein Zielvideo sowie alle Videos desselben Kanals aus dem Verlauf.

    :param driver: Aktive WebDriver-Instanz
    :param video_id: YouTube-Video-ID
    """
    try:
        rules = BlockRuleEngine.from_logs()

        driver.get("https://www.youtube.com/feed/history")
        time.sleep(2)

        channel_name = _find_channel_name(driver, video_id)
        if not channel_name:
            print("[⚠️] Kanal nicht gefunden – keine Löschung")
            return

        deleted = 0
        seen_blocks = set()
        last_height = 0

        while True:
            blocks = _get_history_blocks(driver)

            for block in blocks:
                # Nutze ID des Elements zur Duplikatserkennung
                block_id = block.id
                if block_id in seen_blocks:
                    continue
                seen_blocks.add(block_id)

                # Kanalname vom aktuellen Block extrahieren
                try:
                    current_name = block.find_element(
                        By.CSS_SELECTOR, "ytd-channel-name a"
                    ).text.strip()
                except NoSuchElementException:
                    continue

                # Ist es derselbe Kanal wie das Zielvideo?
                if current_name != channel_name:
                    continue

                # Prüfe, ob Kanal überhaupt blockiert werden darf
                decision = rules.explain_block_decision(title="", channel_name=channel_name)
                if not decision.block:
                    print(f"[🛑] Überspringe '{current_name}' – Grund: {decision.reason or 'nicht blockiert'}")
                    continue

                if _click_remove_from_history(driver, block, current_name):
                    deleted += 1
                    time.sleep(1)

            # Scrolle weiter
            driver.execute_script("window.scrollBy(0, 2000);")
            time.sleep(1.5)

            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        if deleted == 0:
            print(f"[ℹ️] Keine Videos von '{channel_name}' entfernt")
        else:
            print(f"[✅] {deleted} Videos von '{channel_name}' entfernt")

    except Exception as e:
        print(f"[❌] Fehler bei Kanalentfernung: {e}")


def _get_history_blocks(driver: WebDriver):
    return driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")


def _is_video_from_channel(block, channel_name: str) -> bool:
    try:
        current_name = block.find_element(
            By.CSS_SELECTOR, "ytd-channel-name a"
        ).text.strip()
        return current_name == channel_name
    except NoSuchElementException:
        return False


def _click_remove_from_history(driver: WebDriver, block: WebElement, channel_name: str) -> bool:
    """
    Versucht, das Entfernen-Symbol im History-Eintrag zu klicken.
    Gibt True zurück, wenn erfolgreich.
    """
    try:
        button = block.find_element(
            By.CSS_SELECTOR, 'button[aria-label="Remove from watch history"]'
        )

        # Scroll in den sichtbaren Bereich
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", block)

        time.sleep(0.5)

        # Warte, bis Button sichtbar ist
        WebDriverWait(block.parent, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Remove from watch history"]')))

        # Klick mit ActionChains (vermeidet Überdeckungen)
        ActionChains(block.parent).move_to_element(button).click().perform()

        print(f"[🗑️] Video von Kanal '{channel_name}' wurde entfernt.")
        return True
    except Exception as e:
        print(f"[⚠️] Klick auf Entfernen fehlgeschlagen bei '{channel_name}': {e}")
        return False


def _find_channel_name(driver: WebDriver, video_id: str, verbose: bool = False) -> str | None:
    """
    Extrahiert den Kanalnamen zu einem gegebenen Video im Verlauf.

    :param driver: WebDriver
    :param video_id: YouTube Video ID
    :param verbose: Optionales Debugging aktivieren
    :return: Kanalname oder None
    """
    blocks = _get_history_blocks(driver)
    for idx, block in enumerate(blocks):
        hrefs = block.find_elements(By.CSS_SELECTOR, "a#thumbnail")
        urls = [href.get_attribute("href") for href in hrefs]
        if any(video_id in (url or "") for url in urls):
            try:
                channel_elem = block.find_element(By.CSS_SELECTOR, "ytd-channel-name a")
                name = channel_elem.text.strip()
                if verbose:
                    print(f"[🔎] Block {idx}: Video-ID gefunden → Kanal: '{name}'")
                return name
            except NoSuchElementException:
                if verbose:
                    print(f"[⚠️] Block {idx}: Kein Kanalname-Element für Video-ID {video_id}")
                return None
    if verbose:
        print(f"[❌] Kein Video mit ID {video_id} im sichtbaren Verlauf gefunden.")
    return None



def clean_blocked_channels_from_history(driver: WebDriver) -> None:
    """
    Geht durch die gesamte YouTube-Verlaufseite und entfernt Videos
    von bereits bekannten blockierten Kanälen.
    """
    print("[🧹] Starte Bereinigung anhand der Blockliste...")

    rules = BlockRuleEngine.from_logs()

    deleted = 0
    seen_ids = set()
    last_height = 0

    driver.get("https://www.youtube.com/feed/history")
    time.sleep(2)

    while True:
        blocks = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")
        for block in blocks:
            block_id = block.id
            if block_id in seen_ids:
                continue
            seen_ids.add(block_id)

            try:
                channel_name = block.find_element(
                    By.CSS_SELECTOR, "ytd-channel-name a"
                ).text.strip()

                decision = rules.explain_block_decision(title="", channel_name=channel_name)
                if decision.block:
                    print(f"[🚫] Blocke '{channel_name}' – Grund: {decision.reason}")
                    _click_remove_from_history(driver, block, channel_name)
                    deleted += 1
                    time.sleep(1)

            except NoSuchElementException:
                continue

        driver.execute_script("window.scrollBy(0, 2000);")
        time.sleep(1.5)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    if deleted == 0:
        print("[ℹ️] Keine passenden Videos gefunden.")
    else:
        print(f"[✅] {deleted} Videos entfernt.")
