# Tennis matcher

Creates tennis matches for Stegen at ATL Lund. Uses data from [luckylosertennis.com](https://www.luckylosertennis.com/) to calculate the matchups.

It uses [Irvin's solution](https://www.sciencedirect.com/science/article/abs/pii/0196677485900331) to the [stable roommates problem](https://en.wikipedia.org/wiki/Stable_roommates_problem) from the [python matching package](https://github.com/daffidwilde/matching) to create the matchups.

To calculate each players preferences a weight for all opponents are calculated by which the opponents are ordered.

```py
# file player_preferences.py

def _calculate_opponent_weight(player_elo: int, opponent_elo: int, matches_count: int):
    """
    The `matches_count` is the number of matches the player
    has played against the opponent in the last 90 days.
    """
    abs_elo_diff = abs(player_elo - opponent_elo)
    if matches_count == 0:
        return abs_elo_diff
    return abs(int(round(abs_elo_diff * matches_count)))
```

## Install

1. Clone this repository
2. Create a virtual environment, e.g. `python3 -m venv venv`
3. Activate the virtual environment, e.g. `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r src/dev_requirements.txt
   pip install -r src/requirements.txt
   ```

## Usage

1. Create a file named `playerpool.json` in the project root. Add current players to the player pool. The name of the players must be their exact name at [luckylosertennis.com](https://www.luckylosertennis.com/).

   ```json
   {
     "playerpool": [
       "Name of player 1",
       "Name of player 2",
       "Name of player 3",
       "Name of player 4"
     ]
   }
   ```

2. Create the matchups:

   ```bash
   python src/match_cli.py
   ```

The matchups will be written to a file named `matchup-result.txt`.
