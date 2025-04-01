import random
import string
from flask import Blueprint, render_template, request, redirect, url_for, make_response
from models import Game, User, Leaderboard, Avatar, Skin, UserAvatar, UserSkin
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
    all_icons = Skin.query.all()
    all_avatars = Avatar.query.all()
    
    # Lọc avatar và loại bỏ trùng lặp
    avatars = []
    added_urls = set()
    
    # Tìm avatar1, avatar2, avatar3 (không lấy default_avatar)
    for avatar in all_avatars:
        if avatar.image_url in added_urls:
            continue  # Bỏ qua nếu URL này đã được thêm
            
        if "avatar1.png" in avatar.image_url or "avatar2.png" in avatar.image_url or "avatar3.png" in avatar.image_url:
            avatars.append(avatar)
            added_urls.add(avatar.image_url)
    
    # Lọc skin và loại bỏ trùng lặp
    icons = []
    added_urls = set()  # Reset lại set cho skin
    
    # Tìm icon1, icon2 (không lấy default_icon)
    for skin in all_icons:
        if skin.image_url in added_urls:
            continue  # Bỏ qua nếu URL này đã được thêm
            
        if "icon1.png" in skin.image_url or "icon2.png" in skin.image_url:
            icons.append(skin)
            added_urls.add(skin.image_url)
    
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
                "name": "Avatar 3",
                "image_url": "/static/images/avatar3.png",
                "price": 500
            }
        ]

    # Lấy danh sách vật phẩm đã sở hữu từ database
    user_avatars = UserAvatar.query.filter_by(user_id=user_id).all()
    user_skins = UserSkin.query.filter_by(user_id=user_id).all()
    
    # Chuyển đổi thành danh sách các ID
    user_avatar_ids = [user_avatar.avatar_id for user_avatar in user_avatars]
    user_skin_ids = [user_skin.skin_id for user_skin in user_skins]
    
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