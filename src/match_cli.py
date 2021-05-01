import json
import logging
from datetime import date
from typing import Dict, List, Optional

from matching.games import StableRoommates
from matching.matchings import SingleMatching

from models import Player
from player_data import (
    fetch_opponent_stats,
    fetch_player_data,
    fetch_player_match_history,
)
from player_preferences import calculate_player_preferences

logging.basicConfig(level=logging.DEBUG)


def _load_player_pool() -> List[str]:
    with open("playerpool.json") as json_file:
        json_data: Dict = json.load(json_file)
        return json_data.get("playerpool", [])


def _create_match_row(
    court_number: int,
    player1: Player,
    player2: Player,
    stats: str,
    previous_match_date: Optional[date],
) -> str:
    result = (
        f"Court {court_number}: "
        f"{player1.name} {player1.elo_points}pts VS {player2.name} {player2.elo_points}pts "
        f"=> {stats} "
    )
    if previous_match_date:
        result = f"{result} ({previous_match_date})"
    return result


def _find_player_by_name(players: List[Player], player_name: str) -> Optional[Player]:
    return next((p for p in players if p.name == player_name), None)


def main():
    logging.info("Fetching player data...")
    player_data = fetch_player_data()

    logging.info("Calculating player preferences...")
    player_preferences = calculate_player_preferences(
        all_players=player_data,
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
        player_history = fetch_player_match_history(
            player=player, match_history_days=31
        )
        opponent_previous_match_dates = sorted(
            player_history.get(opponent.name, []),
            key=lambda x: x.match_date,
            reverse=True,
        )
        previous_match_date = (
            opponent_previous_match_dates[0].match_date
            if opponent_previous_match_dates
            else None
        )
        match_rows.append(
            _create_match_row(
                court_number=court_number,
                player1=player,
                player2=opponent,
                stats=fetch_opponent_stats(
                    player_id=player.id, opponent_id=opponent.id
                ),
                previous_match_date=previous_match_date,
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
