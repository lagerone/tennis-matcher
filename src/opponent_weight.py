from datetime import date, timedelta
from typing import List

from current_date_provider import get_date_today


def _calculate_points_for_match_date(match_date: date) -> int:
    if _is_date_within_margin(input_date=match_date, margin_days=7):
        return 150
    if _is_date_within_margin(input_date=match_date, margin_days=14):
        return 75
    if _is_date_within_margin(input_date=match_date, margin_days=35):
        return 25
    return 0


def _is_date_within_margin(input_date: date, margin_days: int) -> bool:
    return get_date_today() - timedelta(days=margin_days) <= input_date


def calculate_opponent_weight(
    player_elo: int, opponent_elo: int, previous_match_dates: List[date]
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
    matches_within_margin = [
        d
        for d in previous_match_dates
        if _is_date_within_margin(input_date=d, margin_days=35)
    ]
    previous_matches_added_points = 0
    for match_date in matches_within_margin:
        previous_matches_added_points += _calculate_points_for_match_date(
            match_date=match_date
        )
    return abs_elo_diff + previous_matches_added_points
