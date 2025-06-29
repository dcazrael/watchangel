from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from typing import List, Dict
import time
from .config_loader import load_lines

BLOCK_PHRASES = [s.lower() for s in load_lines("block_phrases.txt")]

# Konstante für Menüeinträge
HIDE_LABEL = "hide user from my channel"
BLOCK_LABEL = "block channel for kids"

def block_channel(driver: WebDriver, channel_url: str) -> None:
    """
    Steuert den YouTube-Kanal an und startet den Blockierprozess.
    """
    driver.get(channel_url + "/about")

    if not wait_for_about_modal(driver):
        print("[❌] About-Modal ist nicht erschienen")
        return

    try:
        open_report_menu(driver)
        menu_items = get_report_menu_items(driver)
        handle_channel_menu(driver, menu_items, channel_url)
    except Exception as e:
        print(f"[❌] Fehler beim Blockieren: {e}")

def wait_for_about_modal(driver: WebDriver) -> bool:
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Report user']"))
        )
        return True
    except TimeoutException:
        return False

def open_report_menu(driver: WebDriver) -> None:
    """
    Klickt auf das Flaggen-Menü des Kanals.
    """
    flag_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#flagging-button button"))
    )
    flag_button.click()
    time.sleep(1)

def get_report_menu_items(driver: WebDriver) -> List:
    """
    Extrahiert die Menüeinträge aus dem Report-Menü.
    """
    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tp-yt-paper-item"))
    )
    return driver.find_elements(By.CSS_SELECTOR, "tp-yt-paper-item")


def handle_channel_menu(driver: WebDriver, menu_items: List, channel_url: str) -> None:
    actions: Dict[str, bool] = {
        BLOCK_LABEL: False,
        HIDE_LABEL: False
    }

    # Nur Texte merken, keine Elemente
    menu_texts = {HIDE_LABEL: None, BLOCK_LABEL: None}

    for item in menu_items:
        text = item.text.strip().lower()
        if HIDE_LABEL in text:
            menu_texts[HIDE_LABEL] = text
        elif BLOCK_LABEL in text:
            menu_texts[BLOCK_LABEL] = text

    # 1. HIDE
    if menu_texts[HIDE_LABEL]:
        open_report_menu(driver)
        new_items = get_report_menu_items(driver)
        for item in new_items:
            if HIDE_LABEL in item.text.strip().lower():
                actions[HIDE_LABEL] = handle_hide_user(driver, item)
                break
        time.sleep(1)

    # 2. BLOCK
    if menu_texts[BLOCK_LABEL]:
        open_report_menu(driver)
        new_items = get_report_menu_items(driver)
        for item in new_items:
            if BLOCK_LABEL in item.text.strip().lower():
                actions[BLOCK_LABEL] = handle_block_kids(driver, item)
                break
        time.sleep(1)

    summarize_blocking(actions, channel_url)



def handle_block_kids(driver: WebDriver, item) -> bool:
    item.click()
    try:
        print("[🧪] Warte auf 'CONTINUE'-Button...")
        continue_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#confirm-button button[aria-label='Continue']"))
        )
        continue_button.click()
        print("[👉] CONTINUE geklickt")
    except TimeoutException:
        print("[⚠️] CONTINUE nicht gefunden")
        return False

    print("[🧪] Suche 'BLOCK'- oder 'UNBLOCK'-Button...")
    try:
        toggle_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-toggle-button-renderer button"))
        )
        label = toggle_button.get_attribute("aria-label") or ""
        if "block" in label.lower() and "unblock" not in label.lower():
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(toggle_button)).click()
            print("[🚫] BLOCK geklickt")
        elif "unblock" in label.lower():
            print("[ℹ️] Bereits geblockt – UNBLOCK vorhanden, kein Klick nötig")
        else:
            print(f"[❔] Unerwartetes aria-label: {label}")

        handle_done(driver)
        return True
    except TimeoutException:
        print("[⚠️] BLOCK/UNBLOCK-Button nicht gefunden")
        return False


def handle_hide_user(driver: WebDriver, item) -> bool:
    item.click()
    try:
        print("[🧪] Klicke auf Submit-Button...")
        submit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#confirm-button button[aria-label='Submit']"))
        )
        submit_button.click()
        print("[✅] Submit ausgeführt")
        return True
    except TimeoutException:
        print("[⚠️] Submit nicht geklickt")
        return False


def handle_done(driver: WebDriver) -> bool:
    # [🧼] DONE klicken
    try:
        print("[🧪] Warte auf 'DONE'-Button...")
        done_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#done-button button[aria-label='Done']"))
        )
        done_button.click()
        print("[✅] DONE geklickt")
    except TimeoutException:
        print("[⚠️] DONE nicht gefunden – Dialog evtl. offen")

    time.sleep(1)
    return True

def summarize_blocking(actions: Dict[str, bool], channel_url: str) -> None:
    if any(actions.values()):
        print(f"[👮‍♂️] Blockiert: {channel_url}")
        if not all(actions.values()):
            print(f"[⚠️] Nur teilweise blockiert: {actions}")
    else:
        print("[⚠️] Kein passender Menüeintrag gefunden")
