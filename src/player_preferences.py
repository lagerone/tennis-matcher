from typing import Dict, List, NamedTuple

from models import Player
from opponent_weight import calculate_opponent_weight
from player_data import fetch_player_match_history


class TennisException(Exception):
    """Raised when something sucks"""


class Opponent(NamedTuple):
    name: str
    weight: int


def _create_opponents_from_players(
    player_name: str, player_data: List[Player], match_history_days: int
) -> List[Opponent]:
    current_player = next((p for p in player_data if p.name == player_name), None)
    if not current_player:
        raise TennisException(f'No player found named "{player_name}".')

    opponent_players = [player for player in player_data if player.name != player_name]

    opponent_history = fetch_player_match_history(
        player=current_player, match_history_days=match_history_days
    )

    result: List[Opponent] = []
    for opponent in opponent_players:
        current_opponent = next(
            (p for p in player_data if p.name == opponent.name), None
        )
        if not current_opponent:
            raise TennisException(
                f'Opponent "{opponent.name}" not found in player data.'
            )
        previous_matches = opponent_history.get(current_opponent.name, [])
        current_opponent_weight = calculate_opponent_weight(
            player_elo=current_player.elo_points,
            opponent_elo=current_opponent.elo_points,
            previous_match_dates=[pm.match_date for pm in previous_matches],
        )
        result.append(Opponent(name=opponent.name, weight=current_opponent_weight))

    return result


def _create_player_preferences(
    player_name: str, player_pool: List[Player], match_history_days: int
) -> List[str]:
    current_player = next((p for p in player_pool if p.name == player_name), None)

    if not current_player:
        raise TennisException(f'No player found named "{player_name}".')

    opponent_data: List[Opponent] = _create_opponents_from_players(
        player_name=player_name,
        player_data=player_pool,
        match_history_days=match_history_days,
    )

    op_by_weight = sorted(opponent_data, key=lambda i: i.weight, reverse=False)

    player_prefs: List[str] = []
    for op in op_by_weight:
        player_prefs.append(op.name)
    return player_prefs


def _normalize_and_sort_player_pool(player_pool: List[Player]) -> List[Player]:
    sorted_pp_asc = sorted(
        player_pool,
        key=lambda p: p.elo_points,
        reverse=False,
    )
    result: List[Player] = []
    previous_elo = 1000
    for p in sorted_pp_asc:
        normalized_elo = previous_elo + 10
        result.append(
            Player(id=p.id, name=p.name, elo_points=normalized_elo, url=p.url)
        )
        previous_elo = normalized_elo

    return sorted(result, key=lambda p: p.elo_points, reverse=True)


# def _write_to_json_file(filename: str, data: Dict) -> None:
#     with open(filename, "w", encoding="utf-8") as file:
#         json.dump(data, file, ensure_ascii=False, indent=2, default=str)


def calculate_player_preferences(
    all_players: List[Player], player_pool: List[str], match_history_days: int
) -> Dict[str, List[str]]:
    """Creates a dictionary of player names and a ordered list of preferred opponent names.

    Args:
        all_players (List[Player]):
        player_pool (List[str]):
        match_history_days (int):

    Returns:
        Dict[str, List[str]]:
    """
    normalized_and_sorted_player_pool = _normalize_and_sort_player_pool(
        player_pool=[p for p in all_players if p.name in player_pool]
    )

    for player_name in player_pool:
        player_exists = next((p for p in all_players if p.name == player_name), None)
        if not player_exists:
            raise TennisException(
                f'Player name "{player_name}" could not be found in the rankings.'
            )

    player_preferences: Dict = {}
    for player in normalized_and_sorted_player_pool:
        player_preferences[player.name] = _create_player_preferences(
            player_name=player.name,
            player_pool=normalized_and_sorted_player_pool,
            match_history_days=match_history_days,
        )

    return player_preferences
