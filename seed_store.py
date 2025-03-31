from app import create_app, db
from models import Avatar, Skin
import random

def seed_avatars_and_skins():
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
    
    app = create_app()
    with app.app_context():
        print("Bắt đầu thêm dữ liệu giả cho avatar và skin...")
        
        # Thêm avatar
        for avatar_data in sample_avatars:
            # Kiểm tra xem avatar đã tồn tại chưa
            existing_avatar = Avatar.query.filter_by(image_url=avatar_data["image_url"]).first()
            
            if not existing_avatar:
                avatar = Avatar(**avatar_data)
                db.session.add(avatar)
                print(f"Đã thêm avatar: {avatar_data['name']}")
            else:
                print(f"Avatar đã tồn tại: {avatar_data['name']}")
        
        # Thêm skin
        for skin_data in sample_skins:
            # Kiểm tra xem skin đã tồn tại chưa
            existing_skin = Skin.query.filter_by(image_url=skin_data["image_url"]).first()
            
            if not existing_skin:
                skin = Skin(**skin_data)
                db.session.add(skin)
                print(f"Đã thêm skin: {skin_data['name']}")
            else:
                print(f"Skin đã tồn tại: {skin_data['name']}")
        
        db.session.commit()
        print("Đã thêm dữ liệu giả cho avatar và skin thành công!")

if __name__ == "__main__":
    seed_avatars_and_skins() 