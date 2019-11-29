
from uuid import uuid4
from numpy import transpose, array


class Player:

    def __init__(self, player_name, disk):
        self.player_name = player_name
        self.disk = disk
        self.player_id = str(uuid4())

    def player_details(self):

        return {'player_name': self.player_name, 'player_id': self.player_id, 'disk': self.disk}


class Board:

    LAST_COUNTER = None

    def __init__(self, cols, rows, valid_disks):
        self.cols = cols
        self.rows = rows
        self.valid_disks = valid_disks
        self.board_matrix = array([['_'] * self.rows for _ in range(self.cols)])

    def drop_disk(self, col, disk):

        if disk not in self.valid_disks and disk == self.LAST_COUNTER:
            raise Exception(f'Invalid disk: {disk}.')
        try:
            insert_index = ''.join(self.board_matrix[col]).rindex('_')
            self.board_matrix[col][insert_index] = disk
            self.LAST_COUNTER = disk
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
    PLAYER_1, PlAYER_1_COUNTER = None, 'X'
    PLAYER_2, PlAYER_2_COUNTER = None, 'O'

    def __init__(self):
        self.game_id = '123'  # uuid4()
        self.board = Board(9, 6, [self.PlAYER_1_COUNTER, self.PlAYER_2_COUNTER])

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
            return self.PLAYER_1
        elif not self.PLAYER_2:
            if self.PLAYER_1.player_name != player_name:
                self.PLAYER_2 = Player(player_name, 'O')
                self.STATE = 'READY'
                return self.PLAYER_2
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
                    'game_board': str(self.board), 'player_turn': self.next_player_turn(), 'winner': self.check_for_winner()}
        else:
            # Game has not started
            return {'game_id': self.game_id, 'state': self.STATE}

    def check_for_winner(self):
        """
        Check for vertical, horizontal or diagonal 5 in a row. Using list slicing
        :return: Winning or not
        :rtype: bool
        """
        return False
        # return self.check_coulumn() or self.check_row()

    def check_column(self, col_number):
        """
        Check for 5 in a row for a column.
        Only need to check first 2 slots due to only having 6 vertical spaces.
        Only check column if the number of disks is greater than 4.
        :return:
        """

        if self.board[col_number].count('X') + self.board[col_number].count('O') > 4:
            for disk in reversed(self.board[col_number]):
                # Iterating top down increases efficiency
                current_disk = '_'
                num_in_a_row = 0
                if disk == '_':
                    # no more player disks in the column
                    break
                if disk == current_disk:
                    num_in_a_row += 1
                else:
                    current_disk = disk
                    num_in_a_row = 0
                    continue
                if num_in_a_row == 5:
                    return True

    def next_player_turn(self):
        """
        Determine the next player to drop a disk

        :return: Player ID of next player
        :rtype:
        """

        last_disk = self.board.LAST_COUNTER
        if last_disk:
            return self.PLAYER_2.player_id if self.PLAYER_1.disk == last_disk else self.PLAYER_1.player_id

        # No player has made a move yet
        return self.PLAYER_1.player_id



