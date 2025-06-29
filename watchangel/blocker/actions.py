# blocker/actions.py

import time
from typing import Dict, List
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from .constants import HIDE_LABEL, BLOCK_LABEL, CSS_SELECTORS
from .ui_navigation import (
    wait_for_about_modal,
    open_report_menu,
    get_report_menu_items,
    click_done_button,
)


def block_channel(driver: WebDriver, channel_url: str) -> None:
    """
    Startet den vollständigen Blockiervorgang für einen Kanal.
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


def handle_channel_menu(driver: WebDriver, menu_items: List, channel_url: str) -> None:
    actions: Dict[str, bool] = {BLOCK_LABEL: False, HIDE_LABEL: False}
    menu_texts = {HIDE_LABEL: None, BLOCK_LABEL: None}

    for item in menu_items:
        text = item.text.strip().lower()
        if HIDE_LABEL in text:
            menu_texts[HIDE_LABEL] = text
        elif BLOCK_LABEL in text:
            menu_texts[BLOCK_LABEL] = text

    if menu_texts[HIDE_LABEL]:
        new_items = get_report_menu_items(driver)
        for item in new_items:
            if HIDE_LABEL in item.text.strip().lower():
                actions[HIDE_LABEL] = handle_hide_user(driver, item)
                break
        time.sleep(1)

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
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, CSS_SELECTORS["continue_button"])
            )
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

        click_done_button(driver)
        return True
    except TimeoutException:
        print("[⚠️] BLOCK/UNBLOCK-Button nicht gefunden")
        return False


def handle_hide_user(driver: WebDriver, item) -> bool:
    label = item.text.strip().lower()
    if "unhide user from my channel" in label:
        print("[ℹ️] Bereits versteckt – UNHIDE vorhanden, kein Klick nötig")
        return True

    item.click()
    try:
        print("[🧪] Klicke auf Submit-Button...")
        submit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, CSS_SELECTORS["submit_button"])
            )
        )
        submit_button.click()
        print("[✅] Submit ausgeführt")
        return True
    except TimeoutException:
        print("[⚠️] Submit nicht geklickt")
        return False


def summarize_blocking(actions: Dict[str, bool], channel_url: str) -> None:
    if any(actions.values()):
        print(f"[👮‍♂️] Blockiert: {channel_url}")
        if not all(actions.values()):
            print(f"[⚠️] Nur teilweise blockiert: {actions}")
    else:
        print("[⚠️] Kein passender Menüeintrag gefunden")

def unhide_user_from_channel(driver: WebDriver, channel_url: str) -> bool:
    """
    Öffnet die /about-Seite des Kanals und führt einen Unhide-Vorgang aus,
    falls 'Unhide user from my channel' im Menü gefunden wird.
    Gibt True zurück, wenn erfolgreich oder bereits nicht versteckt.
    """
    driver.get(channel_url.rstrip("/") + "/about")

    if not wait_for_about_modal(driver):
        print("[❌] About-Modal ist nicht erschienen")
        return False

    try:
        open_report_menu(driver)
        menu_items = get_report_menu_items(driver)
        for item in menu_items:
            text = item.text.strip().lower()
            if "unhide user from my channel" in text:
                item.click()
                print("[🔓] Unhide ausgeführt")
                time.sleep(1)
                try:
                    print("[🧪] Klicke auf Submit-Button...")
                    submit_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, CSS_SELECTORS["submit_button"])
                        )
                    )
                    submit_button.click()
                    print("[✅] Submit ausgeführt")
                    return True
                except TimeoutException:
                    print("[⚠️] Submit nicht geklickt")
                    return False
        print("[ℹ️] Kein Unhide notwendig – Nutzer war nicht blockiert")
        return True
    except Exception as e:
        print(f"[❌] Fehler beim Unhide: {e}")
        return False
