from watchangel.rules.block_rules import BlockRuleEngine
from watchangel.model.scanned_video import ScannedVideo
from watchangel.model.matched_video import MatchedVideo


def match_video(video: ScannedVideo, rules: BlockRuleEngine) -> MatchedVideo | None:
    """
    Bewertet ein Videoobjekt mit der BlockRuleEngine.

    :param video: Das erkannte Video
    :param rules: Regelwerk zur Bewertung
    :return: Matching-Ergebnis oder None
    """
    decision = rules.explain_block_decision(
        title=video.title,
        channel_name=video.channel_name,
        video_url=f"https://www.youtube.com/watch?v={video.video_id}",
    )

    if decision.block:
        return MatchedVideo(block=video, decision=decision)
    return None
