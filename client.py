import os
import requests
from retrying import retry
import time

HOST = 'http://127.0.0.1:5000'
API_PREFIX = '{host}/api/v1/'.format(host=HOST)


def make_request_to_server(endpoint, method='GET', body=None):
    """
    Send request to Connect_5 server. Note if request fails for conneciton error, error will be raised.
    :param endpoint: Target endpoint
    :param method: Request method
    :param body: Request body
    :return: Response
    :rtype: requests.Response
    """

    url = os.path.join(API_PREFIX, endpoint)
    return requests.get(url) if method == 'GET' else requests.post(url, json=body)


class Client:

    def __init__(self, player_name):
        self.player_name = player_name
        self.player_id = None
        self.game_id = None
        self.game_state = None
        self.disc = None
        self.winner = None

    @retry(retry_on_exception=lambda e: isinstance(e, Exception), wait_fixed=1000, stop_max_attempt_number=12)
    def establish_connection(self):
        """
        Establish connection to Game session. Max attempts is 12

        :return: Connection successful
        :rtype: bool
        """
        print('Attempting to connect to server...')
        res = make_request_to_server(f'connect/{self.player_name}')
        if res.status_code == 200:
            response_json = res.json()
            self.game_id = response_json['game_id']
            player = response_json['player']
            self.player_id = player['player_id']
            self.disc = player['disc']
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

    @retry(retry_on_exception=lambda e: isinstance(e, Exception), wait_fixed=5000, stop_max_attempt_number=12)
    def get_game_status(self):
        """
        Query server for game status

        :return: Json response
        :rtype: dict
        """
        print('Getting game status...')
        res = make_request_to_server(f'game_status/{self.game_id}')

        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(f'Could not read game status: {res.json()["message"]}')

    def drop_disc(self, col):
        """
        Drop disc into the specified column
        :param col: Column number
        :type col: int
        :return: Json response from server
        """

        drop_disc_body = {'game_id': self.game_id, 'player_id': self.player_id, 'column': col, 'disc': self.disc}
        res = make_request_to_server('drop_disc', method='POST', body=drop_disc_body)
        if res.status_code == 200:
            response_json = res.json()
            # Update game state and winner status
            self.winner = response_json['winner']
            self.game_state = response_json['state']
        elif res.status_code == 400:
            # Most likely a invalid column
            raise Exception(res.json()['message'])


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
            game_status = self.get_game_status()
            self.game_state = game_status['state']
            self.winner = game_status['winner']
            if self.game_state == 'WINNER':
                # The game has been won
                return False
            elif game_status['player_turn'] == self.player_id:
                # Players turn now
                return True
            time.sleep(5)
            if time.time() - start_time > 60:
                print('Opponent player took to long to respond. You are the winner.')
                self.winner = self.player_id
                self.game_state = 'WINNER'
                return False

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
    """
    Start game of connect 5
    """

    play = True

    player_name = input('Input player name: ')

    while play:
        player = Client(player_name)
        player.establish_connection()
        try:
            player.poll_until_other_player_connected()
        except Exception as e:
            print(e)
            break

        player.poll_until_turn()

        while True:
            if player.poll_until_turn():
                try:
                    player.display_board()
                    print('Board updated. Your turn.')
                    column = select_column()
                    player.drop_disc(column)
                    player.display_board()
                    if player.game_state == 'WINNER':
                        break
                except Exception as e:
                    print('Something went wrong: ' + str(e))
            elif player.game_state == 'WINNER':
                break

        if player.player_id == player.winner:
            print('You won. Congratulations!!!')
        else:
            print('You lost.')

        play_again = input("Would you like to play again? y/n: ")
        play = False if play_again != 'y' else True


if __name__ == '__main__':
    try:
        start_game()
    except Exception as e:
        print(f'Game exited unexpectedly: {e}')




