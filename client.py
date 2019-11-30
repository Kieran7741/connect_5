import os
import requests
from retrying import retry
import time

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
    return requests.get(url) if method == 'GET' else requests.post(url, json=body)


class Client:

    def __init__(self, player_name):
        self.player_name = player_name
        self.player_id = None
        self.game_id = None
        self.game_state = None
        self.disk = None

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
            player = response_json['player']
            self.player_id = player['player_id']
            self.disk = player['disk']
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

    def get_game_status(self):
        """
        Query server for game status

        :return: Json response
        :rtype: dict
        """

        res = make_request_to_server(f'game_status/{self.game_id}')

        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(f'Could not read game status: {res.status_code}')

    def drop_disk(self, col):
        """
        Drop disk into the specified column
        :param col: Column number
        :return: Json response from server
        """

        drop_disk_body = {'game_id': self.game_id, 'player_id': self.player_id, 'column': col, 'disk': self.disk }
        res = make_request_to_server('drop_disk', method='POST', body=drop_disk_body)
        if res.status_code == 200:
            return res.json()

    def poll_until_turn(self):
        """
        Poll game status every 5 seconds until clients turn.
        If opponent does not respond within 60 seconds then client wins.
        :return: Opponent made turn
        :rtype: bool
        """

        start_time = time.time()

        while True:
            print(f'Waiting for opponent: {round(60 - (time.time() - start_time))} seconds remaining')
            if self.get_game_status()['player_turn'] == self.player_id:
                break
            time.sleep(5)
            if time.time() - start_time > 60:
                print('Opponent player took to long to respond. You are the winner.')
                return False
        return True

    def display_board(self):
        """
        Display game board
        """

        print(self.get_game_status()['game_board'] + '\n')


def select_column():
    """
    Ask client to select a column.

    :return: Selected column
    :rtype: int
    """
    print('You have 60 seconds to make a more or you loss the game.')
    while True:
        try:
            column = int(input('Select Column (1-9): ')) - 1
            return column
        except ValueError:
            print('Please enter an integer')


def start_game():

    player_name = input('Input player name: ')

    player = Client(player_name)
    player.establish_connection()
    player.poll_until_other_player_connected()
    player.poll_until_turn()

    while True:
        if player.poll_until_turn():
            try:
                player.display_board()
                print('Board updated. Your turn.')
                column = select_column()
                game_status = player.drop_disk(column)
                print(game_status['game_board'])

                if game_status['winner'] == player.player_id:
                    print('You won. Congratulations!!')
                    break
            except Exception as e:
                print('Invalid column: ' + str(e))

        print('Game finished...')


if __name__ == '__main__':

    play = True
    while play:
        print('Starting new game...')
        start_game()

        play_again = input("Would you like to play again? y/n: ")
        play = False if play_again != 'y' else True





