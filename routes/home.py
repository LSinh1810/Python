import random
import string
from flask import Blueprint, render_template, request, redirect, url_for, make_response
from models import Game, User, Leaderboard, Avatar, Skin
from extensions import db
from sqlalchemy import desc

home_bp = Blueprint('home', __name__)

def generate_user_id():
    """Tạo ID ngẫu nhiên gồm 10 ký tự."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

@home_bp.route('/')
def index():
    # Kiểm tra xem người chơi đã có tên và ID trong cookie chưa
    user_id = request.cookies.get('user_id')
    display_name = request.cookies.get('display_name')

    if not display_name or not user_id:
        # Nếu chưa có, chuyển hướng đến trang nhập tên
        return redirect(url_for('home.enter_name'))

    # Lấy thông tin người dùng
    user = User.query.get(user_id)
    if not user:
        # Tạo người dùng mới nếu không tìm thấy
        user = User(user_id=user_id, displayName=display_name)
        db.session.add(user)
        db.session.commit()

    # Lấy dữ liệu leaderboard thực từ cơ sở dữ liệu
    leaderboard_data = db.session.query(
        User, Leaderboard
    ).join(
        Leaderboard, User.user_id == Leaderboard.user_id
    ).order_by(
        desc(Leaderboard.wins)
    ).limit(5).all()
    
    # Định dạng dữ liệu cho template
    leaderboard = []
    for user_data, leaderboard_entry in leaderboard_data:
        leaderboard.append({
            "user": {
                "username": user_data.displayName,
                "avatar": user_data.avatar or "/static/images/default_avatar.png"
            },
            "wins": leaderboard_entry.wins
        })
    
    # Tạo dữ liệu giả cho leaderboard nếu không có dữ liệu từ database
    if not leaderboard:
        leaderboard = [
            {
                "user": {
                    "username": "Nguyễn Văn A",
                    "avatar": "/static/images/avatar1.png"
                },
                "wins": 48
            },
            {
                "user": {
                    "username": "Trần Thị B",
                    "avatar": "/static/images/avatar2.png"
                },
                "wins": 36
            },
            {
                "user": {
                    "username": "Lê Văn C",
                    "avatar": "/static/images/default_avatar.png"
                },
                "wins": 29
            },
            {
                "user": {
                    "username": "Phạm Thị D",
                    "avatar": "/static/images/avatar1.png"
                },
                "wins": 21
            },
            {
                "user": {
                    "username": "Hoàng Văn E",
                    "avatar": "/static/images/avatar2.png"
                },
                "wins": 15
            }
        ]
    
    # Lấy dữ liệu icon và avatar từ cơ sở dữ liệu
    icons = Skin.query.limit(2).all()
    avatars = Avatar.query.limit(3).all()
    
    # Tạo dữ liệu giả cho icons và avatars nếu không có dữ liệu từ database
    if not icons:
        icons = [
            {
                "skin_id": 1,
                "name": "Icon 1",
                "image_url": "/static/images/icon1.png",
                "price": 100
            },
            {
                "skin_id": 2,
                "name": "Icon 2", 
                "image_url": "/static/images/icon2.png",
                "price": 200
            }
        ]
    
    if not avatars:
        avatars = [
            {
                "avatar_id": 1,
                "name": "Avatar 1",
                "image_url": "/static/images/avatar1.png",
                "price": 300
            },
            {
                "avatar_id": 2,
                "name": "Avatar 2",
                "image_url": "/static/images/avatar2.png",
                "price": 400
            },
            {
                "avatar_id": 3,
                "name": "Avatar Mặc định",
                "image_url": "/static/images/default_avatar.png",
                "price": 200
            }
        ]

    # Đọc danh sách vật phẩm đã sở hữu từ cookie
    owned_avatars = request.cookies.get('owned_avatars', '')
    owned_skins = request.cookies.get('owned_skins', '')
    
    # Chuyển đổi chuỗi cookie thành danh sách các ID
    user_avatar_ids = [int(id) for id in owned_avatars.split(',') if id.isdigit()]
    user_skin_ids = [int(id) for id in owned_skins.split(',') if id.isdigit()]
    
    # Thêm avatar mặc định (ID 3) nếu người dùng chưa có avatar nào
    if 3 not in user_avatar_ids:
        user_avatar_ids.append(3)
    
    # Lấy số tiền từ cookie
    user_coins = request.cookies.get('user_coins', '3000')

    return render_template('home.htm', 
                           leaderboard=leaderboard, 
                           icons=icons, 
                           avatars=avatars, 
                           username=display_name, 
                           user_id=user_id,
                           user=user,
                           user_avatar_ids=user_avatar_ids,
                           user_skin_ids=user_skin_ids,
                           user_coins=user_coins)

@home_bp.route('/enter_name', methods=['GET', 'POST'])
def enter_name():
    if request.method == 'POST':
        display_name = request.form.get('display_name')
        if not display_name:
            return render_template('set_name.htm', error="Tên không được để trống!")

        # Tạo ID ngẫu nhiên
        user_id = generate_user_id()

        # Lưu vào cơ sở dữ liệu
        user = User(user_id=user_id, displayName=display_name)
        db.session.add(user)
        db.session.commit()

        # Lưu vào cookie
        response = make_response(redirect(url_for('home.index')))
        response.set_cookie('display_name', display_name, max_age=60*60*24*30)  # Lưu trong 30 ngày
        response.set_cookie('user_id', user_id, max_age=60*60*24*30)  # Lưu trong 30 ngày
        response.set_cookie('user_coins', '3000', max_age=60*60*24*30)  # Lưu số tiền mặc định
        return response

    return render_template('set_name.htm')