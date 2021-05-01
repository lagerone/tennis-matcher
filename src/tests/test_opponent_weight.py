from datetime import datetime, timedelta, timezone
from unittest import TestCase
from unittest.mock import Mock, patch

from opponent_weight import calculate_opponent_weight


class TestCalculateOpponentWeight(TestCase):
    def test_should_calculate_weight_without_previous_match_date(self):
        # Act
        result = calculate_opponent_weight(player_elo=1000, opponent_elo=900)

        # Assert
        self.assertEqual(result, 100)

    @patch("opponent_weight.get_date_today")
    def test_should_weigh_matches_within_date_range_higher(
        self, mock_get_date_today: Mock
    ):
        # Arrange
        player_elo = 1000
        opponent_elo = 900
        datetime_now = datetime.now(tz=timezone.utc)
        mock_get_date_today.return_value = datetime_now
        latest_match_date_within_7_days = datetime_now - timedelta(days=7)
        latest_match_date_within_14_days = datetime_now - timedelta(days=14)
        latest_match_date_within_35_days = datetime_now - timedelta(days=35)

        # Act
        result1 = calculate_opponent_weight(
            player_elo=player_elo,
            opponent_elo=opponent_elo,
            previous_match_dates=latest_match_date_within_7_days,
        )
        result2 = calculate_opponent_weight(
            player_elo=player_elo,
            opponent_elo=opponent_elo,
            previous_match_dates=latest_match_date_within_14_days,
        )
        result3 = calculate_opponent_weight(
            player_elo=player_elo,
            opponent_elo=opponent_elo,
            previous_match_dates=latest_match_date_within_35_days,
        )
        result4 = calculate_opponent_weight(
            player_elo=player_elo, opponent_elo=opponent_elo
        )

        # Assert
        self.assertTrue(result1 > result2, f"result1: {result1} vs result2: {result2}")
        self.assertTrue(result2 > result3, f"result2: {result2} vs result3: {result3}")
        self.assertTrue(result3 > result4, f"result4: {result3} vs result4: {result4}")

    @patch("opponent_weight.get_date_today")
    def test_should_weigh_matches_within_date_range_lower_than_large_elo_diff(
        self, mock_get_date_today: Mock
    ):
        # Arrange
        player_elo = 1000
        datetime_now = datetime.now(tz=timezone.utc)
        mock_get_date_today.return_value = datetime_now
        latest_match_date_within_7_days = datetime_now - timedelta(days=7)
        latest_match_date_within_14_days = datetime_now - timedelta(days=14)

        # Act
        result1 = calculate_opponent_weight(
            player_elo=player_elo,
            opponent_elo=900,
            previous_match_dates=latest_match_date_within_7_days,
        )
        result2 = calculate_opponent_weight(
            player_elo=player_elo,
            opponent_elo=900,
            previous_match_dates=latest_match_date_within_14_days,
        )
        result3 = calculate_opponent_weight(player_elo=player_elo, opponent_elo=650)

        # Assert
        self.assertTrue(result1 < result3, f"result1: {result1} vs result3: {result3}")
        self.assertTrue(result2 < result3, f"result2: {result2} vs result3: {result3}")
