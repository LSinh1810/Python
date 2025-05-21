from flask import Blueprint, render_template, redirect, url_for, request, make_response
from models import User, Game
from app import db
import random
import string

pvp_noti_bp = Blueprint('pvp_noti', __name__)

@pvp_noti_bp.route('/pvp_noti')
def index():
    # Check if user has cookies
    user_id = request.cookies.get('user_id')
    display_name = request.cookies.get('display_name')
    
    # If no cookies, redirect to name input page
    if not user_id or not display_name:
        return redirect(url_for('home.enter_name'))
    
    # Get user data
    user = User.query.get(user_id)
    if not user:
        # Create user if not exists
        from routes.home import create_new_user
        user = create_new_user(user_id, display_name)
    
    # Game settings (fixed as per requirements)
    game_settings = {
        'move_time': 30,  # 30 seconds per move
        'player_time': 5,  # 5 minutes per player
        'first_move': 'random'  # Random first move
    }
    
    return render_template('pvp_noti.htm', user=user, game_settings=game_settings)

@pvp_noti_bp.route('/create_pvp_game')
def create_pvp_game():
    # Check if user has cookies
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('home.enter_name'))
    
    # Generate a random 6-digit room code
    room_code = ''.join(random.choices(string.digits, k=6))
    
    # Create a new game record for PVP
    new_game = Game(
        player1_id=user_id,
        status='waiting',  # Change status to 'waiting'
        room_code=room_code
    )
    new_game.current_player_id = user_id # Gán người chơi hiện tại là người tạo phòng
    
    db.session.add(new_game)
    db.session.commit()
    
<<<<<<< HEAD
    # Store game_id in cookie and redirect to waiting room
    response = make_response(redirect(url_for('pvp.wait_for_opponent', room_code=room_code)))
=======
    # Store game_id in cookie
    response = make_response(redirect(url_for('pvp.index')))
>>>>>>> 9659b1dfd28954a0967c6643b0ede3957388a8ab
    response.set_cookie('game_id', str(new_game.game_id), max_age=60*60*24)  # 24 hours
    
    return response

@pvp_noti_bp.route('/join_pvp_game', methods=['POST'])
def join_pvp_game():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('home.enter_name'))

    room_code = request.form.get('room_code')
    game = Game.query.filter_by(room_code=room_code, status='waiting').first()

    if game:
        if game.player1_id == user_id:
            # Player is trying to join their own game again
            # Redirect to waiting room or show an error
            return redirect(url_for('pvp.wait_for_opponent', room_code=room_code))
        
        game.player2_id = user_id
        game.status = 'ongoing'
        db.session.commit()
        
        response = make_response(redirect(url_for('pvp.pvp_game', room_code=room_code)))
        response.set_cookie('game_id', str(game.game_id), max_age=60*60*24)
        return response
    else:
        # Handle error: room not found or not available
        # You might want to redirect back with an error message
        return redirect(url_for('.index', error='Room not found or already full'))