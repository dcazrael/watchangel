# 🛡️ Watchangel

**Watchangel** ist ein Python-Tool, das automatisch verdächtige YouTube-Videos erkennt und deren Kanäle blockiert – speziell für Eltern, deren Kinder YouTube über Tablets nutzen.

---

## 🌟 Ziel

Viele kinderschädliche oder schlicht „braindead“ Videos (z. B. *M\&Ms zählen*, *Slime crush*, *Learn Colors*) umgehen YouTubes Filter und werden unter tausenden Accounts hochgeladen.
Watchangel filtert solche Inhalte aus dem **Watch-Verlauf** (History) und blockiert die zugehörigen Kanäle automatisch – durch einen Selenium gesteuerten Chrome.

---

## 🔧 Funktionen

* Lädt den neuesten Eintrag aus der Watch-History
* Prüft Titel auf verdächtige Keywords
* Speichert das Thumbnail lokal ab
* Protokolliert den Block in `blocked_channels.json`
* Öffnet den Kanal, klickt auf das Menü und wählt „Don't recommend channel“

---

## 🚀 Setup

### 1. Projekt klonen

```bash
git clone https://github.com/deinname/watchangel
cd watchangel
uv pip install -e .
```

> Du brauchst: Python 3.10+, [`uv`](https://github.com/astral-sh/uv), Chrome + chromedriver

---

### 2. Chrome-Profil anlegen

Starte einmal manuell Chrome mit:

```bash
google-chrome --user-data-dir=~/.ytwatcher
```

* Logge dich in YouTube ein
* Stelle die Sprache auf **Englisch (US)** (Wichtig für „Don't recommend“-Menü)
* Beende Chrome

---

### 3. Projektstruktur

```text
watchangel/
├── config/
│   ├── block_keywords.txt     ← Schlüsselwörter wie „slime“, „m&ms“ etc.
│   └── block_phrases.txt      ← Texte im Kontextmenü (z. B. „Don't recommend“)
├── thumbnails/                ← Gespeicherte Thumbnails verdächtiger Videos
├── blocked_channels.json      ← Log-Datei geblockter Kanäle
├── watchangel/
│   ├── __init__.py
│   ├── main.py                ← Einstiegspunkt
│   ├── watcher.py
│   ├── analyzer.py
│   ├── blocker.py
│   └── config_loader.py
```

---

## ▶️ Ausführen

```bash
python watchangel/main.py
```

Der Watchdog läuft in einer Endlosschleife und prüft alle 5 Minuten das neueste Video aus der Watch-History.

---

## 🧐 Beispielausgabe

```text
[🎯] Prüfe: M&Ms Rainbow Slime Learn Colors
[⚠️ BLOCK] Verdächtiges Video erkannt: M&Ms Rainbow Slime Learn Colors
[✅] Kanal blockiert: SlimeForFunTV
```

---

## 🧰 Erweiterungsmöglichkeiten

* Bildbasierte Klassifikation via `imagehash`
* Manuelle Whitelist
* Weboberfläche zum Bearbeiten der Blockliste
* Automatische Reports via Discord, Telegram, E-Mail etc.

---

## ⚠️ Hinweis

Dieses Tool **verwendet Selenium** mit echtem Chrome. Du solltest es nur auf deinem eigenen Rechner ausführen und **nicht öffentlich hosten** – insbesondere wegen des Google-Logins.

---

## 📜 Lizenz

MIT – frei nutzbar und anpassbar.
Verwendung auf eigene Verantwortung.
