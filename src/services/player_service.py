from typing import List

from models import OpponentMatchHistory, Player
from opponent_weight import calculate_opponent_weight
from player_data import fetch_player_match_history
from strategies.models import Opponent, TennisException


def create_player_preferences(
    player_name: str, all_players: List[Player], match_history_days: int
) -> List[str]:
    current_player = next((p for p in all_players if p.name == player_name), None)

    if not current_player:
        raise TennisException(f'No player found named "{player_name}".')

    opponent_data: List[Opponent] = create_opponents_from_players(
        player_name=player_name,
        player_data=all_players,
        match_history_days=match_history_days,
    )

    op_by_weight = sorted(opponent_data, key=lambda i: i.weight, reverse=False)

    player_prefs: List[str] = []
    for op in op_by_weight:
        player_prefs.append(op.name)
    return player_prefs


def create_opponents_from_players(
    player_name: str, player_data: List[Player], match_history_days: int
) -> List[OpponentMatchHistory]:
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
