from flask import Blueprint, render_template, request
from models import User, Leaderboard, Game
from app import db
from sqlalchemy import desc

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/leaderboard')
def index():
    # Lấy danh sách người chơi xếp hạng theo số trận thắng
    leaderboard_data = db.session.query(
        User, Leaderboard
    ).join(
        Leaderboard, User.user_id == Leaderboard.user_id
    ).order_by(
        desc(Leaderboard.wins)
    ).limit(10).all()
    
    # Kiểm tra cookie người dùng
    user_id = request.cookies.get('user_id')
    user = User.query.get(user_id) if user_id else None
    
    # Lấy thứ hạng của người dùng đang đăng nhập (nếu có)
    user_rank = None
    if user:
        user_leaderboard = Leaderboard.query.filter_by(user_id=user_id).first()
        if user_leaderboard:
            # Đếm số người chơi có nhiều chiến thắng hơn
            higher_players = Leaderboard.query.filter(
                Leaderboard.wins > user_leaderboard.wins
            ).count()
            user_rank = higher_players + 1
    
    # Lấy tổng số game đã chơi
    total_games = Game.query.filter(Game.status == 'completed').count()
    
    return render_template(
        'leaderboard.htm', 
        leaderboard_data=leaderboard_data,
        user=user, 
        user_rank=user_rank,
        total_games=total_games
    ) 