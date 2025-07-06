from pathlib import Path
import requests
from PIL import Image
import imagehash

import re


def save_thumbnail(video_url: str, output_path: Path) -> None:
    """
    Lädt das Thumbnail eines YouTube-Videos herunter und speichert es lokal.

    :param video_url: Die Video-URL
    :param output_path: Pfad, unter dem das Bild gespeichert werden soll
    """
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError(f"Ungültige YouTube-URL oder keine Video-ID erkennbar: {video_url}")

    url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(response.content)


def get_thumbnail_hash(image_path: Path) -> str:
    """
    Berechnet den perceptual hash (phash) eines Bildes zur Ähnlichkeitserkennung.

    :param image_path: Pfad zum Bild
    :return: Hashwert als hex-String
    """
    image = Image.open(image_path)
    phash = imagehash.phash(image)
    return str(phash)


def extract_video_id(url: str) -> str | None:
    """
    Extrahiert die YouTube-Video-ID aus einer URL oder gibt None zurück, wenn keine erkennbar ist.
    """
    if re.fullmatch(r"[a-zA-Z0-9_-]{5,}", url):
        return url
    if "shorts" in url:
        match = re.search(r"/shorts/([a-zA-Z0-9_-]{5,})", url)
        if match:
            return match.group(1)
    elif "watch?v=" in url:
        match = re.search(r"v=([a-zA-Z0-9_-]{5,})", url)
        if match:
            return match.group(1)
    elif "youtu.be/" in url:
        match = re.search(r"youtu\.be/([a-zA-Z0-9_-]{5,})", url)
        if match:
            return match.group(1)
    return None  # Kein valider Match
