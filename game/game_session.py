
from uuid import uuid4
from numpy import transpose, array, diagonal, flip


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
        self.turns = 0

    def drop_disk(self, col, disk):
        """
        Drop disk into board.
        :param col:
        :param disk:
        :return:
        """

        if disk not in self.valid_disks or disk == self.LAST_COUNTER:
            raise Exception(f'Invalid disk: {disk}.')
        try:
            insert_index = ''.join(self.board_matrix[col]).rindex('_')
            self.board_matrix[col][insert_index] = disk
            self.LAST_COUNTER = disk
        except ValueError:
            raise ValueError('No space left in that column')

    def check_for_winner(self):
        """
        Check for vertical, horizontal or diagonal 5 in a row.
        :return: Winning disk if winner found else None
        :rtype: str or None
        """

        winner = self.check_rows_and_cols()

        return winner if winner else self.check_diagonals()

    def check_diagonals(self):
        """
        Get board diagonals from the board using numpy.diagonal.
        Need to extract left to right diagonals and right to left diagonals of 5 or greater.
        :return:
        """
        board = transpose(self.board_matrix)
        horizontal_flip_board = flip(board) # flip board to extract right to left diagonal
        diagonals = []

        for i in range(-1, 5): # Only diagonals greater than len 4
            diagonals.append(diagonal(board, i))
            diagonals.append(diagonal(horizontal_flip_board))

        for diag in diagonals:
            winner = self.check_if_line_has_five_in_a_row(list(diag))
            if winner:
                print('Winner by connecting a col')
                return winner

    def check_rows_and_cols(self):
        """
        Check rows and columns for 5 in a row.
        :return: Winning disc if winner found else none
        :rtype: str or None
        """

        for col in self.board_matrix:
            winner = self.check_if_line_has_five_in_a_row(list(col))
            if winner:
                print('Winner by connecting a col')
                return winner

        for row in transpose(self.board_matrix):
            winner = self.check_if_line_has_five_in_a_row(list(row))
            if winner:
                print('Winner by connecting a row')
                return winner

    def check_if_line_has_five_in_a_row(self, line):
        """
        Check each list for 5 consecutive disks.
        If the line contains 'XXXXX' or 'OOOOO' then we have a winner.

        :param line: line of disks to check.
        :type line: list
        :return: Winning disk if winner found else None
        :rtype: str or None
        """

        line_as_string = ''.join(line)

        for disc in self.valid_disks:
            if disc*5 in line_as_string:
                return disc

    def __str__(self):
        """
        Sample output for empty board
        :return: String of board
        :rtype: str
        """
        return ' ' + str(transpose(self.board_matrix))[1:-1] + '\n\n   1   2   3   4   5   6   7   8   9  '


class GameSession:

    STATE = 'WAITING FOR PLAYERS'
    PLAYER_1, PlAYER_1_COUNTER = None, 'X'
    PLAYER_2, PlAYER_2_COUNTER = None, 'O'

    def __init__(self):
        self.game_id = '123'  # uuid4()
        self.board = Board(9, 6, [self.PlAYER_1_COUNTER, self.PlAYER_2_COUNTER])
        self.winner = None

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
                    'game_board': str(self.board), 'player_turn': self.next_player_turn(),
                    'winner': self.winner}
        else:
            # Game has not started
            return {'game_id': self.game_id, 'state': self.STATE}

    def next_player_turn(self):
        """
        Determine the next player to drop a disk

        :return: Player ID of next player
        :rtype: str
        """

        last_disk = self.board.LAST_COUNTER
        if last_disk:
            return self.PLAYER_2.player_id if self.PLAYER_1.disk == last_disk else self.PLAYER_1.player_id

        # No player has made a move yet
        return self.PLAYER_1.player_id

    def check_for_winner(self):
        """
        Check for winner get winners id
        :return: Winners id if winner found else blank string
        :rtype: str
        """
        winning_disc = self.board.check_for_winner()

        if winning_disc:
            self.STATE = 'WINNER'
            self.winner = self.PLAYER_1.player_id if winning_disc == self.PLAYER_1.disk else self.PLAYER_2.player_id


