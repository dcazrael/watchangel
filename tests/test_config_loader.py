import pytest
from watchangel.utils import config_loader

CONFIG_FILE = "block_keywords.txt"


def test_load_lines_returns_non_empty_list():
    lines = config_loader.load_lines(CONFIG_FILE)
    assert isinstance(lines, list)
    assert len(lines) > 0
    assert all(isinstance(line, str) for line in lines)
    assert all(line.strip() == line for line in lines)  # no leading/trailing whitespace


def test_load_lines_ignores_empty_lines(tmp_path):
    fake_file = tmp_path / "test.txt"
    fake_file.write_text("\nfoo\n\n  bar  \n\n", encoding="utf-8")

    # Temporär Pfad umbiegen
    original_config_dir = config_loader.CONFIG_DIR
    config_loader.CONFIG_DIR = tmp_path

    try:
        lines = config_loader.load_lines("test.txt")
        assert lines == ["foo", "bar"]
    finally:
        config_loader.CONFIG_DIR = original_config_dir


def test_load_lines_raises_if_missing():
    with pytest.raises(FileNotFoundError):
        config_loader.load_lines("does_not_exist.txt")
