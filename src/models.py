from typing import NamedTuple


class Player(NamedTuple):
    id: str
    name: str
    url: str
    elo_points: int
