from abc import ABC, abstractmethod
from typing import Dict, List, NamedTuple


class TennisException(Exception):
    """Raised when something sucks"""


class Opponent(NamedTuple):
    name: str
    weight: int


class PlayerPreferencesStrategy(ABC):
    """PlayerPreferencesStrategy"""

    @abstractmethod
    def create_player_preferences(
        self, match_history_days: int
    ) -> Dict[str, List[str]]:
        """create_player_preferences"""
