from flask import Blueprint, render_template, redirect, url_for, session, request, flash, make_response
from models import User, Leaderboard, UserAvatar, Avatar, Skin, UserSkin
from extensions import db
from sqlalchemy import desc

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def index():
    # Kiểm tra cookie người dùng
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('home.enter_name'))
    
    # Lấy thông tin người dùng
    user = User.query.get(user_id)
    if not user:
        # Create user if not exists
        from routes.home import create_new_user
        display_name = request.cookies.get('display_name')
        user = create_new_user(user_id, display_name)
    
    # Lấy danh sách avatar của người dùng
    user_avatars = db.session.query(
        Avatar
    ).join(
        UserAvatar, UserAvatar.avatar_id == Avatar.avatar_id
    ).filter(
        UserAvatar.user_id == user_id
    ).all()
    
    # Lấy danh sách skin của người dùng
    user_skins = db.session.query(
        Skin
    ).join(
        UserSkin, UserSkin.skin_id == Skin.skin_id
    ).filter(
        UserSkin.user_id == user_id
    ).all()
    
    # Lấy danh sách avatar có thể mua
    available_avatars = Avatar.query.filter(
        ~Avatar.avatar_id.in_([ua.avatar_id for ua in user_avatars])
    ).all()
    
    # Lấy danh sách skin có thể mua
    available_skins = Skin.query.filter(
        ~Skin.skin_id.in_([us.skin_id for us in user_skins])
    ).all()
    
    # Lấy số tiền từ cookie
    user_coins = request.cookies.get('user_coins', '3000')
    
    return render_template(
        'profile.htm', 
        user=user,
        user_avatars=user_avatars,
        user_skins=user_skins,
        available_avatars=available_avatars,
        available_skins=available_skins,
        user_coins=user_coins
    )

@profile_bp.route('/update_profile', methods=['POST'])
def update_profile():
    # Kiểm tra cookie người dùng
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('home.enter_name'))
    
    # Get form data
    display_name = request.form.get('displayName')
    
    # Validate display name
    if not display_name or len(display_name) < 3 or len(display_name) > 50:
        flash('Tên hiển thị phải từ 3-50 ký tự')
        return redirect(url_for('profile.index'))
    
    # Update user
    user = User.query.get(user_id)
    if user:
        user.displayName = display_name
        db.session.commit()
        
        # Update cookie
        response = make_response(redirect(url_for('profile.index')))
        response.set_cookie('display_name', display_name)
        flash('Cập nhật hồ sơ thành công')
        return response
    
    return redirect(url_for('profile.index'))

@profile_bp.route('/profile/change_avatar/<int:avatar_id>')
def change_avatar(avatar_id):
    # Kiểm tra cookie người dùng
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('home.enter_name'))
    
    # Kiểm tra xem người dùng có avatar này không
    user_avatar = UserAvatar.query.filter_by(
        user_id=user_id,
        avatar_id=avatar_id
    ).first()
    
    if not user_avatar:
        flash('Bạn chưa sở hữu avatar này')
        return redirect(url_for('profile.index'))
    
    # Lấy thông tin avatar
    avatar = Avatar.query.get(avatar_id)
    if not avatar:
        flash('Avatar không tồn tại')
        return redirect(url_for('profile.index'))
    
    # Cập nhật avatar cho người dùng
    user = User.query.get(user_id)
    if user:
        user.avatar = avatar.image_url
        db.session.commit()
        flash('Đã cập nhật avatar thành công')
    else:
        flash('Không tìm thấy người dùng')
    
    return redirect(url_for('profile.index'))

@profile_bp.route('/profile/change_skin/<int:skin_id>')
def change_skin(skin_id):
    # Kiểm tra cookie người dùng
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('home.enter_name'))
    
    # Kiểm tra xem người dùng có skin này không
    user_skin = UserSkin.query.filter_by(
        user_id=user_id,
        skin_id=skin_id
    ).first()
    
    if not user_skin:
        return redirect(url_for('profile.index'))
    
    # Lưu skin đã chọn vào cookie
    response = make_response(redirect(url_for('profile.index')))
    response.set_cookie('selected_skin', str(skin_id), max_age=60*60*24*30)  # 30 ngày
    
    return response

@profile_bp.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    # Delete user
    user = User.query.get(session['user_id'])
    if user:
        db.session.delete(user)
        db.session.commit()
        
        # Clear session
        session.clear()
        
        flash('Account deleted successfully')
    
    return redirect(url_for('home.login'))