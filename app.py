from flask import Flask, jsonify, abort, request

from game.game_session import GameSession

API_PREFIX = '/api/v1'

app = Flask(__name__)

MAX_GAME_SESSIONS = 10
game_sessions = [GameSession() for _ in range(MAX_GAME_SESSIONS)]  # In memory GameSessions


@app.route(API_PREFIX + '/connect/<player_name>')
def connect_to_game(player_name):
    """
    Provide a player with a session
    :param player_name: player_name
    :return: Game session information if connection successful
    :rtype: flask.Response
    """

    try:
        game_session = connect_player_to_game(player_name)
        return jsonify(game_session.game_details())
    except Exception as e:
        return abort(400, e)


@app.route(API_PREFIX + '/game_status/<game_id>')
def get_game_status(game_id):
    try:
        return jsonify(get_game_session(game_id).game_details())
    except Exception as e:
        return abort(400, f'Could not read game status for {game_id}: {e}')


@app.route(API_PREFIX + '/drop_counter', methods=['POST'])
def drop_disk():

    drop_data = request.json

    try:
        game_session = get_game_session(drop_data['game_id'])

        if not game_session.next_player_turn() == drop_data['player_id']:
            raise Exception(f'Wait your turn client: {drop_data["player_id"]}')

        game_session.board.drop_disk(drop_data['column'], drop_data['disk'])
        return jsonify(game_session.game_details())
    except Exception as e:
        return abort(400, e)


def connect_player_to_game(player_name):
    """
    Get a players game session.
    :param player_name: Name of player
    :return: GameSession object
    """

    for session in game_sessions[:]:
        if session.waiting_for_players:
            session.add_player(player_name)
            return session

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
