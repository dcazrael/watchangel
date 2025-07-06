from dataclasses import dataclass
from selenium.webdriver.remote.webelement import WebElement


@dataclass
class ScannedVideo:
    """
    Repräsentiert ein einzelnes Videoelement aus dem YouTube-Verlauf.
    Enthält Metadaten zur späteren Bewertung und Entfernung.
    """
    title: str
    channel_name: str
    channel_url: str
    video_id: str
    element: WebElement
