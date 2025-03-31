from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request
from models import User, Game, Move, Leaderboard
from extensions import db, socketio
import random
import numpy as np
from datetime import datetime

pve_bp = Blueprint('pve', __name__)

# AI logic for Caro game
class CaroAI:
    def __init__(self, board_size=15):
        self.board_size = board_size
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.player = 1  # Human
        self.ai = 2      # AI
        
    def update_board(self, moves):
        # Reset board
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        
        # Apply all moves
        for move in moves:
            self.board[move.position_y][move.position_x] = 1 if move.player_id == move.game.player1_id else 2
    
    def evaluate_window(self, window, piece):
        score = 0
        opp_piece = self.player if piece == self.ai else self.ai
        
        if window.count(piece) == 5:
            score += 100000
        elif window.count(piece) == 4 and window.count(0) == 1:
            score += 10000
        elif window.count(piece) == 3 and window.count(0) == 2:
            score += 1000
        elif window.count(piece) == 2 and window.count(0) == 3:
            score += 100
        
        if window.count(opp_piece) == 4 and window.count(0) == 1:
            score -= 9000
            
        return score
    
    def score_position(self):
        score = 0
        
        # Score horizontal
        for r in range(self.board_size):
            for c in range(self.board_size - 4):
                window = [self.board[r][c+i] for i in range(5)]
                score += self.evaluate_window(window, self.ai)
        
        # Score vertical
        for c in range(self.board_size):
            for r in range(self.board_size - 4):
                window = [self.board[r+i][c] for i in range(5)]
                score += self.evaluate_window(window, self.ai)
        
        # Score diagonal (positive slope)
        for r in range(self.board_size - 4):
            for c in range(self.board_size - 4):
                window = [self.board[r+i][c+i] for i in range(5)]
                score += self.evaluate_window(window, self.ai)
        
        # Score diagonal (negative slope)
        for r in range(4, self.board_size):
            for c in range(self.board_size - 4):
                window = [self.board[r-i][c+i] for i in range(5)]
                score += self.evaluate_window(window, self.ai)
                
        return score
    
    def get_valid_locations(self):
        valid_locations = []
        
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r][c] == 0:
                    valid_locations.append((r, c))
        
        return valid_locations
    
    def is_terminal_node(self):
        # Check for win
        # Horizontal
        for r in range(self.board_size):
            for c in range(self.board_size - 4):
                window = [self.board[r][c+i] for i in range(5)]
                if window.count(self.player) == 5 or window.count(self.ai) == 5:
                    return True
        
        # Vertical
        for c in range(self.board_size):
            for r in range(self.board_size - 4):
                window = [self.board[r+i][c] for i in range(5)]
                if window.count(self.player) == 5 or window.count(self.ai) == 5:
                    return True
        
        # Diagonal (positive slope)
        for r in range(self.board_size - 4):
            for c in range(self.board_size - 4):
                window = [self.board[r+i][c+i] for i in range(5)]
                if window.count(self.player) == 5 or window.count(self.ai) == 5:
                    return True
        
        # Diagonal (negative slope)
        for r in range(4, self.board_size):
            for c in range(self.board_size - 4):
                window = [self.board[r-i][c+i] for i in range(5)]
                if window.count(self.player) == 5 or window.count(self.ai) == 5:
                    return True
        
        # Check if board is full
        return len(self.get_valid_locations()) == 0
    
    def minimax(self, depth, alpha, beta, maximizing_player):
        valid_locations = self.get_valid_locations()
        is_terminal = self.is_terminal_node()
        
        if depth == 0 or is_terminal:
            if is_terminal:
                # Check for win
                # Horizontal
                for r in range(self.board_size):
                    for c in range(self.board_size - 4):
                        window = [self.board[r][c+i] for i in range(5)]
                        if window.count(self.ai) == 5:
                            return (None, 1000000)
                        elif window.count(self.player) == 5:
                            return (None, -1000000)
                
                # Vertical
                for c in range(self.board_size):
                    for r in range(self.board_size - 4):
                        window = [self.board[r+i][c] for i in range(5)]
                        if window.count(self.ai) == 5:
                            return (None, 1000000)
                        elif window.count(self.player) == 5:
                            return (None, -1000000)
                
                # Diagonal (positive slope)
                for r in range(self.board_size - 4):
                    for c in range(self.board_size - 4):
                        window = [self.board[r+i][c+i] for i in range(5)]
                        if window.count(self.ai) == 5:
                            return (None, 1000000)
                        elif window.count(self.player) == 5:
                            return (None, -1000000)
                
                # Diagonal (negative slope)
                for r in range(4, self.board_size):
                    for c in range(self.board_size - 4):
                        window = [self.board[r-i][c+i] for i in range(5)]
                        if window.count(self.ai) == 5:
                            return (None, 1000000)
                        elif window.count(self.player) == 5:
                            return (None, -1000000)
                
                # Game is over, no more valid moves
                return (None, 0)
            else:
                # Depth is zero
                return (None, self.score_position())
        
        if maximizing_player:
            value = -float("inf")
            column = random.choice(valid_locations)
            
            for pos in valid_locations:
                r, c = pos
                self.board[r][c] = self.ai
                new_score = self.minimax(depth-1, alpha, beta, False)[1]
                self.board[r][c] = 0
                
                if new_score > value:
                    value = new_score
                    column = pos
                
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
                    
            return column, value
        
        else:  # Minimizing player
            value = float("inf")
            column = random.choice(valid_locations)
            
            for pos in valid_locations:
                r, c = pos
                self.board[r][c] = self.player
                new_score = self.minimax(depth-1, alpha, beta, True)[1]
                self.board[r][c] = 0
                
                if new_score < value:
                    value = new_score
                    column = pos
                
                beta = min(beta, value)
                if alpha >= beta:
                    break
                    
            return column, value
    
    def get_best_move(self, depth=3):
        # Get the best move using minimax algorithm
        position, _ = self.minimax(depth, -float("inf"), float("inf"), True)
        return position

@pve_bp.route('/pve')
def index():
    # Check if user has cookies
    user_id = request.cookies.get('user_id')
    game_id = request.cookies.get('game_id')
    
    if not user_id or not game_id:
        return redirect(url_for('home.enter_name'))
    
    # Get game data
    game = Game.query.get(game_id)
    if not game:
        return redirect(url_for('home.index'))
    
    # Get user data
    user = User.query.get(user_id)
    if not user:
        # Create user if not exists
        from routes.home import create_new_user
        display_name = request.cookies.get('display_name')
        user = create_new_user(user_id, display_name)
    
    # Get moves data
    moves = Move.query.filter_by(game_id=game.game_id).order_by(Move.move_order).all()
    
    return render_template('pve.htm', 
                          user=user, 
                          game=game, 
                          moves=moves)

@pve_bp.route('/make_move', methods=['POST'])
def make_move():
    if 'user_id' not in session or 'game_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'})
    
    data = request.json
    x = data.get('x')
    y = data.get('y')
    
    # Get game data
    game = Game.query.get(session['game_id'])
    if not game or game.status != 'ongoing':
        return jsonify({'status': 'error', 'message': 'Game not found or not ongoing'})
    
    # Check if position is valid
    existing_move = Move.query.filter_by(game_id=game.game_id, position_x=x, position_y=y).first()
    if existing_move:
        return jsonify({'status': 'error', 'message': 'Position already taken'})
    
    # Get the last move order
    last_move = Move.query.filter_by(game_id=game.game_id).order_by(Move.move_order.desc()).first()
    move_order = 1 if not last_move else last_move.move_order + 1
    
    # Create new move
    new_move = Move(
        game_id=game.game_id,
        player_id=session['user_id'],
        move_order=move_order,
        position_x=x,
        position_y=y
    )
    
    db.session.add(new_move)
    db.session.commit()
    
    # Check for win
    if check_win(game.game_id, x, y, session['user_id']):
        game.status = 'finished'
        game.winner_id = session['user_id']
        db.session.commit()
        
        # Update leaderboard
        update_leaderboard(session['user_id'], True)
        
        return jsonify({
            'status': 'win',
            'message': 'You win!',
            'move': {
                'x': x,
                'y': y,
                'player_id': session['user_id']
            }
        })
    
    # AI's turn
    ai = CaroAI()
    moves = Move.query.filter_by(game_id=game.game_id).all()
    ai.update_board(moves)
    
    # Get AI's move
    ai_y, ai_x = ai.get_best_move()
    
    # Create AI move
    ai_move = Move(
        game_id=game.game_id,
        player_id=None,  # AI has no player_id
        move_order=move_order + 1,
        position_x=ai_x,
        position_y=ai_y
    )
    
    db.session.add(ai_move)
    db.session.commit()
    
    # Check if AI wins
    if check_win(game.game_id, ai_x, ai_y, None):
        game.status = 'finished'
        game.winner_id = None  # AI wins
        db.session.commit()
        
        # Update leaderboard
        update_leaderboard(session['user_id'], False)
        
        return jsonify({
            'status': 'lose',
            'message': 'AI wins!',
            'move': {
                'x': x,
                'y': y,
                'player_id': session['user_id']
            },
            'ai_move': {
                'x': ai_x,
                'y': ai_y,
                'player_id': None
            }
        })
    
    return jsonify({
        'status': 'success',
        'move': {
            'x': x,
            'y': y,
            'player_id': session['user_id']
        },
        'ai_move': {
            'x': ai_x,
            'y': ai_y,
            'player_id': None
        }
    })

@pve_bp.route('/give_up')
def give_up():
    if 'user_id' not in session or 'game_id' not in session:
        return redirect(url_for('home.login'))
    
    # Get game data
    game = Game.query.get(session['game_id'])
    if not game:
        return redirect(url_for('home.index'))
    
    # Update game status
    game.status = 'cancelled'
    db.session.commit()
    
    # Update leaderboard
    update_leaderboard(session['user_id'], False)
    
    return redirect(url_for('home.index'))

# Helper functions
def check_win(game_id, x, y, player_id):
    # Get all moves for this game
    moves = Move.query.filter_by(game_id=game_id, player_id=player_id).all()
    
    # Create a board representation
    board = [[0 for _ in range(15)] for _ in range(15)]
    for move in moves:
        board[move.position_y][move.position_x] = 1
    
    # Check for 5 in a row
    directions = [
        [(0, 1), (0, -1)],   # Vertical
        [(1, 0), (-1, 0)],   # Horizontal
        [(1, 1), (-1, -1)],  # Diagonal /
        [(1, -1), (-1, 1)]   # Diagonal \
    ]
    
    for dir_pair in directions:
        count = 1  # Count the piece we just placed
        
        # Check in both directions
        for dx, dy in dir_pair:
            nx, ny = x, y
            
            # Count consecutive pieces in this direction
            for _ in range(4):  # Need 4 more to make 5 in a row
                nx, ny = nx + dx, ny + dy
                if (0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] == 1):
                    count += 1
                else:
                    break
            
        if count >= 5:
            return True
    
    return False

def update_leaderboard(user_id, is_win):
    # Get or create leaderboard entry
    leaderboard = Leaderboard.query.filter_by(user_id=user_id).first()
    if not leaderboard:
        leaderboard = Leaderboard(user_id=user_id)
        db.session.add(leaderboard)
    
    # Update stats
    leaderboard.total_games += 1
    if is_win:
        leaderboard.wins += 1
    else:
        leaderboard.losses += 1
    
    # Calculate win rate
    leaderboard.win_rate = leaderboard.wins / leaderboard.total_games if leaderboard.total_games > 0 else 0
    
    db.session.commit()