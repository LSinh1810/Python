from app import create_app, db
from models import User, Avatar, Skin, Leaderboard, UserAvatar, UserSkin
import random

# Danh sách avatar mẫu (sử dụng hình ảnh có sẵn)
sample_avatars = [
    {"name": "Avatar 1", "image_url": "/static/images/avatar3.png", "price": 1000},
    {"name": "Avatar 2", "image_url": "/static/images/avatar1.png", "price": 100},
    {"name": "Avatar 3", "image_url": "/static/images/avatar2.png", "price": 200}
]

# Danh sách skin mẫu (sử dụng icon có sẵn)
sample_skins = [
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
            
            # Gán avatar mặc định
            default_avatar = Avatar.query.filter_by(price=0).first()
            if default_avatar:
                user.avatar = default_avatar.image_url
                
            db.session.add(user)
            db.session.commit()  # Lưu để có được user_id
            
            # Tạo bản ghi leaderboard
            wins = random.randint(0, 50)  # Số trận thắng ngẫu nhiên
            leaderboard = Leaderboard(user_id=user.user_id, wins=wins)
            db.session.add(leaderboard)
            
            # Gán avatar cho người dùng
            user_avatar = UserAvatar(user_id=user.user_id, avatar_id=default_avatar.avatar_id)
            db.session.add(user_avatar)
            
            # Gán skin mặc định cho người dùng
            default_skin = Skin.query.filter_by(price=0).first()
            if default_skin:
                user_skin = UserSkin(user_id=user.user_id, skin_id=default_skin.skin_id)
                db.session.add(user_skin)
        
        # Thêm một số avatar và skin ngẫu nhiên cho người dùng
        for user_data in sample_users[:5]:  # Chỉ cho 5 người dùng đầu tiên
            user = User.query.get(user_data["user_id"])
            
            # Thêm avatar ngẫu nhiên
            random_avatars = Avatar.query.filter(Avatar.price > 0).limit(2).all()
            for avatar in random_avatars:
                user_avatar = UserAvatar(user_id=user.user_id, avatar_id=avatar.avatar_id)
                db.session.add(user_avatar)
            
            # Thêm skin ngẫu nhiên
            random_skins = Skin.query.filter(Skin.price > 0).limit(2).all()
            for skin in random_skins:
                user_skin = UserSkin(user_id=user.user_id, skin_id=skin.skin_id)
                db.session.add(user_skin)
        
        # Lưu tất cả thay đổi
        db.session.commit()
        print("Đã tạo dữ liệu mẫu thành công!")

if __name__ == "__main__":
    seed_database() 