
from uuid import uuid4
from numpy import transpose, array


class Player:

    def __init__(self, player_name, symbol):
        self.player_name = player_name
        self.symbol = symbol
        self.player_id = uuid4()

    def player_details(self):

        return {'player_name': self.player_name, 'player_id': self.player_id, 'symbol': self.symbol}


class Board:

    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows

        self.board_matrix = array([['_'] * self.rows for _ in range(self.cols)])

    def drop_counter(self, col, symbol):

        try:
            insert_index = ''.join(self.board_matrix[col]).rindex('_')
            self.board_matrix[col][insert_index] = symbol
        except ValueError:
            raise ValueError('No space left in that column')

    def __str__(self):
        """
        Sample output for empty board
        :return:
        """
        return ' ' + str(transpose(self.board_matrix))[1:-1] + '\n\n   1   2   3   4   5   6   7   8   9  '


class GameSession:

    STATE = 'WAITING FOR PLAYERS'
    PLAYER_1 = None
    PLAYER_2 = None

    def __init__(self):
        self.game_id = '123'  # uuid4()
        self.board = Board(cols=9, rows=6)

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
            self.PLAYER_1 = Player(player_name, 'X')
            return True
        elif not self.PLAYER_2:
            if self.PLAYER_1.player_name != player_name:
                self.PLAYER_2 = Player(player_name, 'O')
                self.STATE = 'STARTING'
                return True
            else:
                raise Exception(f'Name: {player_name} already in use.')

    def game_details(self):
        """
        Return game details
        :return: Game details
        """
        if not self.waiting_for_players:
            return {'game_id': self.game_id, 'state': self.STATE, 'players': [self.PLAYER_1.player_details(),
                                                                              self.PLAYER_2.player_details()],
                    'game_board': str(self.board)}
        else:
            return {'game_id': self.game_id, 'state': self.STATE}

    def check_for_winner(self, last_drop):
        """
        Check for vertical, horizontal or diagonal 5 in a row. Using list slicing
        :param last_drop: column of last drop
        :return: Winning
        """

        return self.check_coulumn() or self.check_row()

    def check_column(self, col_number):
        """
        Check for 5 in a row for a column.
        Only need to check first 2 symbols due to only having 6 vertical spaces.
        Only check column if the number of counters is greater than 4.
        :return:
        """

        if self.board[col_number].count('X') + self.board[col_number].count('O') > 4:
            for symbol in reversed(self.board[col_number]):
                # Iterating top down increases efficiency
                current_symbol = '_'
                num_in_a_row = 0
                if symbol == '_':
                    # no more player counters in the column
                    break
                if symbol == current_symbol:
                    num_in_a_row += 1
                else:
                    current_symbol = symbol
                    num_in_a_row = 0
                    continue
                if num_in_a_row == 5:
                    return True
