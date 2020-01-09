
"""
Flask unit tests
"""
import unittest
from unittest.mock import Mock, patch

from game_server import create_app

from game_server.game_session import GameSession, Player
from game_server.game import get_game_session, game_sessions, connect_player_to_game



class TestApp(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.game = GameSession()
        self.player = Player('Kieran', 'X')

    @patch('game_server.game.connect_player_to_game')
    def test_connect_to_game__add_player_successful(self, mock_connect_player):

        mock_connect_player.return_value = (self.game, self.player)

        res_json = self.app.get('/api/v1/connect/Kieran').json
        self.assertEqual(res_json['player'], self.player.player_details())
        self.assertEqual(res_json['game_id'], self.game.game_id)

    @patch('game_server.game.connect_player_to_game', side_effect=Exception('Could not find available session for player to join. '
                                                                            'Max sessions reached'))
    def test_connect_to_game__add_player_no_sessions(self, _):

        request_json = self.app.get('api/v1/connect/Kieran').json

        self.assertEqual(request_json, {'message': 'Could not find available session for player to join. Max sessions reached'})

    @patch('game_server.game.get_game_session')
    def test_get_game_status__one_player_added(self, mock_get_game_session):

        self.game.player_1 = self.player
        self.game.players.append(self.player)
        mock_get_game_session.return_value = self.game

        res_json = self.app.get('/api/v1/game_status/123').json
        self.assertEqual(res_json['state'], 'WAITING FOR PLAYERS')
        self.assertEqual(len(res_json['players']), 1)

    @patch('game_server.game.get_game_session')
    def test_get_game_status__two_players_added(self, mock_get_game_session):

        self.game.player_1 = self.player
        player_2 = Player('John', 'O')
        self.game.player_2 = player_2
        self.game.players.append(self.player)
        self.game.players.append(player_2)
        mock_get_game_session.return_value = self.game

        res_json = self.app.get('/api/v1/game_status/123').json
        self.assertEqual(res_json['player_turn'], self.game.player_1.player_id)
        self.assertEqual(len(res_json['players']), 2)

    @patch('game_server.game.get_game_session')
    def test_opponent_joined__not_joined(self, mock_get_game_session):

        self.game.player_1 = self.player
        self.game.players.append(self.player)
        mock_get_game_session.return_value = self.game

        res_json = self.app.get('/api/v1/opponent/joined/123').json
        self.assertEqual(res_json['opponent'], False)

    @patch('game_server.game.get_game_session')
    def test_opponent_joined__has_joined(self, mock_get_game_session):

        self.game.player_1 = self.player
        self.game.player_2 = self.player
        mock_get_game_session.return_value = self.game

        res_json = self.app.get('/api/v1/opponent/joined/123').json
        self.assertEqual(res_json['opponent'], True)

    @patch('game_server.game.get_game_session')
    def test_drop_disc__not_players_turn(self, mock_get_game_session):

        mock_game_session = Mock()
        mock_game_session.next_player_turn = Mock(return_value='123')
        mock_get_game_session.return_value = mock_game_session

        response_json = self.app.post('/api/v1/drop_disc', json={'game_id': '555', 'player_id': '456', 'column': 5, 'disc': 'O'}).json

        self.assertEqual(response_json, {'message': 'It is not your turn: 456'})

    @patch('game_server.game.get_game_session')
    def test_drop_disc__drop_successful(self, mock_get_game_session):
        mock_game_session = Mock()
        mock_game_session.next_player_turn = Mock(return_value='456')
        mock_game_session.game_details = Mock(return_value={'game_server':'details'})
        mock_get_game_session.return_value = mock_game_session

        res = self.app.post('/api/v1/drop_disc', json={'game_id': '555', 'player_id': '456', 'column': 5, 'disc': 'O'})
        self.assertEqual(res.status_code, 200)

    def test_get_game_session__session_found(self):

        self.assertEqual(game_sessions[2], get_game_session(game_sessions[2].game_id))

    def test_get_game_session__session_not_found(self):

        with self.assertRaises(Exception) as e:
            get_game_session(5)

        self.assertEqual('Game session not found', str(e.exception))

    @patch('builtins.print')
    def test_connect_player_to_game__success(self, _):

        game_session, _ = connect_player_to_game('Kieran')
        self.assertEqual(game_sessions[0], game_session)

    # Cant be tested due to in memory game sessions

    # def test_connect_player_to_game__no_sessions(self):
    #     game_sessions.clear()
    #
    #     with self.assertRaises(Exception) as e:
    #         connect_player_to_game('Kieran')
    #     self.assertEqual('Could not find available session for player to join. Max sessions reached', str(e.exception))


if __name__ == '__main__':
    unittest.main()
