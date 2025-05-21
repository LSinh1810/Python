from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, make_response
from models import User, Game, Move, Leaderboard
from extensions import db, socketio
from flask_socketio import emit, join_room, leave_room
import json
from datetime import datetime
import socket

pvp_bp = Blueprint('pvp', __name__)

def get_server_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        server_ip = s.getsockname()[0]
        s.close()
        return server_ip
    except:
        return "localhost"

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
    
    # Determine if current user is player 1
    is_player1 = game.player1_id == user_id
    
    # Get player 1 and player 2 data
    player1 = User.query.get(game.player1_id)
    player2 = User.query.get(game.player2_id) if game.player2_id else None
    
    # Generate game link using server IP
    server_ip = get_server_ip()
    game_link = f"http://{server_ip}:5000/join/{game.room_code}"
    
    return render_template('pvp.htm', 
                          user=user,
                          player1=player1,
                          player2=player2,
                          opponent=opponent,
                          game=game, 
                          moves=moves,
                          is_player1=is_player1,
                          room_code=game.room_code,
                          game_link=game_link)

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    print(f"Player joined room: {room}")

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f"{session.get('display_name', 'Anonymous')} has left the room."}, room=room)

@socketio.on('move')
def handle_move(data):
    try:
        game_id = data.get('game_id')
        room = data.get('room')
        if not game_id or not room:
            print("Error: Missing game_id or room in move event")
            return
            
        row = data.get('row')
        col = data.get('col')
        player_id = data.get('player_id')
        
        if not all([row is not None, col is not None, player_id]):
            print("Error: Missing required move data")
            return
            
        game = Game.query.get(game_id)
        if not game:
            print(f"Error: Game {game_id} not found")
            return
            
        if game.status != 'playing':
            print(f"Error: Game {game_id} is not in playing state")
            return
            
        if game.current_player_id != player_id:
            print(f"Error: Not player {player_id}'s turn")
            return
            
        # Check if position is already taken
        if game.board[row][col] is not None:
            print(f"Error: Position ({row}, {col}) is already taken")
            return
            
        # Update game state
        game.board[row][col] = player_id
        game.last_move = {'row': row, 'col': col}
        game.current_player_id = game.player2_id if player_id == game.player1_id else game.player1_id
        db.session.commit()
        
        # Create move record
        move = Move(
            game_id=game_id,
            player_id=player_id,
            row=row,
            col=col,
            move_order=Move.query.filter_by(game_id=game_id).count() + 1
        )
        db.session.add(move)
        db.session.commit()
        
        # Emit move to all clients in the room
        emit('move_made', {
            'row': row,
            'col': col,
            'player_id': player_id,
            'current_player_id': game.current_player_id,
            'board': game.board
        }, room=room, broadcast=True)
        
        # Check for win
        if check_win(game.board, row, col, player_id):
            game.status = 'finished'
            game.winner_id = player_id
            db.session.commit()
            
            # Update leaderboard
            update_leaderboard(game)
            
            # Emit game over
            emit('game_over', {
                'winner_id': player_id,
                'reason': 'win',
                'board': game.board
            }, room=room, broadcast=True)
            
    except Exception as e:
        print(f"Error in handle_move: {str(e)}")
        return

@socketio.on('chat_message')
def handle_chat(data):
    room = data['room']
    message = data['message']
    username = session.get('display_name', 'Anonymous')
    
    emit('new_message', {
        'sender': username,
        'message': message,
        'time': datetime.now().strftime('%H:%M')
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

@socketio.on('join_game')
def join_game(data):
    try:
        game_id = data.get('game_id')
        player_id = data.get('player_id')
        display_name = data.get('display_name', 'Anonymous')
        room = data.get('room')
        
        if not all([game_id, player_id, room]):
            print("Error: Missing required join data")
            return
            
        game = Game.query.get(game_id)
        if not game:
            print(f"Error: Game {game_id} not found")
            return
            
        # Join the room
        join_room(room)
        print(f"Player {player_id} joined game {game_id} in room {room}")
        
        # If this is player 2 joining
        if game.player2_id is None and game.player1_id != player_id:
            game.player2_id = player_id
            game.status = 'playing'  # Change status to playing
            game.current_player_id = game.player1_id  # Set current player to player 1
            game.board = [[None for _ in range(15)] for _ in range(15)]  # Initialize empty board
            db.session.commit()
            
            # Emit player joined event to all clients
            emit('player_joined', {
                'player_id': player_id,
                'display_name': display_name,
                'game_status': 'playing',
                'current_player_id': game.current_player_id
            }, room=room, broadcast=True)
            
            # Emit game started event to all clients
            emit('game_started', {
                'game_id': game_id,
                'player1_id': game.player1_id,
                'player2_id': player_id,
                'current_player_id': game.current_player_id,
                'status': 'playing',
                'board': game.board
            }, room=room, broadcast=True)
            
            # Emit initial game state to all clients
            emit('game_state', {
                'game_id': game_id,
                'status': 'playing',
                'current_player_id': game.current_player_id,
                'player1_id': game.player1_id,
                'player2_id': player_id,
                'board': game.board
            }, room=room, broadcast=True)
            
    except Exception as e:
        print(f"Error in join_game: {str(e)}")
        return

@socketio.on('timeout_forfeit')
def handle_timeout_forfeit(data):
    room = data['room']
    player_id = data['player_id']
    
    # Get game data
    game = Game.query.filter_by(room_code=room).first()
    if not game:
        return
    
    # Update game status
    game.status = 'finished'
    # Set winner as the other player
    game.winner_id = game.player2_id if game.player1_id == player_id else game.player1_id
    
    db.session.commit()
    
    # Update leaderboard
    update_leaderboard(game.winner_id, True)  # Winner
    update_leaderboard(player_id, False)      # Loser
    
    # Emit game over event
    emit('game_over', {
        'winner_id': game.winner_id,
        'reason': 'timeout'
    }, room=room)

@pvp_bp.route('/join/<room_code>')
def join_game_route(room_code):
    # Get game data
    game = Game.query.filter_by(room_code=room_code).first()
    if not game:
        return redirect(url_for('home.index'))
    
    # If game already has 2 players, redirect to game
    if game.player1_id and game.player2_id:
        response = make_response(redirect(url_for('pvp.index')))
        response.set_cookie('game_id', str(game.game_id), max_age=60*60*24)  # 24 hours
        return response
    
    # Get user data from cookies
    user_id = request.cookies.get('user_id')
    display_name = request.cookies.get('display_name')
    
    # If this is player 1, redirect to game
    if game.player1_id == user_id:
        response = make_response(redirect(url_for('pvp.index')))
        response.set_cookie('game_id', str(game.game_id), max_age=60*60*24)  # 24 hours
        return response
    
    # If this is player 2 joining
    if not game.player2_id:
        # If no user_id or display_name, show name input form
        if not user_id or not display_name:
            return render_template('enter_name.htm', 
                                 room_code=room_code,
                                 is_player2=True)
        
        # Create user if not exists
        user = User.query.get(user_id)
        if not user:
            from routes.home import create_new_user
            user = create_new_user(user_id, display_name)
        
        # Add player 2 to game and initialize game state
        game.player2_id = user_id
        game.status = 'playing'  # Change status to playing
        game.current_player_id = game.player1_id  # Set current player to player 1
        game.board = [[None for _ in range(15)] for _ in range(15)]  # Initialize empty board
        db.session.commit()
        
        # Store game_id in cookie
        response = make_response(redirect(url_for('pvp.index')))
        response.set_cookie('game_id', str(game.game_id), max_age=60*60*24)  # 24 hours
        return response
    
    # If we get here, something went wrong
    return redirect(url_for('home.index'))

# Helper functions
def check_win(board, row, col, player_id):
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
            nx, ny = col, row
            
            # Count consecutive pieces in this direction
            for _ in range(4):  # Need 4 more to make 5 in a row
                nx, ny = nx + dx, ny + dy
                if (0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] == player_id):
                    count += 1
                else:
                    break
            
        if count >= 5:
            return True
    
    return False

def update_leaderboard(game):
    # Get or create leaderboard entry
    leaderboard = Leaderboard.query.filter_by(user_id=game.player1_id).first()
    if not leaderboard:
        leaderboard = Leaderboard(user_id=game.player1_id)
        db.session.add(leaderboard)
    
    # Update stats
    leaderboard.total_games += 1
    if game.winner_id == game.player1_id:
        leaderboard.wins += 1
    else:
        leaderboard.losses += 1
    
    # Calculate win rate
    leaderboard.win_rate = leaderboard.wins / leaderboard.total_games if leaderboard.total_games > 0 else 0
    
    db.session.commit()