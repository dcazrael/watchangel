from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

CONFIG_DIR = PROJECT_ROOT / "config"

log_path = PROJECT_ROOT / "blocked_channels.log"
undo_path = CONFIG_DIR / "undo_block_channels.txt"
wl_path = CONFIG_DIR / "whitelist_channels.txt"
wl_patterns_path = CONFIG_DIR / "whitelist_patterns.txt"