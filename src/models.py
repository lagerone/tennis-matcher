from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, List, NamedTuple


class Player(NamedTuple):
    id: str
    name: str
    url: str
    elo_points: int


class OpponentMatchHistory(NamedTuple):
    match_date: date
    opponent_name: str


class TennisException(Exception):
    """Raised when something sucks"""


class Opponent(NamedTuple):
    name: str
    weight: int


class PlayerPreferencesStrategy(ABC):
    @abstractmethod
    def create_player_preferences(
        self, match_history_days: int
    ) -> Dict[str, List[str]]:
        """Creates a dictionary of player names and a ordered list of preferred opponent names.

        Args:
            match_history_days (int):

        Returns:
            Dict[str, List[str]]: A dictionary of player pool names and a list of
            player preference names.
        """
