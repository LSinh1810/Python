from flask import Blueprint, render_template, request, redirect, url_for, jsonify, make_response
from models import User, Avatar, Skin, UserAvatar, UserSkin
from app import db

store_bp = Blueprint('store', __name__)

@store_bp.route('/store')
def index():
    # Kiểm tra user cookie
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('home.enter_name'))
    
    # Lấy thông tin người dùng
    user = User.query.get(user_id)
    if not user:
        # Tạo user giả nếu không tìm thấy
        user = {
            'displayName': request.cookies.get('display_name', 'Người chơi'),
            'avatar': '/static/images/default_avatar.png'
        }
    
    # Dữ liệu giả cho avatar
    avatars = [
        {
            'avatar_id': 1,
            'name': 'Avatar 1', 
            'image_url': '/static/images/avatar1.png',
            'price': 300
        },
        {
            'avatar_id': 2,
            'name': 'Avatar 2',
            'image_url': '/static/images/avatar2.png',
            'price': 400
        },
        {
            'avatar_id': 3,
            'name': 'Avatar Mặc định',
            'image_url': '/static/images/default_avatar.png',
            'price': 200
        }
    ]
    
    # Dữ liệu giả cho skin
    skins = [
        {
            'skin_id': 1,
            'name': 'Icon 1',
            'image_url': '/static/images/icon1.png',
            'price': 100
        },
        {
            'skin_id': 2,
            'name': 'Icon 2',
            'image_url': '/static/images/icon2.png',
            'price': 200
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
    
    return render_template(
        'store.htm',
        user=user,
        avatars=avatars,
        skins=skins,
        user_avatar_ids=user_avatar_ids,
        user_skin_ids=user_skin_ids,
        user_coins=user_coins
    )

@store_bp.route('/buy_item/<string:item_type>/<int:item_id>', methods=['POST'])
def buy_item(item_type, item_id):
    # Kiểm tra user cookie
    user_id = request.cookies.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Bạn cần đăng nhập để mua hàng'})
    
    # Xác định loại vật phẩm
    item_name = "Avatar" if item_type == "avatar" else "Icon"
    
    # Đọc cookie hiện tại của người dùng để cập nhật vật phẩm sở hữu
    owned_avatars = request.cookies.get('owned_avatars', '')
    owned_skins = request.cookies.get('owned_skins', '')
    
    # Chuyển đổi chuỗi cookie thành danh sách các ID
    owned_avatar_ids = [int(id) for id in owned_avatars.split(',') if id.isdigit()]
    owned_skin_ids = [int(id) for id in owned_skins.split(',') if id.isdigit()]
    
    # Kiểm tra xem người dùng đã sở hữu vật phẩm chưa
    if (item_type == 'avatar' and item_id in owned_avatar_ids) or \
       (item_type == 'skin' and item_id in owned_skin_ids):
        return jsonify({'success': False, 'message': f'Bạn đã sở hữu {item_name} này rồi'})
    
    # Lấy thông tin giá của vật phẩm
    item_price = 0
    if item_type == 'avatar':
        # Dữ liệu giả cho avatar
        avatars = [
            {'avatar_id': 1, 'price': 300},
            {'avatar_id': 2, 'price': 400},
            {'avatar_id': 3, 'price': 200}
        ]
        for avatar in avatars:
            if avatar['avatar_id'] == item_id:
                item_price = avatar['price']
                break
    else:  # skin
        # Dữ liệu giả cho skin
        skins = [
            {'skin_id': 1, 'price': 100},
            {'skin_id': 2, 'price': 200}
        ]
        for skin in skins:
            if skin['skin_id'] == item_id:
                item_price = skin['price']
                break
    
    # Lấy số tiền hiện tại từ cookie
    user_coins = int(request.cookies.get('user_coins', '3000'))
    
    # Kiểm tra xem người dùng có đủ tiền không
    if user_coins < item_price:
        return jsonify({'success': False, 'message': 'Bạn không đủ tiền để mua vật phẩm này'})
    
    # Trừ tiền người dùng
    new_user_coins = user_coins - item_price
    
    # Thêm vật phẩm vào danh sách sở hữu
    if item_type == 'avatar':
        owned_avatar_ids.append(item_id)
        new_owned_avatars = ','.join(map(str, owned_avatar_ids))
    else:  # skin
        owned_skin_ids.append(item_id)
        new_owned_skins = ','.join(map(str, owned_skin_ids))
    
    # Tạo response thành công
    response = jsonify({
        'success': True, 
        'message': f'Mua {item_name} thành công!',
        'remaining_coins': new_user_coins
    })
    
    # Lưu danh sách vật phẩm mới vào cookie (30 ngày)
    if item_type == 'avatar':
        response.set_cookie('owned_avatars', new_owned_avatars, max_age=60*60*24*30)
    else:  # skin
        response.set_cookie('owned_skins', new_owned_skins, max_age=60*60*24*30)
    
    # Lưu số tiền mới vào cookie
    response.set_cookie('user_coins', str(new_user_coins), max_age=60*60*24*30)
    
    return response 