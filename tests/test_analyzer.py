from pathlib import Path

from watchangel.analysis import analyzer
from unittest.mock import patch, MagicMock


def test_is_suspicious_title_hits_expected():
    assert analyzer.is_suspicious_title("Rainbow M&Ms slime colors") is True
    assert analyzer.is_suspicious_title("oddly satisfying video") is True


def test_is_suspicious_title_false_positive():
    assert analyzer.is_suspicious_title("Educational video about animals") is False
    assert analyzer.is_suspicious_title("Introduction to math for kids") is False


@patch("watchangel.analyzer.requests.get")
def test_save_thumbnail_creates_file(mock_get, tmp_path: Path):
    video_id = "abc123"
    out_path = tmp_path / "thumb.jpg"

    # 1x1 weißes PNG-Bild (gültig, aber winzig)
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.content = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc\x00\x01"
        b"\x00\x00\x05\x00\x01\x0d\n\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    mock_get.return_value = mock_response

    analyzer.save_thumbnail(video_id, out_path)

    assert out_path.exists()
    assert out_path.stat().st_size > 0