import time
from selenium.webdriver.chrome.webdriver import WebDriver

def scroll_to_end(driver: WebDriver, max_scrolls: int = 50, pause_time: float = 2.0) -> None:
    """
    Scrollt durch eine Seite bis zum Seitenende oder bis max. Anzahl erreicht ist.
    Wird z. B. in YouTube-Verläufen genutzt.

    :param driver: Aktiver Selenium WebDriver
    :param max_scrolls: Maximal erlaubte Scrollzyklen
    :param pause_time: Wartezeit zwischen Scrolls
    """
    scrolls = 0
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while scrolls < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")

        if new_height == last_height:
            print("[🛑] Seitenende erreicht – keine weiteren Inhalte.")
            break

        last_height = new_height
        scrolls += 1
