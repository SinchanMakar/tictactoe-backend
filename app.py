from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

def check_winner(board):
    lines = [
        [0,1,2],[3,4,5],[6,7,8],  # rows
        [0,3,6],[1,4,7],[2,5,8],  # cols
        [0,4,8],[2,4,6]           # diagonals
    ]
    for line in lines:
        a, b, c = line
        if board[a] and board[a] == board[b] == board[c]:
            return board[a], line
    return None, None

def is_draw(board):
    return all(cell != '' for cell in board)

def minimax(board, is_maximizing):
    winner, _ = check_winner(board)
    if winner == 'O': return 10
    if winner == 'X': return -10
    if is_draw(board): return 0

    if is_maximizing:
        best = -1000
        for i in range(9):
            if board[i] == '':
                board[i] = 'O'
                best = max(best, minimax(board, False))
                board[i] = ''
        return best
    else:
        best = 1000
        for i in range(9):
            if board[i] == '':
                board[i] = 'X'
                best = min(best, minimax(board, True))
                board[i] = ''
        return best

def get_ai_move(board, difficulty):
    empty = [i for i, v in enumerate(board) if v == '']
    if not empty:
        return -1

    if difficulty == 'easy':
        return random.choice(empty)

    if difficulty == 'medium':
        if random.random() < 0.5:
            return random.choice(empty)

    best_score = -1000
    best_move = empty[0]
    for i in empty:
        board[i] = 'O'
        score = minimax(board, False)
        board[i] = ''
        if score > best_score:
            best_score = score
            best_move = i
    return best_move

@app.route('/api/move', methods=['POST'])
def make_move():
    data = request.json
    board = data.get('board', [''] * 9)
    difficulty = data.get('difficulty', 'hard')

    winner, winning_line = check_winner(board)
    if winner or is_draw(board):
        return jsonify({'error': 'Game already over'}), 400

    ai_move = get_ai_move(board, difficulty)
    if ai_move == -1:
        return jsonify({'error': 'No moves available'}), 400

    board[ai_move] = 'O'
    winner, winning_line = check_winner(board)
    draw = is_draw(board)

    return jsonify({
        'board': board,
        'ai_move': ai_move,
        'winner': winner,
        'winning_line': winning_line,
        'draw': draw
    })

@app.route('/api/reset', methods=['POST'])
def reset():
    return jsonify({'board': [''] * 9, 'status': 'ok'})

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
