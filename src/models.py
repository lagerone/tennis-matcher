from datetime import date
from typing import NamedTuple


class Player(NamedTuple):
    id: str
    name: str
    url: str
    elo_points: int


class OpponentMatchHistory(NamedTuple):
    match_date: date
    opponent_name: str
