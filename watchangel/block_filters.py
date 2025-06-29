# watchangel/block_filters.py

from typing import List
from .config_loader import load_lines

# 🔒 Geladene Blockregeln aus config/
BLOCK_KEYWORDS: List[str] = load_lines("block_keywords.txt")
BLOCK_PHRASES: List[str] = load_lines("block_phrases.txt")
BLOCK_CHANNELS: List[str] = load_lines("block_channels.txt")


def is_suspicious_title(title: str) -> bool:
    """
    Prüft, ob ein Videotitel auffällige Schlüsselwörter oder Phrasen enthält.

    :param title: Der Videotitel
    :return: True, wenn verdächtig, sonst False
    """
    lower = title.lower()
    return (
        any(kw in lower for kw in BLOCK_KEYWORDS) or
        any(phrase in lower for phrase in BLOCK_PHRASES)
    )


def is_suspicious_channel(channel_name: str) -> bool:
    """
    Prüft, ob ein Kanalname in der Blockliste steht.

    :param channel_name: Kanalname des YouTube-Kanals
    :return: True, wenn blockiert werden soll, sonst False
    """
    return channel_name.strip().lower() in {c.lower() for c in BLOCK_CHANNELS}


def is_arabic(text: str) -> bool:
    """
    Erkennt arabischen Text anhand typischer Unicode-Bereiche.

    :param text: Titel oder Kanalname
    :return: True, wenn arabischer Text erkannt wird
    """
    return any("\u0600" <= ch <= "\u06FF" or "\u0750" <= ch <= "\u077F" for ch in text)
