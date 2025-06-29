import pytest
from unittest.mock import MagicMock, patch
from watchangel.blocker import block_channel

@patch("watchangel.blocker.time.sleep")
def test_block_channel_click_sequence(mock_sleep):
    # BLOCK_PHRASES enthält z. B. "don't recommend channel"
    mock_video = MagicMock()
    mock_menu_button = MagicMock()
    mock_video.find_element.return_value = mock_menu_button

    mock_menu_item = MagicMock()
    mock_menu_item.text = "Don't recommend channel"
    mock_menu_item.click = MagicMock()

    driver = MagicMock()
    driver.get = MagicMock()
    driver.find_element.return_value = mock_video
    driver.find_elements.return_value = [mock_menu_item]

    block_channel(driver, "https://www.youtube.com/channel/abc123")

    driver.get.assert_called_once_with("https://www.youtube.com/channel/abc123")
    mock_menu_button.click.assert_called_once()
    mock_menu_item.click.assert_called_once()
