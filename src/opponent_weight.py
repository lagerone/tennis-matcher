from datetime import date, timedelta
from typing import Optional

from current_date_provider import get_date_today


def calculate_opponent_weight(
    player_elo: int,
    opponent_elo: int,
    matches_count: int,
    latest_match_date: Optional[date] = None,
):
    """Calculates weight for opponent, where lower weight means a better match.

    Args:
        player_elo (int):
        opponent_elo (int):
        matches_count (int):
        latest_match_date (Optional[datetime]):

    Returns:
        int: weight
    """
    abs_elo_diff = abs(player_elo - opponent_elo)
    if matches_count == 0:
        return abs_elo_diff
    if latest_match_date:
        if _is_date_within_margin(input_date=latest_match_date, margin_days=7):
            return 1000 - abs_elo_diff
        if _is_date_within_margin(input_date=latest_match_date, margin_days=14):
            return 500 - abs_elo_diff
    return abs(int(round(abs_elo_diff * matches_count)))


def _is_date_within_margin(input_date: date, margin_days: int) -> bool:
    today = get_date_today()
    margin = timedelta(days=margin_days)
    return today - margin <= input_date <= today + margin
