from datetime import datetime
from extensions import db

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(10), primary_key=True)
    displayName = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)

class Game(db.Model):
    __tablename__ = 'games'
    game_id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(10), unique=True, nullable=False)
    player1_id = db.Column(db.String(10))
    player2_id = db.Column(db.String(10))
    winner_id = db.Column(db.String(10), nullable=True)
    status = db.Column(db.String(20), default='ongoing')  # 'ongoing', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Move(db.Model):
    move_id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'))
    player_id = db.Column(db.String(10), db.ForeignKey('users.user_id'))
    position = db.Column(db.String(10), nullable=False)
    move_order = db.Column(db.Integer, default=0)
    position_x = db.Column(db.Integer, nullable=True)
    position_y = db.Column(db.Integer, nullable=True)

class Leaderboard(db.Model):
    rank_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(10), db.ForeignKey('users.user_id'))
    wins = db.Column(db.Integer, default=0)

class Avatar(db.Model):
    avatar_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, default=0)

class UserAvatar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(10), db.ForeignKey('users.user_id'))
    avatar_id = db.Column(db.Integer, db.ForeignKey('avatar.avatar_id'))

class Skin(db.Model):
    skin_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, default=0)

class UserSkin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(10), db.ForeignKey('users.user_id'))
    skin_id = db.Column(db.Integer, db.ForeignKey('skin.skin_id'))

class ReplayRequest(db.Model):
    request_id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'))
    player_id = db.Column(db.String(10), db.ForeignKey('users.user_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
