from game.game_session import Player

import unittest

"""Bit of a redundant test class but included anyway"""


class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.player = Player('Kieran', 'X')

    def test_player_details__verify_as_expected(self):

        player_details = self.player.player_details()
        self.assertEqual('Kieran', player_details['player_name'])
        self.assertEqual('X', player_details['disc'])
        self.assertTrue(isinstance(player_details['player_id'], str))
