import json
from typing import Dict

from matching.games import StableRoommates


def _load_player_preferences() -> Dict:
    with open('player_preferences.json') as json_file:
        return json.load(json_file)


def main():
    player_prefs = _load_player_preferences()
    game = StableRoommates.create_from_dictionary(player_prefs=player_prefs)
    result = game.solve()
    print(result)


if __name__ == "__main__":
    main()
