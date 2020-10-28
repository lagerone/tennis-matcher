import json
import logging
from typing import Dict, List

from matching.games import StableRoommates

from player_data import fetch_player_data
from player_preferences import calculate_player_preferences

logging.basicConfig(level=logging.INFO)


def _load_player_pool() -> List[str]:
    with open('playerpool.json') as json_file:
        json_data: Dict = json.load(json_file)
        return json_data.get('playerpool')


def main():
    logging.info("Fetching player data...")
    player_data = fetch_player_data()

    logging.info("Calculating player preferences...")
    player_preferences = calculate_player_preferences(
        all_players_data=player_data, player_pool=_load_player_pool(), match_history_days=90)

    logging.info("Calculating matchups...")
    game = StableRoommates.create_from_dictionary(
        player_prefs=player_preferences)
    result = game.solve()

    matched_players: List[str] = []
    matches: List[str] = []
    for player, opponent in result.items():
        if player in matched_players:
            continue
        matched_players += [player, opponent]
        matches.append(f'{player} vs {opponent}')

    with open('matchup-result.txt', 'w') as file:
        file.write('\n'.join(matches))

    logging.info(f'Done! Matchup result written to "matchup-result.txt".')


if __name__ == "__main__":
    main()
