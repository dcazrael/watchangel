from watchangel.rules.engine_instance import engine
from watchangel.rules.block_rules import BlockDecision

def is_video_blockworthy(title: str, channel_name: str, verbose: bool = False) -> bool:
    decision = engine.explain_block_decision(title, channel_name)
    if decision.block:
        print(f"[⚠️  BLOCK] Verdächtig – {channel_name}")
        print(f"[📛] Grund: {decision.reason}")
    return decision.block

