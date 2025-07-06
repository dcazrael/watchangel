from selenium.webdriver.chrome.webdriver import WebDriver
import json

from watchangel.blocker.actions import unhide_user_from_channel
from watchangel.utils.paths import log_path, undo_path


def apply_undo_channels_from_log(driver: WebDriver) -> None:
    """
    Entsperrt Kanäle aus 'undo_block_channels.txt', sofern sie im Log existieren.
    Erfolgreiche Entsperrung → Logeintrag aus 'blocked_channels.log' entfernen.
    """

    if not log_path.exists() or not undo_path.exists():
        return

    # (1) Lade Undo-Namen (alle lowercased)
    undo_names = {line.strip().lower() for line in undo_path.read_text(encoding="utf-8").splitlines() if line.strip()}

    # (2) Lade komplette Logdatei
    all_entries: list[dict] = []
    with log_path.open(encoding="utf-8") as f:
        for line in f:
            try:
                all_entries.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue

    # (3) Finde und versuche Entsperrung
    removed_entries: list[dict] = []
    remaining_entries: list[dict] = []

    for entry in all_entries:
        name = entry.get("channel_name", "").strip()
        url = entry.get("channel_url", "").strip()

        if name.lower() in undo_names:

            success = unhide_user_from_channel(driver, channel_url=url)
            if success:
                print(f"[🔓] Entsperrt: {name}")
                removed_entries.append(entry)
            else:
                print(f"[⚠️] Konnte '{name}' nicht entsperren.")
                remaining_entries.append(entry)
        else:
            remaining_entries.append(entry)

    # (4) Schreibe neue blocked_channels.log ohne entfernte Kanäle
    if removed_entries:
        with log_path.open("w", encoding="utf-8") as f:
            for entry in remaining_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        print(f"[🧹] {len(removed_entries)} Kanal(e) aus Log entfernt (Undo erfolgreich).")

        # (5) Entferne erfolgreiche aus undo_block_channels.txt
        removed_names = {e["channel_name"].strip().lower() for e in removed_entries}
        updated_undo = [line for line in undo_names if line not in removed_names]

        with undo_path.open("w", encoding="utf-8") as f:
            for line in updated_undo:
                f.write(line + "\n")

        print(f"[🧼] Undo-Liste aktualisiert ({len(updated_undo)} verbleibend).")

