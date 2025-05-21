from flask import Blueprint, render_template, redirect, url_for, request, make_response
from models import User, Game
from app import db
import qrcode
from io import BytesIO
import base64

qr_code_bp = Blueprint('qr_code', __name__)

@qr_code_bp.route('/qr_code/<room_code>')
def index(room_code):
    # Check if user has cookies
    user_id = request.cookies.get('user_id')
    display_name = request.cookies.get('display_name')
    
    if not user_id or not display_name:
        return redirect(url_for('home.enter_name'))
    
    # Get user data
    user = User.query.get(user_id)
    if not user:
        # Create user if not exists
        from routes.home import create_new_user
        user = create_new_user(user_id, display_name)
    
    # Generate QR code
    game_link = f"http://localhost:5000/join/{room_code}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(game_link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()

    return render_template('qrcode.htm', 
                         user=user, 
                         room_code=room_code, 
                         qr_code=qr_code_base64)

@qr_code_bp.route('/join/<room_code>')
def join_game(room_code):
    # Check if user has cookies
    user_id = request.cookies.get('user_id')
    display_name = request.cookies.get('display_name')
    
    if not user_id or not display_name:
        return redirect(url_for('home.enter_name'))
    
    # Get game data
    game = Game.query.filter_by(room_code=room_code).first()
    if not game:
        return redirect(url_for('home.index'))
    
    # Get user data
    user = User.query.get(user_id)
    if not user:
        # Create user if not exists
        from routes.home import create_new_user
        user = create_new_user(user_id, display_name)
    
    # If game already has 2 players, redirect to game
    if game.player1_id and game.player2_id:
        return redirect(url_for('pvp.index'))
    
    # If this is player 1, redirect to game
    if game.player1_id == user_id:
        return redirect(url_for('pvp.index'))
    
    # If this is player 2 joining
    if not game.player2_id:
        game.player2_id = user_id
        db.session.commit()
        return redirect(url_for('pvp.index'))
    
    # If we get here, something went wrong
    return redirect(url_for('home.index'))