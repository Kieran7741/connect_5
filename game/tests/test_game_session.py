from game.game_session import GameSession, Player

import unittest


class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.game_session = GameSession()
        self.game_session.player_1 = Player('Kieran', 'X')
        self.game_session.player_2 = Player('John', 'O')

    def test_waiting_for_players__not_waiting(self):

        self.assertFalse(self.game_session.waiting_for_players)

    def test_waiting_for_players__waiting(self):

        self.game_session.player_2 = None

        self.assertTrue(self.game_session.waiting_for_players)

    def test_add_player__all_players_already_added(self):

        with self.assertRaises(Exception) as e:
            self.game_session.add_player('Mary')

        self.assertEqual('All players already added.', str(e.exception))
