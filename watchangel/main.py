import argparse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver

from watchangel.rules.undo_handler import apply_undo_channels_from_log
from watchangel.run.watch_loop_run import run_watch_loop
from watchangel.run.main_clean_run import run_cleanup_pipeline


def create_driver(profile_dir: Path) -> WebDriver:
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={str(profile_dir)}")
    return webdriver.Chrome(options=options)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cleanup", action="store_true", help="Watch History von geblockten Kanälen bereinigen")
    args = parser.parse_args()

    print("[🚀] Starte WatchAngel...")
    profile_path = Path.home() / ".ytwatcher"
    driver = create_driver(profile_path)

    apply_undo_channels_from_log(driver)

    deleted = run_cleanup_pipeline(driver)
    print(f"[🧼] Insgesamt {deleted} Video(s) bereinigt.")

    run_watch_loop(driver)
    driver.quit()


if __name__ == "__main__":
    main()
