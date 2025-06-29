from pathlib import Path
import requests
from PIL import Image
import imagehash


def save_thumbnail(video_id: str, output_path: Path) -> None:
    """
    Lädt das Thumbnail eines YouTube-Videos herunter und speichert es lokal.

    :param video_id: Die Video-ID
    :param output_path: Pfad, unter dem das Bild gespeichert werden soll
    """
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
