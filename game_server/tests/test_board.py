from game_server.game_session import Board

import unittest
from unittest.mock import patch


class TestBoard(unittest.TestCase):

    def setUp(self):

        self.board = Board(['X', 'O'])

    def test_drop_disk_successful(self):
        self.board.drop_disc(1, 'X')
        self.assertTrue('X' in self.board.board_matrix[1])

    def test_drop_disk__invalid_disk(self):

        with self.assertRaises(Exception) as e:
            self.board.drop_disc(1, 'Y')

        self.assertEqual('Invalid disc: Y', str(e.exception))

    def test_drop_disk__no_space_left_in_column(self):

        self.board.board_matrix[1] = ['']  # This represents a full column

        with self.assertRaises(Exception) as e:
            self.board.drop_disc(1, 'X')

        self.assertEqual('No space left in column: 1', str(e.exception))

    def test_drop_disk__invalid_column(self):

        with self.assertRaises(Exception) as e:
            self.board.drop_disc(20, 'X')
        self.assertEqual('Invalid column: 20', str(e.exception))

    @patch('game_server.game_session.Board.check_rows_and_cols', return_value='X')
    def test_check_for_winner__winner_found(self, _):
        self.assertEqual('X', self.board.check_for_winner())

    @patch('game_server.game_session.Board.check_rows_and_cols', return_value=None)
    @patch('game_server.game_session.Board.check_diagonals', return_value=None)
    def test_check_for_winner__no_winner_found(self, *_):
        self.assertIsNone(self.board.check_for_winner())

    def test_check_diagonals__no_winner(self):

        self.assertIsNone(self.board.check_diagonals())

    @patch('builtins.print')
    def test_check_diagonals__winner(self, _):
        self.board.board_matrix[0][0] = 'X'
        self.board.board_matrix[1][1] = 'X'
        self.board.board_matrix[2][2] = 'X'
        self.board.board_matrix[3][3] = 'X'
        self.board.board_matrix[4][4] = 'X'

        self.assertEqual('X', self.board.check_diagonals())

    def test_check_row_and_col__no_winner(self):
        self.assertIsNone(self.board.check_rows_and_cols())

    @patch('builtins.print')
    def test_check_row_and_col__row_winner(self, mock_print):

        self.board.board_matrix[0][0] = 'X'
        self.board.board_matrix[1][0] = 'X'
        self.board.board_matrix[2][0] = 'X'
        self.board.board_matrix[3][0] = 'X'
        self.board.board_matrix[4][0] = 'X'

        self.assertEqual('X', self.board.check_rows_and_cols())
        mock_print.assert_called_once_with('Winner by connecting a row')

    @patch('builtins.print')
    def test_check_row_and_col__col_winner(self, mock_print):

        self.board.board_matrix[2] = ['X', 'X', 'X', 'X', 'X', '_']

        self.assertEqual('X', self.board.check_rows_and_cols())
        mock_print.assert_called_once_with('Winner by connecting a column')

    def test_check_if_line_has_five_in_a_row__winner(self):

        self.assertEqual('X', self.board.check_if_line_has_five_in_a_row(['X', 'X', 'X', 'X', 'X', '_']))

    def test_check_if_line_has_five_in_a_row__no_winner(self):

        self.assertIsNone(self.board.check_if_line_has_five_in_a_row(['X', 'X', '_', '_', '_', '_']))

if __name__ == '__main__':
    unittest.main()
