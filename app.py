from flask import Flask, jsonify, abort, request, make_response

from game.game_session import GameSession

API_PREFIX = '/api/v1'

MAX_GAME_SESSIONS = 10
game_sessions = [GameSession() for _ in range(MAX_GAME_SESSIONS)]  # In memory GameSessions

app = Flask(__name__)


@app.errorhandler(400)
def error_handler(error):
    """Build json response message for 400 errors"""
    return make_response(jsonify({'message': error.description}), 400)


@app.route(API_PREFIX + '/connect/<player_name>')
def connect_to_game(player_name):
    """
    Provide a player with a session

    :param player_name: player_name
    :type player_name: str
    :return: Game session information if connection successful
    :rtype: flask.Response
    """

    try:
        game_session, player = connect_player_to_game(player_name)
        return jsonify({'player': player.player_details(), 'game_id': game_session.game_id})
    except Exception as e:
        return abort(400, str(e))


@app.route(API_PREFIX + '/game_status/<game_id>')
def get_game_status(game_id):
    """
    Get status for game_id

    :param game_id: Game to check status of
    :type game_id: str
    :return: Game status
    :rtype: flask.Response
    """

    try:
        return jsonify(get_game_session(game_id).game_details())
    except Exception as e:
        return abort(400, f'Could not read game status for {game_id}: {e}')


@app.route(API_PREFIX + '/opponent/joined/<game_id>')
def opponent_joined(game_id):
    """
    Check if both players have joined the game

    :param game_id: Game to check
    :type game_id: str
    :return: Json containing opponent key indicating if opponent has connected
    :rtype: flask.Response
    """
    try:
        return jsonify({'opponent': not get_game_session(game_id).waiting_for_players})
    except Exception as e:
        abort(400, str(e))


@app.route(API_PREFIX + '/drop_disc', methods=['POST'])
def drop_disc():
    """
    Drop disc into game board.

    :return: Game status after disk dropped.
    :rtype: flask.Response
    """

    drop_data = request.json
    try:
        game_session = get_game_session(drop_data['game_id'])

        if not game_session.next_player_turn() == drop_data['player_id']:
            raise Exception(f'It is not your turn: {drop_data["player_id"]}')

        game_session.board.drop_disc(drop_data['column'], drop_data['disc'])
        game_session.check_for_winner()

        return jsonify(game_session.game_details())
    except Exception as e:
        return abort(400, e)


def connect_player_to_game(player_name):
    """
    Get a players game session.

    :param player_name: Name of player
    :return: GameSession object and connected player object
    :rtype: tuple
    :raises Exception: if no available sessions
    """

    for session in game_sessions[:]:
        if session.waiting_for_players:
            return session, session.add_player(player_name)

    raise Exception('Could not find available session for player to join. Max sessions reached')


def get_game_session(session_id):
    """
    Get game session by id

    :param session_id: Game session to search for
    :return: Matched GameSession
    :rtype: game.game_session.GameSession
    """

    for session in game_sessions:
        if session_id == session.game_id:
            return session

    raise Exception('Game session not found')


if __name__ == '__main__':
    app.run()
