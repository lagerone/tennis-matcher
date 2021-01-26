from datetime import date, timedelta
from typing import Optional

from current_date_provider import get_date_today


def calculate_opponent_weight(
    player_elo: int,
    opponent_elo: int,
    latest_match_date: Optional[date] = None,
):
    """Calculates weight for opponent, where lower weight means a better match.

    Args:
        player_elo (int):
        opponent_elo (int):
        latest_match_date (Optional[datetime]):

    Returns:
        int: weight
    """
    abs_elo_diff = abs(player_elo - opponent_elo)
    if latest_match_date:
        if _is_date_within_margin(input_date=latest_match_date, margin_days=7):
            return abs_elo_diff + 100
        if _is_date_within_margin(input_date=latest_match_date, margin_days=14):
            return abs_elo_diff + 75
        if _is_date_within_margin(input_date=latest_match_date, margin_days=35):
            return abs_elo_diff + 25
    return abs_elo_diff


def _is_date_within_margin(input_date: date, margin_days: int) -> bool:
    return get_date_today() - timedelta(days=margin_days) <= input_date
