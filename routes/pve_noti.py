from flask import Blueprint, render_template, redirect, url_for, request, make_response
from models import User, Game
from app import db
import random

pve_noti_bp = Blueprint('pve_noti', __name__)

@pve_noti_bp.route('/pve_noti')
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
    
    return render_template('pve_noti.htm', user=user, game_settings=game_settings)

@pve_noti_bp.route('/start_pve_game')
def start_pve_game():
    # Check if user has cookies
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('home.enter_name'))
    
    # Create a new game record for PVE
    new_game = Game(
        player1_id=user_id,
        player2_id=None,  # No player 2 for PVE
        status='ongoing',
        room_code=f"pve_{random.randint(100000, 999999)}"
    )
    
    db.session.add(new_game)
    db.session.commit()
    
    # Store game_id in cookie
    response = make_response(redirect(url_for('pve.index')))
    response.set_cookie('game_id', str(new_game.game_id), max_age=60*60*24)  # 24 hours
    
    return response