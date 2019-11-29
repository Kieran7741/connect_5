from flask import Flask, jsonify, abort

from game.game_session import GameSession

API_PREFIX = '/api/v1'

app = Flask(__name__)

game_sessions = [GameSession() for _ in range(10)]  # In memory GameSessions


@app.route(API_PREFIX + '/connect/<player_name>')
def connect_to_game(player_name):
    """
    Provide a player with a session
    :param player_name: player_name
    :return:
    """

    try:
        game_session = connect_player_to_game(player_name)
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


if __name__ == '__main__':
    app.run()
