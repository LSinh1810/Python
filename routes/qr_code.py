from flask import Blueprint, render_template, redirect, url_for, request, make_response
from models import User, Game
from app import db
import qrcode
from io import BytesIO
import base64

home_bp = Blueprint('home', __name__)

qr_code_bp = Blueprint('qr_code', __name__)

@qr_code_bp.route('/qr_code')
def index():
    # Dữ liệu giả
    user = {"username": "Player1", "avatar": "/static/images/avatar1.png"}
    room_code = "ABC123"
    game_link = f"http://localhost:5000/join_game/{room_code}"

    return render_template('qr_code.htm', user=user, room_code=room_code, game_link=game_link)

@qr_code_bp.route('/join_game/<room_code>')
def join_game(room_code):
    # Lấy thông tin người chơi từ cookie
    user_id = request.cookies.get('user_id')
    display_name = request.cookies.get('username')

    # Nếu không có cookie, chuyển hướng đến trang nhập tên
    if not user_id or not display_name:
        response = make_response(redirect(url_for('home.index')))
        response.set_cookie('join_room', room_code, max_age=60*60)  # 1 giờ
        return response

    # Tìm game với room_code
    game = Game.query.filter_by(room_code=room_code).first()
    if not game:
        response = make_response(redirect(url_for('home.index')))
        return response

    # Nếu là người chơi thứ hai, thêm vào game
    if game.player1_id != user_id and not game.player2_id:
        game.player2_id = user_id
        db.session.commit()

    # Lưu game_id vào cookie
    response = make_response(redirect(url_for('pvp.index')))
    response.set_cookie('game_id', str(game.game_id), max_age=60*60*24)  # 24 giờ

    # Nếu cả hai người chơi đã vào, chuyển đến game
    if game.player1_id and game.player2_id:
        return response

    # Nếu chưa, hiển thị màn hình chờ
    return render_template('waiting.htm', user={"username": display_name}, room_code=room_code)