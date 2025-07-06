from watchangel.utils.config_loader import load_lines
from watchangel.rules.block_rules import BlockRuleEngine

engine = BlockRuleEngine(
    keywords=load_lines("block_keywords.txt"),
    phrases=load_lines("block_phrases.txt"),
    block_channels=load_lines("block_channels.txt"),  # ✅ korrekt
    whitelist_channels=load_lines("whitelist_channels.txt"),
    whitelist_patterns=load_lines("whitelist_patterns.txt"),
    undo_channels=load_lines("undo_block_channels.txt"),
)
