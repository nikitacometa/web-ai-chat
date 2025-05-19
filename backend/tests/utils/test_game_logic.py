import unittest
from unittest.mock import patch # Import patch
import math
import sys
import os

# Add the parent directory of 'utils' to sys.path to allow 'from utils... import'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_DIR = os.path.dirname(SCRIPT_DIR) # /tests
BACKEND_DIR = os.path.dirname(SERVICE_DIR) # /backend
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from utils.game_logic import calculate_bet_impact

class TestCalculateBetImpact(unittest.TestCase):

    def test_zero_amount(self):
        self.assertEqual(calculate_bet_impact(amount=0, spell="test spell"), 0.0)

    def test_negative_amount(self):
        self.assertEqual(calculate_bet_impact(amount=-10, spell="test spell"), 0.0)

    def test_amount_less_than_one_for_log(self):
        # log10(max(1.0, 0.1)) = log10(1.0) = 0. So impact should be 0.
        # prompt_power = 2 words / 10 = 0.2, clamped to 0.5
        # random_factor is [0.8, 1.2]
        # expected: 0.0 * 0.5 * random_factor = 0.0
        self.assertEqual(calculate_bet_impact(amount=0.1, spell="two words"), 0.0)

    # Patch random.uniform for deterministic tests where needed
    @patch('utils.game_logic.random.uniform') # Path to random.uniform within game_logic.py
    def test_basic_impact_deterministic(self, mock_uniform):
        mock_uniform.return_value = 1.0 # Force random_factor to 1.0
        # amount=10 -> log_bet_term = 1.0
        # spell="four words test spell" (4 words) -> prompt_power=0.5
        # random_factor = 1.0 (mocked)
        # expected_impact = 1.0 * 0.5 * 1.0 = 0.5
        # final impact rounded to 4 decimal places
        self.assertEqual(calculate_bet_impact(amount=10, spell="four words test spell"), 0.5000)
        mock_uniform.assert_called_once_with(0.8, 1.2)

    @patch('utils.game_logic.random.uniform')
    def test_prompt_power_clamping_low_deterministic(self, mock_uniform):
        mock_uniform.return_value = 1.0
        # amount=10 -> log_bet_term = 1.0
        # spell="one" (1 word) -> prompt_power=0.5 (clamped from 0.1)
        # expected_impact = 1.0 * 0.5 * 1.0 = 0.5
        self.assertEqual(calculate_bet_impact(amount=10, spell="one"), 0.5000)
        mock_uniform.assert_called_once_with(0.8, 1.2)

    @patch('utils.game_logic.random.uniform')
    def test_prompt_power_clamping_high_deterministic(self, mock_uniform):
        mock_uniform.return_value = 1.0
        # spell=16 words -> prompt_power=1.5 (clamped from 1.6)
        # expected_impact = 1.0 * 1.5 * 1.0 = 1.5
        self.assertEqual(calculate_bet_impact(amount=10, spell="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16"), 1.5000)
        mock_uniform.assert_called_once_with(0.8, 1.2)

    @patch('utils.game_logic.random.uniform')
    def test_max_impact_clamping_deterministic(self, mock_uniform):
        mock_uniform.return_value = 1.0 # Ensure random factor doesn't lower it below 10 if product is high
        # amount=10^8 -> log_bet_term = 8.0
        # spell=15 words -> prompt_power=1.5
        # random_factor=1.0 (mocked)
        # calculated_impact = 8.0 * 1.5 * 1.0 = 12.0
        # final_impact = min(12.0, 10.0) = 10.0
        self.assertEqual(calculate_bet_impact(amount=10**8, spell="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"), 10.0000)
        mock_uniform.assert_called_once_with(0.8, 1.2)
    
    @patch('utils.game_logic.random.uniform')
    def test_impact_clamped_at_10_even_with_max_random(self, mock_uniform):
        mock_uniform.return_value = 1.2 # Max random factor
        # amount=10^8 -> log_bet_term = 8.0
        # spell=15 words -> prompt_power=1.5
        # random_factor=1.2 (mocked)
        # calculated_impact = 8.0 * 1.5 * 1.2 = 14.4
        # final_impact = min(14.4, 10.0) = 10.0
        self.assertEqual(calculate_bet_impact(amount=10**8, spell="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"), 10.0000)
        mock_uniform.assert_called_once_with(0.8, 1.2)

    @patch('utils.game_logic.random.uniform')
    def test_empty_spell_deterministic(self, mock_uniform):
        mock_uniform.return_value = 1.0
        # amount=10 -> log_bet_term = 1.0
        # spell="" (0 words) -> prompt_power=0.5 (clamped from 0.0, min 0.5)
        # expected_impact = 1.0 * 0.5 * 1.0 = 0.5
        self.assertEqual(calculate_bet_impact(amount=10, spell=""), 0.5000)
        mock_uniform.assert_called_once_with(0.8, 1.2)

if __name__ == '__main__':
    unittest.main() 