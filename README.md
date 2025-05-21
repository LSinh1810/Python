# Caro Game Online

Game cờ caro trực tuyến được xây dựng bằng Python Flask và SocketIO.

## Cấu trúc dự án

- `app.py`: Tệp chính khởi động ứng dụng
- `models.py`: Định nghĩa các model cho cơ sở dữ liệu
- `extensions.py`: Cấu hình các extension
- `routes/`: Thư mục chứa các blueprint
- `static/`: Thư mục chứa các tệp tĩnh (CSS, JS, hình ảnh)
- `templates/`: Thư mục chứa các template HTML
- `ai_player.py`: Mã nguồn cho AI chơi caro

## Cài đặt

1. Tạo môi trường ảo và kích hoạt:
```
pip install flask flask-socketio pymysql flask-sqlalchemy
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Cài đặt các gói phụ thuộc:
```
pip install flask flask-socketio pymysql flask-sqlalchemy
```

3. Tạo cơ sở dữ liệu MySQL với tên `CaroPython`

4. Khởi động ứng dụng:
```
python app.py
```

## Tạo dữ liệu mẫu

Để tạo dữ liệu mẫu cho leaderboard, avatar và skin, chạy lệnh sau:

```
python seed_all.py
```

Hoặc có thể chạy từng tệp riêng:

```
python seed_store.py     # Tạo dữ liệu cho avatar và skin
python seed_leaderboard.py  # Tạo dữ liệu cho bảng xếp hạng
```

## Chức năng

- Đăng nhập bằng tên hiển thị
- Chơi với AI (robot)
- Chơi với người chơi khác (qua mã phòng hoặc QR code)
- Bảng xếp hạng
- Avatar và skin tùy chỉnh 