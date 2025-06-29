from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from .constants import CSS_SELECTORS

import time


def wait_for_about_modal(driver: WebDriver, timeout: int = 10) -> bool:
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Report user']"))
        )
        return True
    except TimeoutException:
        return False


def open_report_menu(driver: WebDriver, timeout: int = 10) -> None:
    flag_button = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, CSS_SELECTORS["flag_button"]))
    )
    flag_button.click()
    time.sleep(1)


def get_report_menu_items(driver: WebDriver, timeout: int = 5):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, CSS_SELECTORS["report_item"]))
    )
    return driver.find_elements(By.CSS_SELECTOR, CSS_SELECTORS["report_item"])


def click_done_button(driver: WebDriver, timeout: int = 5) -> bool:
    try:
        done_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, CSS_SELECTORS["done_button"]))
        )
        done_button.click()
        return True
    except TimeoutException:
        return False
