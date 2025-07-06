import time

from selenium.webdriver.chrome.webdriver import WebDriver

from watchangel.watcher.watch_loop import check_history_once


def run_watch_loop(driver: WebDriver) -> None:
    """
        Startet die Überwachungsschleife für den YouTube-Wiedergabeverlauf.

        Führt in regelmäßigen Abständen `check_history_once(...)` aus, um neue Videos
        zu prüfen und ggf. automatisch zu blockieren oder zu entfernen.

        Beendet sich sauber bei KeyboardInterrupt (Strg+C).

        :param driver: Aktive Selenium WebDriver-Instanz
        """
    try:
        while True:
            check_history_once(driver)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[⛔️] Manuell beendet")
    finally:
        driver.quit()
