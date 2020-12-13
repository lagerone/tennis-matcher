from datetime import date
from operator import itemgetter
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from current_date_provider import get_date_today
from opponent_weight import calculate_opponent_weight


class TennisException(Exception):
    """Raised when something sucks"""


class MatchHistory:
    def __init__(self, match_date: date, opponent_name: str) -> None:
        self.match_date: date = match_date
        self.opponent_name: str = opponent_name


def _create_opponent_history_dict(date: str, opponent: str) -> MatchHistory:
    return MatchHistory(match_date=_create_date(date), opponent_name=opponent)


def _create_date(input: str):
    s = input.split("-")
    return date(int(s[0]), int(s[1]), int(s[2]))


def _get_match_history_by_opponent(
    player: Dict, match_history_days: int
) -> Dict[str, List[MatchHistory]]:
    """
    Returns:
        Dict[str, List[MatchHistory]]: kvp of opponent name and a list of
        matches against that opponent
    """
    url = f'https://www.luckylosertennis.com/ATL/ATLstegen/public/players/matches/{player["id"]}/1'
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find(name="table", class_="table")
    rows: List[Tag] = table.find_all("tr")

    raw_match_history = []
    for row in rows:
        cols = row.find_all("td")
        stripped_cols: List[str] = []
        for c in cols:
            stripped_cols.append(c.text.strip())
        raw_match_history.append([element for element in stripped_cols if element])

    del raw_match_history[-1]
    del raw_match_history[0]

    matches: List[MatchHistory] = []

    for raw_match in raw_match_history:
        opponent_name = raw_match[2] if raw_match[3] == player["name"] else raw_match[3]
        matches.append(
            _create_opponent_history_dict(date=raw_match[1], opponent=opponent_name)
        )

    opponent_matches: Dict[str, List[MatchHistory]] = {}
    for match in matches:
        time_since_match = get_date_today() - match.match_date
        if time_since_match.days >= match_history_days:
            break
        match_history = opponent_matches.get(match.opponent_name, [])
        match_history.append(match)
        opponent_matches[match.opponent_name] = match_history

    return opponent_matches


def _add_weight_to_player_data(
    player_name: str, player_data: List[Dict], match_history_days: int
):
    current_player = next((p for p in player_data if p["name"] == player_name), None)
    if not current_player:
        raise TennisException(f'No player found named "{player_name}".')

    opponents = [player for player in player_data if player["name"] != player_name]

    history = _get_match_history_by_opponent(
        player=current_player, match_history_days=match_history_days
    )
    for opponent in opponents:
        current_opponent = next(
            (p for p in player_data if p["name"] == opponent["name"]), None
        )
        if not current_opponent:
            raise TennisException(
                f'Opponent "{opponent["name"]}" not found in player data.'
            )
        previous_matches = history.get(current_opponent["name"], [])
        current_opponent_latest_match = (
            sorted(
                history.get(current_opponent["name"], []),
                key=lambda x: x.match_date,
                reverse=True,
            )[0]
            if previous_matches
            else None
        )
        current_opponent["weight"] = calculate_opponent_weight(
            player_elo=current_player["elo_points"],
            opponent_elo=current_opponent["elo_points"],
            matches_count=len(history.get(current_opponent["name"], [])),
            latest_match_date=current_opponent_latest_match.match_date
            if current_opponent_latest_match
            else None,
        )
    return opponents


def _create_player_preferences(
    player_name: str, player_data: List[Dict], match_history_days: int
):
    current_player = next((p for p in player_data if p["name"] == player_name), None)

    if not current_player:
        raise TennisException(f'No player found named "{player_name}".')

    opponent_data: List[Dict] = _add_weight_to_player_data(
        player_name=player_name,
        player_data=player_data,
        match_history_days=match_history_days,
    )

    op_by_weight = sorted(opponent_data, key=lambda i: i["weight"], reverse=False)

    player_prefs: List[str] = []
    for op in op_by_weight:
        player_prefs.append(op["name"])
    return player_prefs


def calculate_player_preferences(
    all_players_data: List[Dict], player_pool: List[str], match_history_days: int
) -> Dict[str, List[str]]:
    player_preferences: Dict = {}
    ordered_player_pool_data = sorted(
        [p for p in all_players_data if p["name"] in player_pool],
        key=itemgetter("elo_points"),
        reverse=True,
    )
    for player in ordered_player_pool_data:
        player_preferences[player["name"]] = _create_player_preferences(
            player_name=player["name"],
            player_data=ordered_player_pool_data,
            match_history_days=match_history_days,
        )

    return player_preferences
