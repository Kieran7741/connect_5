
"""
Flask unit tests
"""
from flask import Flask
from werkzeug.exceptions import BadRequest
import unittest
from unittest.mock import Mock, patch

from app import (connect_to_game, drop_disc, get_game_status, opponent_joined)

from game.game_session import GameSession, Player

app = Flask(__name__)
app.config['TESTING'] = True


class TestApp(unittest.TestCase):

    def setUp(self):
        self.game = GameSession()
        self.player = Player('Kieran', 'X')

    @patch('app.connect_player_to_game')
    def test_connect_to_game__add_player_successful(self, mock_connect_player):

        mock_connect_player.return_value = (self.game, self.player)

        with app.app_context():
            res_json = connect_to_game('Kieran').json
            self.assertEqual(res_json['player'], self.player.player_details())
            self.assertEqual(res_json['game_id'], self.game.game_id)

    @patch('app.connect_player_to_game', side_effect=Exception('Could not find available session for player to join. '
                                                               'Max sessions reached'))
    def test_connect_to_game__add_player_no_sessions(self, _):

        with app.app_context():
            with self.assertRaises(BadRequest) as req:
                connect_to_game('Kieran')
            self.assertEqual(str(req.exception), '400 Bad Request: Could not find available session for player to join.'
                                                 ' Max sessions reached')

    @patch('app.get_game_session')
    def test_get_game_status__one_player_added(self, mock_get_game_session):

        self.game.player_1 = self.player
        self.game.players.append(self.player)
        mock_get_game_session.return_value = self.game

        with app.app_context():
            res_json = get_game_status('123').json
            self.assertEqual(res_json['state'], 'WAITING FOR PLAYERS')
            self.assertEqual(len(res_json['players']), 1)

    @patch('app.get_game_session')
    def test_get_game_status__two_players_added(self, mock_get_game_session):

        self.game.player_1 = self.player
        player_2 = Player('John', 'O')
        self.game.player_2 = player_2
        self.game.players.append(self.player)
        self.game.players.append(player_2)
        mock_get_game_session.return_value = self.game

        with app.app_context():
            res_json = get_game_status('123').json
            self.assertEqual(res_json['player_turn'], self.game.player_1.player_id)
            self.assertEqual(len(res_json['players']), 2)

    @patch('app.get_game_session')
    def test_opponent_joined__not_joined(self, mock_get_game_session):

        self.game.player_1 = self.player
        self.game.players.append(self.player)
        mock_get_game_session.return_value = self.game

        with app.app_context():
            res_json = opponent_joined('123').json
            self.assertEqual(res_json['opponent'], False)

    @patch('app.get_game_session')
    def test_opponent_joined__has_joined(self, mock_get_game_session):

        self.game.player_1 = self.player
        self.game.player_2 = self.player
        mock_get_game_session.return_value = self.game

        with app.app_context():

            res_json = opponent_joined('123').json
            self.assertEqual(res_json['opponent'], True)

    @patch('app.get_game_session')
    def test_drop_disc__not_players_turn(self, mock_get_game_session):

        mock_game_session = Mock()
        mock_game_session.next_player_turn = Mock(return_value='123')
        mock_get_game_session.return_value = mock_game_session

        with app.test_request_context(json={'game_id': '555', 'player_id': '456', 'column': 5, 'disc': 'O'}):

            with self.assertRaises(BadRequest) as e:
                drop_disc()
            self.assertEqual('400 Bad Request: It is not your turn: 456', str(e.exception))

    @patch('app.get_game_session')
    def test_drop_disc__drop_successful(self, mock_get_game_session):
        mock_game_session = Mock()
        mock_game_session.next_player_turn = Mock(return_value='456')
        mock_game_session.game_details = Mock(return_value={'game':'details'})
        mock_get_game_session.return_value = mock_game_session

        with app.test_request_context(json={'game_id': '555', 'player_id': '456', 'column': 5, 'disc': 'O'}):
            res = drop_disc()
            self.assertEqual(res.status_code, 200)
