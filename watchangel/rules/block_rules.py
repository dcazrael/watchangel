import json
import re
from dataclasses import dataclass
from typing import ClassVar, Iterable, Optional

from langdetect import detect, LangDetectException

from watchangel.blocker.constants import COMMON_MISDETECTIONS_FOR_ENGLISH
from watchangel.utils.config_loader import load_lines
from watchangel.utils.paths import log_path, wl_path, wl_patterns_path, undo_path
from watchangel.globals import VERBOSE

EMOJI_PATTERN = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)


@dataclass
class BlockDecision:
    """Repräsentiert die Entscheidung, ob ein Video blockiert werden soll."""
    block: bool
    reason: Optional[str] = None


class BlockRuleEngine:
    """
    Bewertet YouTube-Videos anhand von Titel und Kanalname nach festgelegten Regeln.
    """

    _instance: ClassVar[Optional["BlockRuleEngine"]] = None

    def __init__(
            self,
            keywords: Iterable[str],
            phrases: Iterable[str],
            block_channels: Iterable[str],
            whitelist_channels: Iterable[str] = (),
            whitelist_patterns: Iterable[str] = (),
            undo_channels: Iterable[str] = (),
            allowed_languages: Iterable[str] = ("de", "en", "ja"),
    ) -> None:
        self.keywords = {kw.lower() for kw in keywords}
        self.phrases = {ph.lower() for ph in phrases}
        self.block_channels = {ch.lower() for ch in block_channels}
        self.whitelist_channels = {wl.lower() for wl in whitelist_channels}
        self.whitelist_patterns = [p.lower() for p in whitelist_patterns]
        self.undo_channels = {uc.lower() for uc in undo_channels}
        self.allowed_languages = set(allowed_languages)

    # ------------------- Initialisierung -------------------

    @classmethod
    def load_once(cls) -> "BlockRuleEngine":
        """Lädt Regelbasis einmalig aus TXT-Dateien im Projektverzeichnis."""
        return cls(
            keywords=load_lines("block_keywords.txt"),
            phrases=load_lines("block_phrases.txt"),
            block_channels=load_lines("block_channels.txt"),
            whitelist_channels=load_lines("whitelist_channels.txt"),
            whitelist_patterns=load_lines("whitelist_patterns.txt"),
            undo_channels=load_lines("undo_block_channels.txt"),
        )

    @classmethod
    def from_logs(cls, verbose: bool = VERBOSE) -> "BlockRuleEngine":
        """Erstellt Instanz aus Logdatei, Whitelist und Undo-Liste."""

        blocked, whitelist, wl_patterns, undo = [], [], [], []

        if log_path.exists():
            with log_path.open(encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line.strip())
                        name = obj.get("channel_name", "").strip()
                        if name:
                            blocked.append(name)
                    except json.JSONDecodeError:
                        continue

        if wl_path.exists():
            whitelist = [l.strip() for l in wl_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        if wl_patterns_path.exists():
            wl_patterns = [l.strip() for l in wl_patterns_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        if undo_path.exists():
            undo = [l.strip() for l in undo_path.read_text(encoding="utf-8").splitlines() if l.strip()]

        # ⛔️ Entferne manuell entblockte Channels aus der Logliste
        blocked = [c for c in blocked if c.lower() not in {u.lower() for u in undo}]

        if verbose:
            print(f"[📄] {len(blocked)} Kanäle aus Logdatei geladen.")

        if undo:
            undo_set = {u.lower() for u in undo}
            original_count = len(blocked)
            blocked = [c for c in blocked if c.lower() not in undo_set]
            removed = original_count - len(blocked)

            if removed > 0:
                # Logdatei aktualisieren (nicht abhängig von verbose!)
                with log_path.open("w", encoding="utf-8") as f:
                    for c in blocked:
                        f.write(json.dumps({"channel_name": c}) + "\n")

                if verbose:
                    print(f"[🧹] {removed} Kanäle aus blocked_channels.log entfernt (manuell entblockt).")

        return cls(
            keywords=[],
            phrases=[],
            block_channels=blocked,
            whitelist_channels=whitelist,
            whitelist_patterns=wl_patterns,
            undo_channels=undo,
        )

    # ------------------- Hauptlogik -------------------

    def is_blockworthy(self, title: str, channel_name: str, video_url: str = "") -> bool:
        """Gibt zurück, ob das Video blockiert werden soll."""
        return self.explain_block_decision(title, channel_name, video_url).block

    def explain_block_decision(self, title: str, channel_name: str, video_url: str = "") -> BlockDecision:
        """
        Liefert eine Entscheidung samt Begründung, warum ein Video blockiert wurde.
        """
        name = channel_name.strip().lower()
        lower_title = title.strip().lower()

        # 0. Mix-Video
        if video_url and self.is_mix(title, video_url):
            return BlockDecision(True, "Mix-Video erkannt")

        # 1. Whitelist-Kanalname (genau)
        if name in self.whitelist_channels:
            return BlockDecision(False, "whitelisted")

        # 2. Whitelist-Pattern (entweder im Titel oder Kanalname)
        for pattern in self.whitelist_patterns:
            if pattern in name or pattern in lower_title:
                return BlockDecision(False, f"whitelisted pattern: {pattern}")

        # 3. Undo
        if name in self.undo_channels:
            return BlockDecision(False, "manually unblocked")

        # 4. Arabisch
        if self.is_arabic(channel_name):
            return BlockDecision(True, "arabic channel name")
        if self.is_arabic(title):
            return BlockDecision(True, "arabic title")

        # 5. Sprache
        if self.is_unsupported_language(channel_name):
            return BlockDecision(True, "unsupported channel language")
        if self.is_unsupported_language(title):
            return BlockDecision(True, "unsupported title language")

        # 6. Blockliste
        if name in self.block_channels:
            return BlockDecision(True, "explicitly blocked channel")

        # 7. Keywords/Phrasen im Titel
        for phrase in self.phrases:
            if phrase in lower_title:
                return BlockDecision(True, f"matched phrase: {phrase}")
        for keyword in self.keywords:
            if keyword in lower_title:
                return BlockDecision(True, f"matched keyword: {keyword}")

        return BlockDecision(False, None)

    # ------------------- Regel-Helfer -------------------

    def is_arabic(self, text: str) -> bool:
        """Erkennt arabische Schriftzeichen im Text."""
        return any("\u0600" <= ch <= "\u06FF" or "\u0750" <= ch <= "\u077F" for ch in text)

    def is_unsupported_language(self, text: str) -> bool:
        cleaned = self.strip_emojis(text)
        words = cleaned.split()
        letters_only = ''.join(c for c in cleaned if c.isalpha())

        if len(letters_only) < 5 or len(words) < 3:
            return False

        try:
            lang = detect(cleaned)
            if VERBOSE:
                print(f"[🧪] Language detected: {lang} ← {cleaned!r}")
            # Wenn fälschlich Somali etc. erkannt wurde, als Englisch behandeln
            if lang in COMMON_MISDETECTIONS_FOR_ENGLISH and "a" in cleaned.lower():
                lang = "en"
            return lang not in self.allowed_languages
        except LangDetectException:
            return self.is_arabic(text)

    def is_mix(self, title: str, video_url: str) -> bool:
        """
        Erkennt YouTube-Mix-Videos anhand von URL oder Titelstruktur.
        """
        title_lc = title.lower()
        return (
                "mix" in title_lc
                or "automix" in title_lc
                or "playlist" in title_lc
                or "best of" in title_lc
                or "youTube mix" in title_lc
                or "list=rd" in video_url.lower()
                or "list=ul" in video_url.lower()
                or "/mix/" in video_url.lower()
        )

    @staticmethod
    def strip_emojis(text: str) -> str:
        """Entfernt Emojis (Unicode 10000+)."""
        return EMOJI_PATTERN.sub("", text)
