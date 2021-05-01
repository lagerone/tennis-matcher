from datetime import date
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from current_date_provider import get_date_today
from models import OpponentMatchHistory, Player


def _create_player(name: str, url: str, elo_points: int) -> Player:
    return Player(
        id=url.replace("https://", "").split("/")[6],
        name=name,
        url=url,
        elo_points=elo_points,
    )


def fetch_opponent_stats(player_id: str, opponent_id: str) -> str:
    url = f"https://www.luckylosertennis.com/ATL/ATLstegen/public/players/view/{player_id}"
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find(name="table", class_="table")

    if not table:
        return "never played"

    rows: List[Tag] = table.find_all("tr")

    raw_player_data = []
    for row in rows:
        cols = row.find_all("td")
        stripped_cols: List[str] = []
        for c in cols:
            anchor: Optional[Tag] = c.find(name="a")
            if anchor:
                stripped_cols.append(anchor.get("href"))
            else:
                stripped_cols.append(c.text.strip())
        raw_player_data.append([element for element in stripped_cols if element])

    del raw_player_data[0]

    opponent_row = next(
        (row for row in raw_player_data if str(row[0]).endswith(f"/{opponent_id}")),
        None,
    )
    if not opponent_row:
        return "never played"
    return f"{opponent_row[1]}-{opponent_row[2]}-{opponent_row[3]}"


def fetch_player_data() -> List[Player]:
    page = requests.get(
        "https://www.luckylosertennis.com/ATL/ATLstegen/public/rankings/view"
    )

    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find(name="table", class_="table")
    rows: List[Tag] = table.find_all("tr")

    raw_player_data = []
    for row in rows:
        cols = row.find_all("td")
        stripped_cols: List[str] = []
        for c in cols:
            anchor: Optional[Tag] = c.find(name="a")
            if anchor:
                stripped_cols.append(
                    f'https://www.luckylosertennis.com{anchor.get("href", None)}'
                )
            stripped_cols.append(c.text.strip())
        raw_player_data.append([element for element in stripped_cols if element])

    # delete table header and footer
    del raw_player_data[-1]
    del raw_player_data[0]

    players: List[Player] = []

    for player_data in raw_player_data:
        p = _create_player(
            name=player_data[2],
            url=player_data[1],
            elo_points=int(str(player_data[3]).replace(" ", "")),
        )
        players.append(p)

    return players


def _create_date(input: str):
    s = input.split("-")
    return date(int(s[0]), int(s[1]), int(s[2]))


def _create_opponent_history(date: str, opponent: str) -> OpponentMatchHistory:
    return OpponentMatchHistory(match_date=_create_date(date), opponent_name=opponent)


def fetch_player_match_history(
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
