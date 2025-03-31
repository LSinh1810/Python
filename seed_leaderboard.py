from app import create_app, db
from models import User, Leaderboard
import random

# Tên người chơi mẫu tiếng Việt
vietnamese_names = [
    "Nguyễn Văn An", "Trần Thị Bình", "Lê Văn Cường", "Phạm Thị Dung", 
    "Hoàng Văn Em", "Ngô Thị Phương", "Vũ Văn Giàu", "Đặng Thị Hồng",
    "Bùi Văn Inox", "Lý Thị Khánh", "Hồ Văn Lộc", "Mai Thị Minh",
    "Đỗ Văn Năm", "Huỳnh Thị Oanh", "Phan Văn Phúc", "Trương Thị Quỳnh",
    "Dương Văn Rồng", "Võ Thị Sen", "Đinh Văn Tâm", "Nguyễn Thị Uyên"
]

def seed_leaderboard():
    app = create_app()
    with app.app_context():
        print("Bắt đầu thêm dữ liệu giả vào bảng xếp hạng...")
        
        # Xóa dữ liệu cũ nếu có
        db.session.query(Leaderboard).delete()
        db.session.commit()
        
        # Tạo người dùng và thêm vào bảng xếp hạng
        for i, name in enumerate(vietnamese_names):
            # Tạo ID người dùng
            user_id = f"user{i+1}"
            
            # Kiểm tra xem người dùng đã tồn tại chưa
            existing_user = User.query.filter_by(user_id=user_id).first()
            
            if not existing_user:
                # Tạo người dùng mới
                user = User(
                    user_id=user_id,
                    displayName=name,
                    avatar=f"/static/images/{'default_avatar.png' if i % 3 == 0 else 'avatar' + str((i % 2) + 1) + '.png'}"
                )
                db.session.add(user)
                db.session.commit()
                print(f"Đã tạo người dùng: {name}")
            else:
                print(f"Người dùng {name} đã tồn tại")
                user = existing_user
            
            # Kiểm tra xem đã có bản ghi leaderboard chưa
            existing_leaderboard = Leaderboard.query.filter_by(user_id=user_id).first()
            
            if not existing_leaderboard:
                # Tạo bản ghi leaderboard mới với số lượt thắng ngẫu nhiên
                wins = random.randint(5, 100)
                leaderboard = Leaderboard(user_id=user_id, wins=wins)
                db.session.add(leaderboard)
                print(f"Đã thêm {name} vào bảng xếp hạng với {wins} chiến thắng")
            else:
                # Cập nhật số lượt thắng ngẫu nhiên
                existing_leaderboard.wins = random.randint(5, 100)
                print(f"Đã cập nhật số chiến thắng cho {name}")
        
        db.session.commit()
        print("Đã thêm dữ liệu giả vào bảng xếp hạng thành công!")

if __name__ == "__main__":
    seed_leaderboard() 