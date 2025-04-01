from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from models import User, Game, Move, Leaderboard
from extensions import db, socketio
from flask_socketio import emit, join_room, leave_room
import json
from datetime import datetime

pvp_bp = Blueprint('pvp', __name__)

# Update the render_template calls in the pvp.py file
@pvp_bp.route('/pvp')
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
    
    # Get opponent data
    opponent_id = game.player2_id if game.player1_id == user_id else game.player1_id
    opponent = User.query.get(opponent_id) if opponent_id else None
    
    # Get moves data
    moves = Move.query.filter_by(game_id=game.game_id).order_by(Move.move_order).all()
    
    return render_template('pvp.htm', 
                          user=user, 
                          opponent=opponent,
                          game=game, 
                          moves=moves)

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('status', {'msg': f"{session.get('display_name', 'Anonymous')} has joined the room."}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f"{session.get('display_name', 'Anonymous')} has left the room."}, room=room)

@socketio.on('move')
def handle_move(data):
    game_id = data['game_id']
    x = data['x']
    y = data['y']
    player_id = data['player_id']
    room = data['room']
    
    # Verify it's the player's turn
    game = Game.query.get(game_id)
    if not game or game.status != 'ongoing':
        emit('error', {'msg': 'Game not found or not ongoing'}, room=room)
        return
    
    # Check if position is valid
    existing_move = Move.query.filter_by(game_id=game_id, position_x=x, position_y=y).first()
    if existing_move:
        emit('error', {'msg': 'Position already taken'}, room=room)
        return
    
    # Get the last move order
    last_move = Move.query.filter_by(game_id=game_id).order_by(Move.move_order.desc()).first()
    move_order = 1 if not last_move else last_move.move_order + 1
    
    # Create new move
    new_move = Move(
        game_id=game_id,
        player_id=player_id,
        move_order=move_order,
        position_x=x,
        position_y=y
    )
    
    db.session.add(new_move)
    db.session.commit()
    
    # Check for win
    if check_win(game_id, x, y, player_id):
        game.status = 'finished'
        game.winner_id = player_id
        db.session.commit()
        
        # Update leaderboard for both players
        update_leaderboard(player_id, True)
        opponent_id = game.player2_id if game.player1_id == player_id else game.player1_id
        if opponent_id:
            update_leaderboard(opponent_id, False)
        
        emit('game_over', {
            'winner_id': player_id,
            'move': {
                'x': x,
                'y': y,
                'player_id': player_id
            }
        }, room=room)
    else:
        # Continue game
        emit('move_made', {
            'x': x,
            'y': y,
            'player_id': player_id
        }, room=room)

@socketio.on('chat')
def handle_chat(data):
    room = data['room']
    message = data['message']
    username = session.get('display_name', 'Anonymous')
    
    emit('chat_message', {
        'username': username,
        'message': message,
        'timestamp': datetime.now().strftime('%H:%M')
    }, room=room)

@pvp_bp.route('/give_up')
def give_up():
    if 'user_id' not in session or 'game_id' not in session:
        return redirect(url_for('home.enter_name'))
    
    # Get game data
    game = Game.query.get(session['game_id'])
    if not game:
        return redirect(url_for('home.index'))
    
    # Update game status
    game.status = 'cancelled'
    db.session.commit()
    
    # Emit game_over event to both players
    socketio.emit('game_over', {'reason': 'Player gave up'}, room=f"game_{game.room_code}")
    
    # Update leaderboard for both players
    if game.player1_id == session['user_id']:
        # Current player is player 1, they lose and player 2 wins
        update_leaderboard(game.player1_id, False)
        update_leaderboard(game.player2_id, True)
    else:
        # Current player is player 2, they lose and player 1 wins
        update_leaderboard(game.player1_id, True)
        update_leaderboard(game.player2_id, False)
    
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