import os
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver

from watchangel.watcher import check_history_once


def create_driver(profile_dir: Path) -> WebDriver:
    """
    Initialisiert den Chrome-WebDriver mit dem angegebenen Benutzerprofil.

    :param profile_dir: Pfad zum Benutzerdatenverzeichnis
    :return: Chrome WebDriver-Instanz
    """
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={str(profile_dir)}")
    return webdriver.Chrome(options=options)


def run_watch_loop(driver: WebDriver) -> None:
    """
    Führt die Hauptüberwachungsschleife aus.

    :param driver: Chrome WebDriver-Instanz
    """
    try:
        while True:
            check_history_once(driver)
    except KeyboardInterrupt:
        print("\n[⛔️] Manuell beendet")
    finally:
        driver.quit()


def main() -> None:
    """
    Einstiegspunkt für das WatchAngel-Tool.
    """
    profile_dir = Path.home() / ".ytwatcher"
    print("[🚀] Starte WatchAngel...")
    time.sleep(1)

    driver = create_driver(profile_dir)
    run_watch_loop(driver)


if __name__ == "__main__":
    main()
