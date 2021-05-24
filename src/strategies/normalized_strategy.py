from typing import Dict, List

from opponent_weight import calculate_opponent_weight
from player_data import fetch_player_match_history

from models import OpponentMatchHistory, Player
from strategies.models import Opponent, PlayerPreferencesStrategy, TennisException


class NormalizedStrategy(PlayerPreferencesStrategy):
    def __init__(self, player_pool_names: List[str], all_players: List[Player]) -> None:
        self._player_pool_names = player_pool_names
        self._all_players = all_players

    def create_player_preferences(
        self, match_history_days: int
    ) -> Dict[str, List[str]]:
        player_preferences: Dict = {}
        for player in self._all_players:
            player_preferences[player.name] = self._create_player_preferences(
                player_name=player.name,
                match_history_days=match_history_days,
            )

        return player_preferences

    def _create_opponents_from_players(
        self, player_name: str, player_data: List[Player], match_history_days: int
    ) -> List[OpponentMatchHistory]:
        current_player = next((p for p in player_data if p.name == player_name), None)
        if not current_player:
            raise TennisException(f'No player found named "{player_name}".')

        opponent_players = [
            player for player in player_data if player.name != player_name
        ]

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
        self, player_name: str, match_history_days: int
    ) -> List[str]:
        current_player = next(
            (p for p in self._all_players if p.name == player_name), None
        )

        if not current_player:
            raise TennisException(f'No player found named "{player_name}".')

        opponent_data: List[Opponent] = self._create_opponents_from_players(
            player_name=player_name,
            player_data=self._all_players,
            match_history_days=match_history_days,
        )

        op_by_weight = sorted(opponent_data, key=lambda i: i.weight, reverse=False)

        player_prefs: List[str] = []
        for op in op_by_weight:
            player_prefs.append(op.name)
        return player_prefs

    def _create_normalized_player_pool(
        self, all_players: List[Player], player_pool_names: List[str]
    ) -> List[Player]:
        valid_player_pool = [p for p in all_players if p.name in player_pool_names]
        sorted_pp_asc = sorted(
            valid_player_pool,
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
