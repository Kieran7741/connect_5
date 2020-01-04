from client import Client, make_request_to_server, select_column, start_game, create_client

import unittest
from unittest.mock import Mock, patch


class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = Client('Kieran')

    @patch('requests.get')
    def test_make_request_to_server__get(self, mock_get):

        make_request_to_server('some/endpoint')
        mock_get.assert_called()

    @patch('requests.post')
    def test_make_request_to_server__post(self, mock_post):

        make_request_to_server('some/endpoint', method='POST', body={'body': 'hello'})
        mock_post.assert_called()

    @patch('builtins.print')
    @patch('client.make_request_to_server')
    def test_establish_connection(self, mock_make_request, _):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {'game_id': '123', 'player': {'player_id': '456', 'disc': 'X'}}
        mock_make_request.return_value = mock_response

        self.assertTrue(self.client.establish_connection())
        self.assertEqual(self.client.disc, 'X')
        self.assertEqual(self.client.game_id, '123')
        self.assertEqual(self.client.player_id, '456')
    
    @patch('builtins.print')
    @patch('time.sleep')
    @patch('client.make_request_to_server', side_effect=Exception)
    def test_establish_connection__cannot_connect(self, *_):
      
        self.assertRaises(Exception, self.client.establish_connection)

    @patch('client.make_request_to_server')
    def test_drop_disc__no_winner_after_drop(self, mock_make_request):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {'game_id': '123', 'winner': None, 'state': 'PLAYING'}
        mock_make_request.return_value = mock_response
        self.client.drop_disc(5)
        self.assertIsNone(self.client.winner)
        self.assertEqual(self.client.game_state, 'PLAYING')

    @patch('client.make_request_to_server')
    def test_drop_disc__winner_after_drop(self, mock_make_request):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {'game_id': '123', 'winner': '456', 'state': 'WINNER'}
        mock_make_request.return_value = mock_response
        self.client.player_id = '456'
        self.client.drop_disc(5)
        self.assertEqual(self.client.winner , '456')
        self.assertEqual(self.client.game_state, 'WINNER')
    
    @patch('client.make_request_to_server')
    def test_drop_disc__invalid_column(self, mock_make_request):
        mock_response = Mock(status_code=400)
        mock_response.json.return_value = {'message': 'Invalid column: 5'}
        mock_make_request.return_value = mock_response
        with self.assertRaises(Exception) as e:
            self.client.drop_disc(5)

        self.assertEqual('Invalid column: 5' , str(e.exception))

    @patch('builtins.print')
    @patch('client.make_request_to_server')
    def test_poll_until_other_player_connected__other_player_joined(self, mock_make_request, _):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {'opponent': True}
        mock_make_request.return_value = mock_response

        self.assertTrue(self.client.poll_until_other_player_connected())

    @patch('time.sleep')
    @patch('builtins.print')
    @patch('client.make_request_to_server')
    def test_poll_until_other_player_connected(self, *_):

        with self.assertRaises(Exception) as e:
            self.client.poll_until_other_player_connected()
        
        self.assertEqual('No opponent joined within the timeout of 60 seconds.', str(e.exception))
        
    @patch('builtins.print')
    @patch('time.time', side_effect=[0, 1])
    @patch('client.Client.get_game_status', return_value={'state': 'PLAYING', 'winner': None, 'player_turn': '123'})
    def test_poll_until_turn__clients_turn(self, *_):
        self.client.player_id = '123'
        
        self.assertTrue(self.client.poll_until_turn())

    @patch('builtins.print')
    @patch('time.time', side_effect=[0, 1])
    @patch('client.Client.get_game_status', return_value={'state': 'WINNER', 'winner': '123', 'player_turn': '123'})
    def test_poll_until_turn__winner_found(self, *_):
        
        self.assertFalse(self.client.poll_until_turn())
        self.assertEqual(self.client.game_state, 'WINNER')

    @patch('time.sleep')
    @patch('time.time', side_effect=[0, 1, 100])
    @patch('client.Client.get_game_status', return_value={'state': 'PLAYING', 'winner': None, 'player_turn': '456'})
    @patch('builtins.print')
    def test_poll_until_turn__opponent_disconnected(self, mock_print, *_):
        self.client.player_id = '123'
        self.assertFalse(self.client.poll_until_turn())

        mock_print.assert_called_with('Opponent took to long to respond. You are the winner.')
        self.assertEqual(self.client.player_id, self.client.winner)

    @patch('client.Client.get_game_status', return_value={'game_board': " ['_' '_' '_' '_' '_' '_' '_' '_' '_']\n ['_' '_' '_' '_' '_' '_' '_' '_' '_']\n ['_' '_' '_' '_' '_' '_' '_' '_' '_']\n ['_' '_' '_' '_' '_' '_' '_' '_' '_']\n ['_' '_' '_' '_' '_' '_' '_' '_' '_']\n ['_' '_' '_' '_' '_' '_' '_' '_' '_']\n\n   1   2   3   4   5   6   7   8   9  "})
    @patch('builtins.print')
    def test_display_board(self, mock_print, _):

        self.client.display_board()
        mock_print.assert_called_with(" ['_' '_' '_' '_' '_' '_' '_' '_' '_']\n ['_' '_' '_' '_' '_' '_' '_' '_' '_']\n ['_' '_' '_' '_' '_' '_' '_' '_' '_']\n ['_' '_' '_' '_' '_' '_' '_' '_' '_']\n ['_' '_' '_' '_' '_' '_' '_' '_' '_']\n ['_' '_' '_' '_' '_' '_' '_' '_' '_']\n\n   1   2   3   4   5   6   7   8   9  \n")

    @patch('builtins.print')
    @patch('builtins.input', side_effect=list(range(1, 9)))
    def test_select_column__valid_inputs(self, *_):
        for i in range(1, 9):
            self.assertEqual(select_column(), i - 1)

    @patch('builtins.input', side_effect=['100', '6'])
    @patch('builtins.print')
    def test_select_column__invalid_column_number(self, mock_print, _):
        
        self.assertEqual(select_column(), 5)
        mock_print.assert_called_with('Invalid range: 100 not in range (1-9)')

    @patch('builtins.input', side_effect=['Not a number', '6'])
    @patch('builtins.print')
    def test_select_column__invalid_input_string(self, mock_print, _):
        
        self.assertEqual(select_column(), 5)
        mock_print.assert_called_with('Please enter an integer')

    @patch('client.Client.establish_connection')
    @patch('client.Client.poll_until_other_player_connected',
           side_effect=Exception('No opponent joined within the timeout of 60 seconds.'))
    @patch('builtins.input', return_value='Kieran')
    def test_start_game__opponent_did_not_join(self, *_):

        with self.assertRaises(Exception) as e:
            start_game()
            self.assertEqual('No opponent joined within the timeout of 60 seconds.', str(e.exception))

    @patch('client.select_column')
    @patch('builtins.input', return_value='Kieran')
    @patch('client.Client.establish_connection')
    @patch('client.Client.poll_until_other_player_connected')
    @patch('client.Client.display_board')
    @patch('client.Client.drop_disc')
    @patch('client.Client.poll_until_turn')
    @patch('client.create_client')
    @patch('builtins.print')
    def test_start_game__player_win(self, mock_print, mock_client, *_):
        self.client.game_state = 'WINNER'
        self.client.winner = self.client.player_id
        mock_client.return_value = self.client

        start_game()
        mock_print.assert_called_with('You won. Congratulations!!!')

    @patch('builtins.input', return_value='Kieran')
    def test_create_client(self, _):

        client = create_client()
        self.assertEqual(client.player_name, 'Kieran')

    @patch('client.select_column')
    @patch('builtins.input', return_value='Kieran')
    @patch('client.Client.establish_connection')
    @patch('client.Client.poll_until_other_player_connected')
    @patch('client.Client.display_board')
    @patch('client.Client.drop_disc')
    @patch('client.Client.poll_until_turn')
    @patch('client.create_client')
    @patch('builtins.print')
    def test_start_game__player_lost(self, mock_print, mock_client, *_):
        self.client.game_state = 'WINNER'
        self.client.winner = '123'
        mock_client.return_value = self.client

        start_game()
        mock_print.assert_called_with('You lost.')

if __name__ == '__main__':
    unittest.main()
