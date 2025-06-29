import argparse
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver

from watchangel.history.cleaner import clean_blocked_channels_from_history
from watchangel.rules.undo_handler import apply_undo_channels_from_log
from watchangel.watcher.watch_loop import check_history_once


def create_driver(profile_dir: Path) -> WebDriver:
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={str(profile_dir)}")
    return webdriver.Chrome(options=options)


def run_watch_loop(driver: WebDriver) -> None:
    try:
        while True:
            check_history_once(driver)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[⛔️] Manuell beendet")
    finally:
        driver.quit()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cleanup", action="store_true", help="Watch History von geblockten Kanälen bereinigen")
    args = parser.parse_args()

    print("[🚀] Starte WatchAngel...")
    profile_path = Path.home() / ".ytwatcher"
    driver = create_driver(profile_path)

    apply_undo_channels_from_log(driver)

    if args.cleanup:
        clean_blocked_channels_from_history(driver)
        driver.quit()
        return

    run_watch_loop(driver)


if __name__ == "__main__":
    main()
