from datetime import date
from typing import Dict, List, NamedTuple

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from current_date_provider import get_date_today
from models import Player
from opponent_weight import calculate_opponent_weight


class TennisException(Exception):
    """Raised when something sucks"""


class OpponentMatchHistory(NamedTuple):
    match_date: date
    opponent_name: str


class Opponent(NamedTuple):
    name: str
    weight: int


def _create_opponent_history(date: str, opponent: str) -> OpponentMatchHistory:
    return OpponentMatchHistory(match_date=_create_date(date), opponent_name=opponent)


def _create_date(input: str):
    s = input.split("-")
    return date(int(s[0]), int(s[1]), int(s[2]))


def _get_match_history_by_opponent(
    player: Player, match_history_days: int
) -> Dict[str, List[OpponentMatchHistory]]:
    """
    Returns:
        Dict[str, List[MatchHistory]]: kvp of opponent name and a list of
        matches against that opponent
    """
    url = f"https://www.luckylosertennis.com/ATL/ATLstegen/public/players/matches/{player.id}/1"
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

    del raw_match_history[0]

    matches: List[OpponentMatchHistory] = []

    for raw_match in raw_match_history:
        opponent_name = raw_match[2] if raw_match[3] == player.name else raw_match[3]
        matches.append(
            _create_opponent_history(date=raw_match[1], opponent=opponent_name)
        )

    opponent_matches: Dict[str, List[OpponentMatchHistory]] = {}
    for match in matches:
        time_since_match = get_date_today() - match.match_date
        if time_since_match.days >= match_history_days:
            break
        match_history = opponent_matches.get(match.opponent_name, [])
        match_history.append(match)
        opponent_matches[match.opponent_name] = match_history

    return opponent_matches


def _create_opponents_from_players(
    player_name: str, player_data: List[Player], match_history_days: int
) -> List[Opponent]:
    current_player = next((p for p in player_data if p.name == player_name), None)
    if not current_player:
        raise TennisException(f'No player found named "{player_name}".')

    opponent_players = [player for player in player_data if player.name != player_name]

    opponent_history = _get_match_history_by_opponent(
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
        current_opponent_latest_match = (
            sorted(
                opponent_history.get(current_opponent.name, []),
                key=lambda x: x.match_date,
                reverse=True,
            )[0]
            if previous_matches
            else None
        )

        current_opponent_weight = calculate_opponent_weight(
            player_elo=current_player.elo_points,
            opponent_elo=current_opponent.elo_points,
            latest_match_date=current_opponent_latest_match.match_date
            if current_opponent_latest_match
            else None,
        )
        result.append(Opponent(name=opponent.name, weight=current_opponent_weight))

    return result


def _create_player_preferences(
    player_name: str, player_data: List[Player], match_history_days: int
) -> List[str]:
    current_player = next((p for p in player_data if p.name == player_name), None)

    if not current_player:
        raise TennisException(f'No player found named "{player_name}".')

    opponent_data: List[Opponent] = _create_opponents_from_players(
        player_name=player_name,
        player_data=player_data,
        match_history_days=match_history_days,
    )

    op_by_weight = sorted(opponent_data, key=lambda i: i.weight, reverse=False)

    player_prefs: List[str] = []
    for op in op_by_weight:
        player_prefs.append(op.name)
    return player_prefs


def _normalize_player_pool(player_pool: List[Player]) -> List[Player]:
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


def calculate_player_preferences(
    all_players_data: List[Player], player_pool: List[str], match_history_days: int
) -> Dict[str, List[str]]:
    """Creates a dictionary of player names and a ordered list of preferred opponent names.

    Args:
        all_players_data (List[Player]):
        player_pool (List[str]):
        match_history_days (int):

    Returns:
        Dict[str, List[str]]:
    """
    player_preferences: Dict = {}
    ordered_player_pool_data = sorted(
        [p for p in all_players_data if p.name in player_pool],
        key=lambda p: p.elo_points,
        reverse=True,
    )

    for player_name in player_pool:
        player_exists = next(
            (p for p in all_players_data if p.name == player_name), None
        )
        if not player_exists:
            raise TennisException(
                f'Player name "{player_name}" could not be found in the rankings.'
            )

    for player in ordered_player_pool_data:
        player_preferences[player.name] = _create_player_preferences(
            player_name=player.name,
            player_data=_normalize_player_pool(ordered_player_pool_data),
            match_history_days=match_history_days,
        )

    return player_preferences
