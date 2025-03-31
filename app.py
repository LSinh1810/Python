import random
import string
from flask import Flask
from extensions import db, socketio
import pymysql

pymysql.install_as_MySQLdb()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'caro_game_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/CaroPython'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app)
    
    # Add Jinja2 functions
    app.jinja_env.globals.update(enumerate=enumerate)

    # Import and register blueprints
    from routes.home import home_bp
    from routes.qr_code import qr_code_bp
    from routes.after_game import after_game_bp
    from routes.leaderboard import leaderboard_bp
    from routes.store import store_bp
    from routes.pvp_noti import pvp_noti_bp
    from routes.pve_noti import pve_noti_bp
    from routes.pvp import pvp_bp
    from routes.pve import pve_bp
    from routes.profile import profile_bp
    app.register_blueprint(home_bp)
    app.register_blueprint(qr_code_bp)
    app.register_blueprint(after_game_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(pvp_noti_bp)
    app.register_blueprint(pve_noti_bp)
    app.register_blueprint(pvp_bp)
    app.register_blueprint(pve_bp)
    app.register_blueprint(profile_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()  # Chỉ tạo bảng Game
    socketio.run(app, debug=True)