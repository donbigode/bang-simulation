from flask import Flask, request, jsonify
from main import simulate_game, compute_probability_matrix

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'message': 'Bang! Simulation Service'})

@app.route('/simulate')
def simulate_route():
    try:
        players = int(request.args.get('players', 4))
    except ValueError:
        return jsonify({'error': 'Invalid players parameter'}), 400
    chars = request.args.get('characters')
    characters = [c.strip() for c in chars.split(',')] if chars else None
    winner, players_data = simulate_game(players, characters)
    return jsonify({'winner': winner, 'players': players_data})

@app.route('/probability-matrix')
def matrix_route():
    try:
        players = int(request.args.get('players', 4))
        games = int(request.args.get('games', 50))
    except ValueError:
        return jsonify({'error': 'Invalid query parameters'}), 400
    df = compute_probability_matrix(players_count=players, games_per_combo=games)
    return jsonify(df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
