from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request
from models import User, Game, Move, Leaderboard
from extensions import db, socketio
import random
import numpy as np
from datetime import datetime
from ai_player import AIPlayer

pve_bp = Blueprint('pve', __name__)

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
    
    # Không cần lấy các nước đi từ database
    moves = []
    
    return render_template('pve.htm', 
                          user=user, 
                          game=game, 
                          moves=moves)

@pve_bp.route('/make_move', methods=['POST'])
def make_move():
    data = request.json
    x = data.get('x')
    y = data.get('y')
    game_id = data.get('game_id')
    
    # Lấy user_id từ cookie
    user_id = request.cookies.get('user_id')
    
    if not user_id or not game_id:
        return jsonify({'status': 'error', 'message': 'Không đăng nhập'})
    
    # Get game data
    game = Game.query.get(game_id)
    if not game or game.status != 'ongoing':
        return jsonify({'status': 'error', 'message': 'Trò chơi không tìm thấy hoặc đã kết thúc'})
    
    # Không cần kiểm tra vị trí trong database, vì không lưu vào database
    # Tất cả đều được xử lý trên client-side
    
    # Lấy bảng cờ từ yêu cầu
    board = data.get('board', [[0 for _ in range(15)] for _ in range(15)])
    
    # Kiểm tra win với bảng cờ hiện tại
    if check_win_from_board(board, x, y, 1):  # 1 represents player
        game.status = 'finished'
        game.winner_id = user_id
        db.session.commit()
        
        # Update leaderboard
        update_leaderboard(user_id, True)
        
        return jsonify({
            'status': 'win',
            'message': 'Bạn thắng!',
            'move': {
                'x': x,
                'y': y,
                'player_id': user_id
            }
        })
    
    # Cập nhật bảng cờ với nước đi mới của người chơi
    board[y][x] = 1  # 1 for player
    
    # Sử dụng AI từ ai_player.py
    try:
        ai = AIPlayer()
        ai_x, ai_y = ai.get_move(board)
        
        # Kiểm tra nếu AI đặt vào ô đã có quân
        if board[ai_y][ai_x] != 0:
            # Tìm ô trống ngẫu nhiên
            empty_cells = []
            for r in range(15):
                for c in range(15):
                    if board[r][c] == 0:
                        empty_cells.append((c, r))
            
            if empty_cells:
                ai_x, ai_y = random.choice(empty_cells)
            else:
                # Nếu không còn ô trống, hòa
                game.status = 'finished'
                db.session.commit()
                return jsonify({
                    'status': 'draw',
                    'message': 'Hòa!',
                    'move': {
                        'x': x,
                        'y': y,
                        'player_id': user_id
                    }
                })
        
        # Cập nhật bảng cờ với nước đi của AI
        board[ai_y][ai_x] = 2  # 2 for AI
        
        # Kiểm tra nếu AI thắng
        if check_win_from_board(board, ai_x, ai_y, 2):
            game.status = 'finished'
            game.winner_id = None  # AI wins
            db.session.commit()
            
            # Update leaderboard
            update_leaderboard(user_id, False)
            
            return jsonify({
                'status': 'lose',
                'message': 'AI thắng!',
                'move': {
                    'x': x,
                    'y': y,
                    'player_id': user_id
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
                'player_id': user_id
            },
            'ai_move': {
                'x': ai_x,
                'y': ai_y,
                'player_id': None
            }
        })
    except Exception as e:
        print(f"Lỗi khi xử lý AI: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Lỗi khi xử lý AI: {str(e)}',
            'move': {
                'x': x,
                'y': y,
                'player_id': user_id
            }
        })

@pve_bp.route('/give_up')
def give_up():
    # Lấy thông tin từ cookie
    user_id = request.cookies.get('user_id')
    game_id = request.cookies.get('game_id')
    
    if not user_id or not game_id:
        return redirect(url_for('home.enter_name'))
    
    # Get game data
    game = Game.query.get(game_id)
    if not game:
        return redirect(url_for('home.index'))
    
    # Update game status
    game.status = 'cancelled'
    db.session.commit()
    
    # Update leaderboard
    update_leaderboard(user_id, False)
    
    # Trở về trang chủ thay vì trang after_game
    return redirect(url_for('home.index'))

# Helper functions
def check_win_from_board(board, x, y, player_value):
    """
    Kiểm tra thắng dựa trên bảng cờ
    player_value: 1 cho người chơi, 2 cho AI
    """
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
                if (0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] == player_value):
                    count += 1
                else:
                    break
            
        if count >= 5:
            return True
    
    return False

def update_leaderboard(user_id, is_win):
    # Bỏ qua việc cập nhật leaderboard
    pass