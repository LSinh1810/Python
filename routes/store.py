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
    
    # In ra log để debug
    print("Avatars in store:", avatars)
    print("User owned avatar IDs:", user_avatar_ids)
    
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
    
    # Lấy thông tin người dùng
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'})
    
    # Lấy số tiền từ cookie
    user_coins = int(request.cookies.get('user_coins', '3000'))
    
    # Xác định loại vật phẩm và giá
    if item_type == "avatar":
        item = Avatar.query.get(item_id)
        if not item:
            return jsonify({'success': False, 'message': 'Avatar không tồn tại'})
        price = item.price
    else:
        item = Skin.query.get(item_id)
        if not item:
            return jsonify({'success': False, 'message': 'Skin không tồn tại'})
        price = item.price
    
    # Kiểm tra số tiền
    if user_coins < price:
        return jsonify({'success': False, 'message': 'Số tiền không đủ'})
    
    # Kiểm tra xem đã sở hữu vật phẩm chưa
    if item_type == "avatar":
        existing_item = UserAvatar.query.filter_by(user_id=user_id, avatar_id=item_id).first()
        if existing_item:
            return jsonify({'success': False, 'message': 'Bạn đã sở hữu avatar này'})
    else:
        existing_item = UserSkin.query.filter_by(user_id=user_id, skin_id=item_id).first()
        if existing_item:
            return jsonify({'success': False, 'message': 'Bạn đã sở hữu skin này'})
    
    # Mua vật phẩm
    try:
        # Trừ tiền
        user_coins -= price
        
        # Lưu vào database
        if item_type == "avatar":
            user_avatar = UserAvatar(user_id=user_id, avatar_id=item_id)
            db.session.add(user_avatar)
        else:
            user_skin = UserSkin(user_id=user_id, skin_id=item_id)
            db.session.add(user_skin)
        
        db.session.commit()
        
        # Cập nhật cookie
        response = make_response(jsonify({
            'success': True,
            'message': 'Mua hàng thành công',
            'coins': user_coins
        }))
        response.set_cookie('user_coins', str(user_coins))
        
        return response
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Có lỗi xảy ra khi mua hàng'}) 