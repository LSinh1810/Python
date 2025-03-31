from seed_leaderboard import seed_leaderboard
from seed_store import seed_avatars_and_skins

if __name__ == "__main__":
    print("Bắt đầu tạo dữ liệu giả cho cơ sở dữ liệu...")
    
    # Seed avatars và skins trước
    seed_avatars_and_skins()
    
    # Seed leaderboard sau
    seed_leaderboard()
    
    print("Đã hoàn thành tạo dữ liệu giả!") 