from app import create_app, db
from models import User, Avatar, Skin, Leaderboard, UserAvatar, UserSkin
import random

# Danh sách avatar mẫu (sử dụng hình ảnh có sẵn)
sample_avatars = [
    {"name": "Mặc định", "image_url": "/static/images/default_avatar.png", "price": 0},
    {"name": "Avatar 1", "image_url": "/static/images/avatar1.png", "price": 100},
    {"name": "Avatar 2", "image_url": "/static/images/avatar2.png", "price": 200},
    {"name": "Avatar 3", "image_url": "/static/images/avatar3.png", "price": 300}
]

# Danh sách skin mẫu (sử dụng icon có sẵn)
sample_skins = [
    {"name": "Mặc định", "image_url": "/static/images/default_icon.png", "price": 0},
    {"name": "Icon 1", "image_url": "/static/images/icon1.png", "price": 150},
    {"name": "Icon 2", "image_url": "/static/images/icon2.png", "price": 250}
]

# Danh sách người dùng mẫu
sample_users = [
    {"user_id": "user1", "displayName": "Người chơi 1"},
    {"user_id": "user2", "displayName": "Người chơi 2"},
    {"user_id": "user3", "displayName": "Người chơi 3"},
    {"user_id": "user4", "displayName": "Người chơi 4"},
    {"user_id": "user5", "displayName": "Người chơi 5"},
    {"user_id": "user6", "displayName": "Người chơi 6"},
    {"user_id": "user7", "displayName": "Người chơi 7"},
    {"user_id": "user8", "displayName": "Người chơi 8"},
    {"user_id": "user9", "displayName": "Người chơi 9"},
    {"user_id": "user10", "displayName": "Người chơi 10"}
]

def seed_database():
    app = create_app()
    with app.app_context():
        # Tạo dữ liệu avatar
        for avatar_data in sample_avatars:
            avatar = Avatar(**avatar_data)
            db.session.add(avatar)
        
        # Tạo dữ liệu skin
        for skin_data in sample_skins:
            skin = Skin(**skin_data)
            db.session.add(skin)
        
        # Lưu trước để có thể truy xuất ID
        db.session.commit()
        
        # Tạo dữ liệu người dùng và leaderboard
        for user_data in sample_users:
            # Tạo người dùng
            user = User(**user_data)
            
            # Chọn ngẫu nhiên 1 trong 4 avatar có sẵn
            random_avatar = random.choice(Avatar.query.all())
            user.avatar = random_avatar.image_url
                
            db.session.add(user)
            db.session.commit()  # Lưu để có được user_id
            
            # Tạo bản ghi leaderboard
            wins = random.randint(0, 50)  # Số trận thắng ngẫu nhiên
            leaderboard = Leaderboard(user_id=user.user_id, wins=wins)
            db.session.add(leaderboard)
            
            # Gán avatar đã chọn cho người dùng
            user_avatar = UserAvatar(user_id=user.user_id, avatar_id=random_avatar.avatar_id)
            db.session.add(user_avatar)
            
            # Gán skin mặc định cho người dùng
            default_skin = Skin.query.filter_by(price=0).first()
            if default_skin:
                user_skin = UserSkin(user_id=user.user_id, skin_id=default_skin.skin_id)
                db.session.add(user_skin)
        
        # Đảm bảo tất cả avatar được sử dụng bằng cách gán cho người dùng
        all_avatars = Avatar.query.all()
        for avatar in all_avatars:
            # Chọn một người dùng ngẫu nhiên
            random_user = random.choice(User.query.all())
            # Kiểm tra xem người dùng đã có avatar này chưa
            existing = UserAvatar.query.filter_by(user_id=random_user.user_id, avatar_id=avatar.avatar_id).first()
            if not existing:
                user_avatar = UserAvatar(user_id=random_user.user_id, avatar_id=avatar.avatar_id)
                db.session.add(user_avatar)
        
        # Thêm skin ngẫu nhiên cho một số người dùng
        for user_data in sample_users[:5]:  # Chỉ cho 5 người dùng đầu tiên
            user = User.query.get(user_data["user_id"])
            
            # Thêm skin ngẫu nhiên
            all_skins = Skin.query.all()
            for skin in all_skins:
                # Kiểm tra xem người dùng đã có skin này chưa
                existing = UserSkin.query.filter_by(user_id=user.user_id, skin_id=skin.skin_id).first()
                if not existing:
                    user_skin = UserSkin(user_id=user.user_id, skin_id=skin.skin_id)
                    db.session.add(user_skin)
        
        # Lưu tất cả thay đổi
        db.session.commit()
        print("Đã tạo dữ liệu mẫu thành công!")

if __name__ == "__main__":
    seed_database() 