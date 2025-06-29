from pathlib import Path
from typing import List

CONFIG_DIR = Path(__file__).parent.parent / "config"


def load_lines(filename: str) -> List[str]:
    """
    Lädt Zeilen aus einer Textdatei im config/-Verzeichnis.

    :param filename: Dateiname (z. B. "block_keywords.txt")
    :return: Liste von Zeilen, jeweils getrimmt
    """
    path = CONFIG_DIR / filename
    if not path.exists():
        print(f"[⚠️] Konfigurationsdatei nicht gefunden: {filename}")
        return []

    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
