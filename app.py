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
        game_session, player = connect_player_to_game(player_name)
        return jsonify({'player': player.player_details(), 'game_id': game_session.game_id})
    except Exception as e:
        return abort(400, e)


@app.route(API_PREFIX + '/game_status/<game_id>')
def get_game_status(game_id):
    try:
        return jsonify(get_game_session(game_id).game_details())
    except Exception as e:
        print(e)
        return abort(400, f'Could not read game status for {game_id}: {e}')


@app.route(API_PREFIX + '/opponent/joined/<game_id>')
def opponent_joined(game_id):
    """
    Check if both players have joined the game

    :param game_id:
    :return: Json containing opponent key indicating if opponent has connected
    :rtype: flask.Response
    """

    return jsonify({'opponent': not get_game_session(game_id).waiting_for_players})


@app.route(API_PREFIX + '/drop_disc', methods=['POST'])
def drop_disc():

    drop_data = request.json
    print(drop_data)
    try:
        game_session = get_game_session(drop_data['game_id'])

        if not game_session.next_player_turn() == drop_data['player_id']:
            raise Exception(f'Wait your turn client: {drop_data["player_id"]}')

        game_session.board.drop_disc(drop_data['column'], drop_data['disc'])
        game_session.check_for_winner()

        return jsonify(game_session.game_details())
    except Exception as e:
        print("Error: " + str(e))
        return abort(400, e)


def connect_player_to_game(player_name):
    """
    Get a players game session.
    :param player_name: Name of player
    :return: GameSession object and connected player object
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
