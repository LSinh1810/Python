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
    
    # Lấy avatars từ database và lọc
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
    
    # Lấy skins từ database và lọc
    all_skins = Skin.query.all()
    
    # Lọc skin và loại bỏ trùng lặp
    skins = []
    added_urls = set()  # Reset lại set cho skin
    
    # Tìm icon1, icon2 (không lấy default_icon)
    for skin in all_skins:
        if skin.image_url in added_urls:
            continue  # Bỏ qua nếu URL này đã được thêm
            
        if "icon1.png" in skin.image_url or "icon2.png" in skin.image_url:
            skins.append(skin)
            added_urls.add(skin.image_url)
    
    # Lấy danh sách vật phẩm đã sở hữu từ database
    user_avatars = UserAvatar.query.filter_by(user_id=user_id).all()
    user_skins = UserSkin.query.filter_by(user_id=user_id).all()
    
    # Chuyển đổi thành danh sách các ID
    user_avatar_ids = [user_avatar.avatar_id for user_avatar in user_avatars]
    user_skin_ids = [user_skin.skin_id for user_skin in user_skins]
    
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