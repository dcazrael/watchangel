from dataclasses import dataclass
from watchangel.model.scanned_video import ScannedVideo
from watchangel.rules.block_rules import BlockDecision


@dataclass
class MatchedVideo:
    """
    Verknüpft ein ScannedVideo mit der Blockentscheidung.
    """
    block: ScannedVideo
    decision: BlockDecision
