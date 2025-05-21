from flask import Blueprint, render_template, redirect, url_for, request, make_response
from models import User, Game, Move
from app import db, socketio
from flask_socketio import emit
import random

after_game_bp = Blueprint('after_game', __name__)

@after_game_bp.route('/after_game/<int:game_id>')
def index(game_id):
    # Check if user has cookies
    user_id = request.cookies.get('user_id')
    
    if not user_id:
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
    
    # Get winner data
    winner = User.query.get(game.winner_id) if game.winner_id else None
    
    # Check if PVE or PVP
    is_pve = game.player2_id is None
    
    # Get opponent data for PVP
    opponent = None
    if not is_pve:
        opponent_id = game.player2_id if game.player1_id == user_id else game.player1_id
        opponent = User.query.get(opponent_id)
    
    # Get moves count
    moves_count = Move.query.filter_by(game_id=game_id).count()
    
    return render_template('after_game.htm', 
                          user=user, 
                          game=game, 
                          winner=winner,
                          is_pve=is_pve,
                          opponent=opponent,
                          moves_count=moves_count)

@after_game_bp.route('/replay/<int:game_id>')
def replay(game_id):
    # Check if user has cookies
    user_id = request.cookies.get('user_id')
    
    if not user_id:
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
    
    # Check if PVE or PVP
    is_pve = game.player2_id is None
    
    if is_pve:
        # For PVE, create a new game immediately
        new_game = Game(
            player1_id=user_id,
            player2_id=None,
            status='ongoing',
            room_code=f"pve_{random.randint(100000, 999999)}"  # Generate new random room code
        )
        
        db.session.add(new_game)
        db.session.commit()
        
        # Store game_id in cookie
        response = make_response(redirect(url_for('pve.index')))
        response.set_cookie('game_id', str(new_game.game_id), max_age=60*60*24)  # 24 hours
        
        return response
    else:
        # For PVP, mark player as ready to replay
        # We'll use a database table to track this instead of session
        from models import ReplayRequest
        
        # Check if request already exists
        existing_request = ReplayRequest.query.filter_by(
            game_id=game_id,
            player_id=user_id
        ).first()
        
        if not existing_request:
            # Create new request
            replay_request = ReplayRequest(
                game_id=game_id,
                player_id=user_id
            )
            db.session.add(replay_request)
            db.session.commit()
        
        # Notify other player
        socketio.emit('replay_ready', {
            'player_id': user_id,
            'game_id': game_id
        }, room=f"game_{game.room_code}")
        
        # Check if both players are ready
        opponent_id = game.player2_id if game.player1_id == user_id else game.player1_id
        
        opponent_request = ReplayRequest.query.filter_by(
            game_id=game_id,
            player_id=opponent_id
        ).first()
        
        if opponent_request:
            # Both players ready, create new game
            new_game = Game(
                player1_id=game.player1_id,
                player2_id=game.player2_id,
                status='ongoing',
                room_code=game.room_code
            )
            
            db.session.add(new_game)
            db.session.commit()
            
            # Delete replay requests
            ReplayRequest.query.filter_by(game_id=game_id).delete()
            db.session.commit()
            
            # Notify both players
            socketio.emit('game_restart', {
                'game_id': new_game.game_id
            }, room=f"game_{game.room_code}")
            
            # Store game_id in cookie
            response = make_response(redirect(url_for('pvp.index')))
            response.set_cookie('game_id', str(new_game.game_id), max_age=60*60*24)  # 24 hours
            
            return response
        
        # Wait for other player
        return render_template('waiting_replay.htm', game=game, user=user)

@after_game_bp.route('/leave_room/<int:game_id>')
def leave_room(game_id):
    # Check if user has cookies
    user_id = request.cookies.get('user_id')
    
    if not user_id:
        return redirect(url_for('home.enter_name'))
    
    # Get game data
    game = Game.query.get(game_id)
    if not game:
        return redirect(url_for('home.index'))
    
    # Delete any replay requests
    from models import ReplayRequest
    ReplayRequest.query.filter_by(
        game_id=game_id,
        player_id=user_id
    ).delete()
    db.session.commit()
    
    # Notify other player if PVP
    if game.player2_id:
        socketio.emit('player_left', {
            'player_id': user_id
        }, room=f"game_{game.room_code}")
    
    # Clear game_id cookie
    response = make_response(redirect(url_for('home.index')))
    response.delete_cookie('game_id')
    
    return response