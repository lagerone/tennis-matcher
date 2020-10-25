import json
from typing import Dict, List, NamedTuple, Optional

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


def _create_player_dict(name: str, url: str, elo_points: int):
    return {
        "id": url.replace('https://', '').split('/')[6],
        "name": name,
        "url": url,
        "elo_points": elo_points
    }


def _scrape_player_data():
    page = requests.get(
        'https://www.luckylosertennis.com/ATL/ATLstegen/public/rankings/view')

    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find(name='table', class_='table')
    rows: List[Tag] = table.find_all('tr')

    raw_player_data = []
    for row in rows:
        cols = row.find_all('td')
        stripped_cols: List[str] = []
        for c in cols:
            anchor: Optional[Tag] = c.find(name='a')
            if anchor:
                stripped_cols.append(
                    f'https://www.luckylosertennis.com{anchor.get("href", None)}')
            stripped_cols.append(c.text.strip())
        raw_player_data.append(
            [element for element in stripped_cols if element])

    del raw_player_data[-1]
    del raw_player_data[0]

    players: List[Dict] = []

    for player_data in raw_player_data:
        p = _create_player_dict(name=player_data[2], url=player_data[1], elo_points=int(
            str(player_data[3]).replace(' ', '')))
        players.append(p)

    with open('players.json', 'w') as outfile:
        json.dump(obj={"players": players}, indent=2, fp=outfile)


if __name__ == "__main__":
    _scrape_player_data()
