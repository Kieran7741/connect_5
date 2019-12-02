from client import Client, make_request_to_server


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

    @patch('client.make_request_to_server')
    def test_establish_connection(self, mock_make_request):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {'game_id': '123', 'player': {'player_id': '456', 'disc': 'X'}}
        mock_make_request.return_value = mock_response

        self.assertTrue(self.client.establish_connection())
        self.assertEqual(self.client.disc, 'X')
        self.assertEqual(self.client.game_id, '123')
        self.assertEqual(self.client.player_id, '456')

    @patch('time.sleep')
    @patch('client.make_request_to_server')
    def test_establish_connection__cannot_connect(self, mock_make_request, _):
        mock_response = Mock(status_code=400)
        mock_response.json.return_value = {'game_id': '123', 'player': {'player_id': '456', 'disc': 'X'}}
        mock_make_request.return_value = mock_response

        self.assertRaises(Exception, self.client.establish_connection)
