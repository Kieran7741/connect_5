
from uuid import uuid4
from collections import OrderedDict


class Player:

    def __init__(self, player_name):
        self.player_name = player_name
        self.player_id = uuid4()

    def player_details(self):

        return {'player_name': self.player_name, 'player_id': self.player_id}


class GameSession:

    STATE = 'WAITING FOR PLAYERS'
    PLAYER_1 = None
    PLAYER_2 = None

    def __init__(self):
        self.game_id = uuid4()
        self.board = OrderedDict({i: ['_'] * 6 for i in range(9)})

    @property
    def waiting_for_players(self):
        return not (self.PLAYER_1 and self.PLAYER_2)

    def add_player(self, player_name):
        """
        Add player to game session
        :param player_name: Name of player to add.
        :return: Player added
        """
        if not self.PLAYER_1:
            self.PLAYER_1 = Player(player_name)
            return True
        elif not self.PLAYER_2:
            if self.PLAYER_1.player_name != player_name:
                self.PLAYER_2 = Player(player_name)
                self.STATE = 'STARTING'
                return True
            else:
                raise Exception(f'Name: {player_name} already in use.')


    def get_board(self):
        return self.board

    def game_details(self):
        """
        Return game details
        :return: Game details
        """
        if not self.waiting_for_players:
            return {'game_id': self.game_id, 'state': self.STATE, 'players': [self.PLAYER_1.player_details(),
                                                                              self.PLAYER_2.player_details()],
                    'game_board': self.get_board()}
        else:
            return {'game_id': self.game_id, 'state': self.STATE}
