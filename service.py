from flask import Flask, request, jsonify, render_template
from main import simulate_game, compute_probability_matrix, compute_statistics
from utils import CHARACTERS

app = Flask(__name__)

@app.route('/')
def index():
    """Render a simple HTML front-end for the simulation."""
    return render_template('index.html', characters=CHARACTERS)

@app.route('/simulate')
def simulate_route():
    try:
        players = int(request.args.get('players', 4))
    except ValueError:
        return jsonify({'error': 'Invalid players parameter'}), 400
    chars = request.args.get('characters')
    characters = [c.strip() for c in chars.split(',')] if chars else None
    winner, players_data, log = simulate_game(players, characters, return_log=True)
    return jsonify({'winner': winner, 'players': players_data, 'log': log})

@app.route('/probability-matrix')
def matrix_route():
    try:
        players = int(request.args.get('players', 4))
        games = int(request.args.get('games', 50))
    except ValueError:
        return jsonify({'error': 'Invalid query parameters'}), 400
    df = compute_probability_matrix(players_count=players, games_per_combo=games)
    return jsonify(df.to_dict(orient='records'))

@app.route('/statistics')
def statistics_route():
    try:
        players = int(request.args.get('players', 4))
        games = int(request.args.get('games', 500))
    except ValueError:
        return jsonify({'error': 'Invalid query parameters'}), 400
    data = compute_statistics(players_count=players, games=games)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
