
"""
Flask unit tests
"""
from flask import Flask
import unittest
from app import (connect_to_game, connect_player_to_game, game_sessions,
                get_game_session, get_game_status, opponent_joined)

app = Flask(__name__)


class TestApp(unittest.TestCase):

    def test_connect_to_game(self):

        with app.test_request_context('/api/v1/connect/kieran'):
            connect_to_game()