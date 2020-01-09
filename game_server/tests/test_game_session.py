from game_server.game_session import GameSession, Player

import unittest
from unittest.mock import Mock, patch


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

    def test_add_player__player_name_already_taken(self):

        self.game_session.player_2 = None
        with self.assertRaises(Exception) as e:
            self.game_session.add_player('Kieran') # same as player 1

        self.assertEqual('Name: Kieran already in use.', str(e.exception))

    @patch('builtins.print')
    def test_add_player__add_player_1(self, _):

        self.game_session.player_1 = None
        self.game_session.add_player('Kieran')
        self.assertTrue(self.game_session.player_1.player_name == 'Kieran')

    @patch('builtins.print')
    def test_add_player__add_player_2(self, _):

        self.game_session.player_2 = None
        self.game_session.add_player('John')
        self.assertTrue(self.game_session.player_2.player_name == 'John')

    def test_game_details__initial_game_details(self):
        self.game_session.game_id = '123'
        self.game_session.player_1 = None
        self.game_session.player_2 = None

        game_status = self.game_session.game_details()
        self.assertEqual(game_status['state'], 'WAITING FOR PLAYERS')
        self.assertEqual(game_status['player_turn'], None)
        self.assertEqual(game_status['winner'], None)

    def test_next_player_turn__default_player_1(self):

        self.assertEqual(self.game_session.next_player_turn(), self.game_session.player_1.player_id)

    def test_next_player_turn__player_2(self):
        self.game_session.board.last_disc = self.game_session.player_1.disc
        self.assertEqual(self.game_session.next_player_turn(), self.game_session.player_2.player_id)

    def test_check_for_winner__winner_found(self):
        mock_board = Mock()
        mock_board.check_for_winner.return_value = 'X'
        self.game_session.board = mock_board

        self.game_session.check_for_winner()
        self.assertEqual(self.game_session.winner, self.game_session.player_1.player_id)

    def test_check_for_winner__no_winner(self):
        mock_board = Mock()
        mock_board.check_for_winner.return_value = None
        self.game_session.board = mock_board
        self.game_session.check_for_winner()
        self.assertIsNone(self.game_session.winner)


if __name__ == '__main__':
    unittest.main()
