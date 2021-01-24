import json
import logging
from typing import Dict, List, Optional

from matching.games import StableRoommates
from matching.matchings import SingleMatching

from models import Player
from player_data import fetch_player_data
from player_preferences import calculate_player_preferences

logging.basicConfig(level=logging.DEBUG)


def _load_player_pool() -> List[str]:
    with open("playerpool.json") as json_file:
        json_data: Dict = json.load(json_file)
        return json_data.get("playerpool", [])


def _create_match_row(court_number: int, player1: Player, player2: Player) -> str:
    return (
        f"Court {court_number}: "
        f"{player1.name} {player1.elo_points}pts VS {player2.name} {player2.elo_points}pts"
    )


def _find_player_by_name(players: List[Player], player_name: str) -> Optional[Player]:
    return next((p for p in players if p.name == player_name), None)


def main():
    logging.info("Fetching player data...")
    player_data = fetch_player_data()

    logging.info("Calculating player preferences...")
    player_preferences = calculate_player_preferences(
        all_players_data=player_data,
        player_pool=_load_player_pool(),
        match_history_days=90,
    )

    logging.info("Calculating matchups...")
    game = StableRoommates.create_from_dictionary(player_prefs=player_preferences)
    result: SingleMatching = game.solve()

    matched_players: List[str] = []
    match_rows: List[str] = []
    court_number = 1
    for p, o in result.items():
        player_name = p.name
        opponent_name = o.name
        if player_name in matched_players:
            continue
        player = _find_player_by_name(players=player_data, player_name=player_name)
        if not player:
            raise MatchException(
                f'Could not find player "{player_name}" in player data.'
            )
        opponent = _find_player_by_name(players=player_data, player_name=opponent_name)
        if not player or not opponent:
            raise MatchException(
                f'Could not find opponent "{opponent_name}" in player data.'
            )
        matched_players += [player_name, opponent_name]
        match_rows.append(
            _create_match_row(
                court_number=court_number, player1=player, player2=opponent
            )
        )
        court_number += 1

    with open("matchup-result.txt", "w") as file:
        file.write("\n".join(match_rows))

    logging.info('Done! Matchup result written to "matchup-result.txt".')


class MatchException(Exception):
    """Raised when this program sucks"""


if __name__ == "__main__":
    main()
