from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, make_response
from models import User, Game, Move, Leaderboard
from extensions import db, socketio
from flask_socketio import emit, join_room, leave_room
import json
from datetime import datetime

pvp_bp = Blueprint('pvp', __name__)

@pvp_bp.route('/pvp/wait/<room_code>')
def wait_for_opponent(room_code):
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('home.enter_name'))
    
    game = Game.query.filter_by(room_code=room_code, status='waiting').first()
    if not game:
        return redirect(url_for('pvp_noti.index', error='Game room not found or already started.'))

    if str(game.player1_id) != user_id:
        return redirect(url_for('pvp_noti.index', error='Invalid access to waiting room.'))

    user = User.query.get(user_id)
    current_user_display_name = user.displayName if user else "Player 1"

    return render_template('wait_for_opponent.htm', room_code=room_code, game_id=game.game_id, display_name=current_user_display_name)

@pvp_bp.route('/pvp/game/<room_code>') # Changed route
def pvp_game(room_code): # Changed function name from index
    user_id = request.cookies.get('user_id')
    game_id_cookie = request.cookies.get('game_id')
    
    if not user_id:
        return redirect(url_for('home.enter_name'))
    
    game = Game.query.filter_by(room_code=room_code).first()
    if not game:
        return redirect(url_for('home.index', error='Game not found for this room code.'))

    if game_id_cookie and str(game.game_id) != game_id_cookie:
        return redirect(url_for('home.index', error='Game session mismatch.'))
    
    if str(game.player1_id) != user_id and (not game.player2_id or str(game.player2_id) != user_id):
        return redirect(url_for('home.index', error='You are not a player in this game.'))

    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('home.enter_name', error='User not found.'))
        
    opponent_id = game.player2_id if str(game.player1_id) == user_id else game.player1_id
    opponent = User.query.get(opponent_id) if opponent_id else None
    
    moves = Move.query.filter_by(game_id=game.game_id).order_by(Move.move_order).all()
    is_player1 = str(game.player1_id) == user_id
    player1_obj_for_template = User.query.get(game.player1_id)
    player2_obj_for_template = User.query.get(game.player2_id) if game.player2_id else None
    
    print(f"[DEBUG pvp_game] Rendering pvp.htm for user: {user_id}")
    print(f"[DEBUG pvp_game] Game ID: {game.game_id}, DB game.player1_id: {game.player1_id}, DB game.player2_id: {game.player2_id}")
    print(f"[DEBUG pvp_game] Object player1 for template: {player1_obj_for_template.user_id if player1_obj_for_template else 'None'}")
    print(f"[DEBUG pvp_game] Object player2 for template: {player2_obj_for_template.user_id if player2_obj_for_template else 'None'}")
    print(f"[DEBUG pvp_game] is_player1 (current user is game.player1_id?): {is_player1}")
    print(f"[DEBUG pvp_game] game.current_player_id: {game.current_player_id}")

    response = make_response(render_template('pvp.htm', 
                                            user=user,
                                            player1=player1_obj_for_template,
                                            player2=player2_obj_for_template,
                                            opponent=opponent,
                                            game=game, 
                                            moves=moves,
                                            is_player1=is_player1,
                                            room_code=game.room_code))
    response.set_cookie('game_id', str(game.game_id), max_age=60*60*24)
    return response

@socketio.on('join_pvp_room') # Renamed event
def on_join_pvp_room(data):
    room = data['room'] 
    user_id = request.cookies.get('user_id')
    user = User.query.get(user_id)
    display_name = user.displayName if user else 'Anonymous'
    
    join_room(room)
    print(f"{display_name} has joined room {room}")
    emit('status', {'msg': f'{display_name} has joined the room.'}, room=room)
    
    game = Game.query.filter_by(room_code=room).first()
    if game and game.player1_id and game.player2_id and game.status == 'ongoing':
        player1 = User.query.get(game.player1_id)
        player2 = User.query.get(game.player2_id)
        print(f"[SocketIO on_join_pvp_room] Emitting 'opponent_joined'. Game status: {game.status}, current_player_id from DB: {game.current_player_id}")
        emit('opponent_joined', {
            'message': f'{player2.displayName if player2 else "Opponent"} has joined. The game will start!',
            'room_code': room,
            'player1_id': game.player1_id, 
            'player1_name': player1.displayName if player1 else "Player 1",
            'player2_id': game.player2_id, 
            'player2_name': player2.displayName if player2 else "Player 2",
            'current_player_id': game.current_player_id,
            'game_url': url_for('pvp.pvp_game', room_code=room, _external=True)
        }, room=room)

@socketio.on('leave_pvp_room') # Renamed event
def on_leave_pvp_room(data):
    room = data['room']
    user_id = request.cookies.get('user_id')
    user = User.query.get(user_id)
    display_name = user.displayName if user else 'Anonymous'
    leave_room(room)
    print(f"{display_name} has left room {room}")
    emit('status', {'msg': f'{display_name} has left the room.'}, room=room)

@socketio.on('make_move')
def handle_move(data):
    print(f"[SocketIO] Received 'make_move' event with data: {data}")
    game_id = data.get('game_id')
    x = data.get('x')
    y = data.get('y')
    player_id = data.get('player_id')
    room = data.get('room')

    if not all([game_id, x is not None, y is not None, player_id, room]):
        print(f"[SocketIO] Invalid data received for 'make_move': {data}")
        emit('error', {'msg': 'Invalid move data received.'}, room=request.sid)
        return
    
    game = Game.query.get(game_id)
    if not game or game.status != 'ongoing':
        emit('error', {'msg': 'Game not found or not ongoing'}, room=room)
        return

    # Kiểm tra xem có đúng lượt của người chơi này không
    if str(game.current_player_id) != str(player_id):
        emit('error', {'msg': 'Not your turn!'}, room=request.sid) # Gửi lỗi về cho client vừa đi sai lượt
        print(f"[SocketIO] Invalid turn: User {player_id} tried to move, but current turn is for {game.current_player_id}")
        return
    
    existing_move = Move.query.filter_by(game_id=game_id, position_x=x, position_y=y).first()
    if existing_move:
        emit('error', {'msg': 'Position already taken'}, room=room)
        return
    
    last_move = Move.query.filter_by(game_id=game_id).order_by(Move.move_order.desc()).first()
    move_order = 1 if not last_move else last_move.move_order + 1
    
    # Create new move with combined position string
    new_move = Move(
        game_id=game_id,
        player_id=player_id,
        position=f"{x},{y}",  # Create combined position string
        move_order=move_order,
        position_x=x,
        position_y=y
    )
    
    db.session.add(new_move)
    db.session.commit()
    
    # Determine opponent_id for the next turn
    opponent_id = None
    if str(game.player1_id) == str(player_id):
        opponent_id = game.player2_id
    else:
        opponent_id = game.player1_id

    # Check for win
    if check_win(game_id, x, y, player_id):
        game.status = 'finished'
        game.winner_id = player_id
        # game.current_player_id = None # Optional: Clear current player on game end
        db.session.commit()
        
        update_leaderboard(player_id, True)
        if opponent_id: # Ensure opponent_id was found before updating their leaderboard
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
        # Update current_player_id in the game
        game.current_player_id = opponent_id
        db.session.commit()

        emit('move_made', {
            'x': x,
            'y': y,
            'player_id': player_id,
            'next_player_id': opponent_id 
        }, room=room)

@socketio.on('time_up_forfeit')
def handle_time_up(data):
    game_id = data['game_id']
    player_id_timed_out = data['player_id']
    room = data['room']

    game = Game.query.get(game_id)
    if not game or game.status != 'ongoing':
        emit('error', {'msg': 'Game not found or already ended for time up forfeit.'}, room=room)
        return

    # Determine winner
    winner_id = None
    if str(game.player1_id) == str(player_id_timed_out):
        winner_id = game.player2_id
    elif str(game.player2_id) == str(player_id_timed_out):
        winner_id = game.player1_id
    else:
        # This shouldn't happen if player_id_timed_out is valid
        emit('error', {'msg': 'Invalid player ID for time out.'}, room=room)
        return

    game.status = 'finished'
    game.winner_id = winner_id
    db.session.commit()

    update_leaderboard(winner_id, True)
    update_leaderboard(player_id_timed_out, False)

    emit('game_over', {
        'winner_id': winner_id,
        'reason': f'Player {User.query.get(player_id_timed_out).displayName} ran out of time.'
    }, room=room)

@socketio.on('chat_message')
def handle_chat(data):
    room = data['room']
    message = data['message']
    user_id = request.cookies.get('user_id')
    user = User.query.get(user_id) 
    sender_name = user.displayName if user else session.get('display_name', 'Anonymous')
    
    emit('new_message', {
        'sender': sender_name,
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
    leaderboard = Leaderboard.query.filter_by(user_id=user_id).first()
    if not leaderboard:
        leaderboard = Leaderboard(user_id=user_id,
                                wins=0, 
                                losses=0, 
                                total_games=0, 
                                win_rate=0.0)
        db.session.add(leaderboard)
    else:
        # Đảm bảo các giá trị không phải là None nếu bản ghi đã tồn tại nhưng có thể có giá trị null từ DB (ít khả năng nếu default hoạt động)
        if leaderboard.wins is None: leaderboard.wins = 0
        if leaderboard.losses is None: leaderboard.losses = 0
        if leaderboard.total_games is None: leaderboard.total_games = 0
        if leaderboard.win_rate is None: leaderboard.win_rate = 0.0
    
    leaderboard.total_games += 1
    if is_win:
        leaderboard.wins += 1
    else:
        leaderboard.losses += 1
    
    if leaderboard.total_games > 0:
        leaderboard.win_rate = round((leaderboard.wins / leaderboard.total_games) * 100, 2) # Tính tỷ lệ phần trăm, làm tròn 2 chữ số
    else:
        leaderboard.win_rate = 0.0
    
    db.session.commit()