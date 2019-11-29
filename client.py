import os
import requests
from retrying import retry

from time import time

HOST = 'http://127.0.0.1:5000'
API_PREFIX = '{host}/api/v1/'.format(host=HOST)


def make_request_to_server(endpoint, method='GET', body=None):
    """
    Send request to Connect_5 server
    :param endpoint:
    :param method:
    :param body:
    :return:
    """
    url = os.path.join(API_PREFIX, endpoint)
    return requests.get(url) if method == 'GET' else requests.post(url, data=body)


def establish_connection(player_name):

    res = make_request_to_server(f'connect/{player_name}')

    if res.status_code == '200':
        return res['player_id']


class Client:

    def __init__(self, player_name):
        self.player_name = player_name
        self.player_id = None
        self.game_id = None
        self.game_state = None

    def establish_connection(self):
        """
        Establish connection to Game session
        :return: Connection successful
        :rtype: bool
        """
        res = make_request_to_server(f'connect/{self.player_name}')
        print(res.status_code)
        if res.status_code == 200:
            response_json = res.json()
            self.game_id = response_json['game_id']
            self.player_id = res.json()['player_id']
            print('Successfully established connection to server')
            return True

    @retry(retry_on_exception=lambda e: isinstance(e, Exception), wait_fixed=5000, stop_max_attempt_number=12)
    def poll_until_other_player_connected(self):
        """
        Poll server until opponent found. Max wait time 60 seconds
        :return: Opponent found.
        :raises Exception: if opponent not found withing the 60 second time out.
        """
        print('Waiting until opponent joins....')
        res = make_request_to_server(f'opponent/joined/{self.game_id}')

        if res.status_code == 200:
            response_json = res.json()
            print(response_json)
            if response_json['opponent']:
                print('Opponent joined.')
                return True
        print('Still waiting on opponent. Sleeping for 5 seconds.')
        raise Exception('No opponent joined within the timeout of 60 seconds.')



if __name__ == '__main__':

    player_1 = Client('Kieran')
    player_1.establish_connection()
    player_1.poll_until_other_player_connected()
