from datetime import date
from unittest import TestCase
from unittest.mock import Mock, patch

from opponent_weight import calculate_opponent_weight


class TestCalculateOpponentWeight(TestCase):
    def test_should_calculate_weight_without_previous_matches(self):
        # Act
        result = calculate_opponent_weight(
            player_elo=1000, opponent_elo=900, matches_count=0
        )

        # Assert
        self.assertEqual(result, 100)

    @patch("opponent_weight.get_date_today")
    def test_should_weigh_matches_within_date_range_higher(
        self, mock_get_date_today: Mock
    ):
        # Arrange
        opponent_elo = 900
        matches_count = 2
        mock_get_date_today.return_value = date(2020, 12, 15)
        latest_match_date_within_7_days = date(2020, 12, 8)
        latest_match_date_within_14_days = date(2020, 12, 2)

        # Act
        result1 = calculate_opponent_weight(
            player_elo=1000,
            opponent_elo=opponent_elo,
            matches_count=matches_count,
            latest_match_date=latest_match_date_within_7_days,
        )
        result2 = calculate_opponent_weight(
            player_elo=1000,
            opponent_elo=opponent_elo,
            matches_count=matches_count,
            latest_match_date=latest_match_date_within_14_days,
        )
        result3 = calculate_opponent_weight(
            player_elo=1000, opponent_elo=opponent_elo, matches_count=0
        )

        # Assert
        self.assertTrue(result1 > result2)
        self.assertTrue(result2 > result3)
