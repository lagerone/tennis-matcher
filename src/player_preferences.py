from datetime import datetime
from operator import itemgetter
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


class TennisException(Exception):
    """Raised when something sucks"""


def _create_opponent_history_dict(date: str, opponent: str):
    return {
        "date": date,
        "opponent": opponent
    }


def _create_date(input: str):
    s = input.split('-')
    return datetime(int(s[0]), int(s[1]), int(s[2]))


def _get_opponents_played_count(player: Dict, match_history_days: int):
    url = f'https://www.luckylosertennis.com/ATL/ATLstegen/public/players/matches/{player["id"]}/1'
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find(name='table', class_='table')
    rows: List[Tag] = table.find_all('tr')

    raw_match_history = []
    for row in rows:
        cols = row.find_all('td')
        stripped_cols: List[str] = []
        for c in cols:
            stripped_cols.append(c.text.strip())
        raw_match_history.append(
            [element for element in stripped_cols if element])

    del raw_match_history[-1]
    del raw_match_history[0]

    matches: List[Dict] = []

    for match in raw_match_history:
        opponent_name = match[2] if match[3] == player['name'] else match[3]
        matches.append(_create_opponent_history_dict(
            date=match[1], opponent=opponent_name))

    opponents_played_count_dict: Dict = {}
    for match in matches:
        time_since_match = datetime.now() - _create_date(match['date'])
        if time_since_match.days >= match_history_days:
            break
        if opponents_played_count_dict.get(match['opponent']):
            opponents_played_count_dict[match['opponent']] += 1
        else:
            opponents_played_count_dict[match['opponent']] = 1

    return opponents_played_count_dict


def _add_weight_to_player_data(player_name: str, player_data: List[Dict], match_history_days: int):
    current_player = next(
        (p for p in player_data if p['name'] == player_name), None)
    if not current_player:
        raise TennisException(f'No player found named "{player_name}".')

    opponents = [
        player for player in player_data if player['name'] != player_name]

    history = _get_opponents_played_count(
        player=current_player, match_history_days=match_history_days)
    for opponent in opponents:
        current_opponent = next(
            (p for p in player_data if p['name'] == opponent['name']), None)
        if not current_opponent:
            raise TennisException(
                f'Opponent "{opponent["name"]}" not found in player data.')
        current_opponent_match_count = history.get(current_opponent['name'], 0)
        current_opponent['weight'] = _calculate_opponent_weight(
            current_player['elo_points'], current_opponent['elo_points'], current_opponent_match_count)
    return opponents


def _calculate_opponent_weight(player_elo: int, opponent_elo: int, matches_count: int):
    abs_elo_diff = abs(player_elo - opponent_elo)
    if matches_count == 0:
        return abs_elo_diff
    return abs(int(round(abs_elo_diff * matches_count)))


def _create_player_preferences(player_name: str, player_data: List[Dict], match_history_days: int):
    current_player = next(
        (p for p in player_data if p['name'] == player_name), None)

    if not current_player:
        raise TennisException(f'No player found named "{player_name}".')

    opponent_data: List[Dict] = _add_weight_to_player_data(
        player_name=player_name, player_data=player_data, match_history_days=match_history_days)

    op_by_weight = sorted(
        opponent_data, key=lambda i: i['weight'], reverse=False)

    player_prefs: List[str] = []
    for op in op_by_weight:
        player_prefs.append(op['name'])
    return player_prefs


def calculate_player_preferences(all_players_data: List[Dict], player_pool: List[str], match_history_days: int) -> Dict[str, List[str]]:
    player_preferences: Dict = {}
    ordered_player_pool_data = sorted([
        p for p in all_players_data if p["name"] in player_pool], key=itemgetter("elo_points"), reverse=True)
    for player in ordered_player_pool_data:
        player_preferences[player["name"]] = _create_player_preferences(
            player_name=player["name"], player_data=ordered_player_pool_data, match_history_days=match_history_days)

    return player_preferences
