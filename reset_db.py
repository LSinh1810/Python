from app import create_app, db

def reset_database():
    app = create_app()
    with app.app_context():
        print("Đang xóa và tạo lại tất cả các bảng...")
        db.drop_all()  # Xóa tất cả các bảng hiện có
        db.create_all()  # Tạo lại tất cả các bảng theo định nghĩa model
        print("Đã tạo lại cơ sở dữ liệu thành công!")

if __name__ == "__main__":
    reset_database() 