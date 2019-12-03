# Connect 5: Multiplayer Flask application

* Coding challenge completed as part of job interview
* The application uses a server to track the state of a connect 5 game sessions
* Players(clients) connect to the server and are assigned to an available game session
* The game starts when two players have joined a game session
* Players wait for their turn before dropping a disc into the board
* Players ping the Flask server every 5 seconds to query the state of the game
* If a player does not take their turn within 60 seconds of the opponent they forfeit the game

## Getting Started

This application was tested on MacOS and Linux using python3.6 on and cannot be guaranteed to work on older/newer versions of python.


### Prerequisites

Clone this repo from github.

### Installing


It is recommended that you create a virtual environment and pip install the contents of requirements.txt
```
python3.6 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

### Running

First start the server:

```commandline
python app.py
```

Then start two clients in separate terminal windows:

```commandline
python client.py
```

Follow the on screen instructions.  
Each player will input their name and wait for an opponent to join the game session.  
Players then take it in turns to drop discs into the board. Valid columns are 1-9. 
  
Once a player matches 5 discs in a row they are declared the winner.   
Both players are provided the option to replay.

## Checking for a winner

The playing board is implemented as a 9 column by 6 row array using numpy
```python
self.board_matrix = array([['_'] * self.ROWS for _ in range(self.COLUMNS)])
```
The board can be visualised by printing out the transpose:
```python
def __str__(self):
    """
    Sample output for empty board
    :return: String of board
    :rtype: str
    """
    return ' ' + str(transpose(self.board_matrix))[1:-1] + '\n\n   1   2   3   4   5   6   7   8   9  '
```
```commandline
 ['_' '_' '_' '_' '_' '_' '_' '_' '_']
 ['_' '_' '_' '_' '_' '_' '_' '_' '_']
 ['_' '_' '_' '_' '_' '_' '_' '_' '_']
 ['X' '_' '_' '_' '_' '_' '_' '_' '_']
 ['X' '_' '_' '_' '_' '_' '_' '_' '_']
 ['X' 'O' '_' 'O' 'O' '_' '_' '_' '_']

   1   2   3   4   5   6   7   8   9  

```

The winner is determined by running the following check on each 'line' in the board.
Note: A line is defined as any straight line through 5 or more discs. No need to check lines less than 5 as these cannot contain a winning pattern.  

```python
def check_if_line_has_five_in_a_row(self, line):
    """
    Check each list for 5 consecutive discs.
    If the line contains 'XXXXX' or 'OOOOO' then we have a winner.

    :param line: line of discs to check.
    :type line: list
    :return: Winning disc if winner found else None
    :rtype: str or None
    """

    line_as_string = ''.join(line)

    for disc in self.valid_discs:
        if disc*5 in line_as_string:
            return disc
```

Extracting rows and columns from the dataset is straight forward:

```python
def check_rows_and_cols(self):
    """
    Check rows and columns for 5 in a row.
    :return: Winning disc if winner found else none
    :rtype: str or None
    """

    for col in self.board_matrix:
        winner = self.check_if_line_has_five_in_a_row(list(col))
        if winner:
            print('Winner by connecting a column')
            return winner

    for row in transpose(self.board_matrix):
        winner = self.check_if_line_has_five_in_a_row(list(row))
        if winner:
            print('Winner by connecting a row')
            return winner
```

Extracting diagonals is more complex and requires the use of numpy.diagonal and numpy.flip:

```python
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
            print('Winner by connecting a diagonal')
            return winner
```


### Running unit tests

All files are unit tested using unittest  
Ensure you are in the root of the project. The below shows the running of test_app.py

```commandline
python -m unittest tests.test_app
```

Generate Test coverage report using coverage.py

```commandline
 coverage run --source=. -m unittest discover -s .
```

## Authors

* **Kieran Lyons** - [Kieran7741](https://github.com/Kieran7741)