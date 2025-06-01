import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from models import db, User, FoodChallenge, LocalGuide, Translation, TouristHelp
from routes import main
from config import Config

def create_app(config_class=Config):
    # Create and configure the app
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize CSRF protection
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(main)
    
    # Make config available to all templates
    @app.context_processor
    def inject_config():
        return dict(config=app.config)
    
    # Create database tables
    with app.app_context():
        # Create uploads directory if it doesn't exist
        os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)
        
        # Create database tables
        db.create_all()
        
        # Create a super user if none exists
        from models import RestaurantOwner
        super_user = RestaurantOwner.query.filter_by(is_super_user=True).first()
        if not super_user:
            from werkzeug.security import generate_password_hash
            admin = User.query.filter_by(email='admin@restorino.com').first()
            if not admin:
                admin = User(
                    name='Admin',
                    email='admin@restorino.com',
                    password_hash=generate_password_hash('admin123'),
                    user_type='owner',
                    is_active=True
                )
                db.session.add(admin)
                db.session.commit()
                
                admin_owner = RestaurantOwner(
                    user_id=admin.id,
                    contact_number='123456789',
                    is_verified=True,
                    is_super_user=True
                )
                db.session.add(admin_owner)
                db.session.commit()
                print('Admin user created: admin@restorino.com / admin123')
        
        # Create sample food challenges if none exist
        if FoodChallenge.query.count() == 0:
            for challenge_data in Config.SAMPLE_CHALLENGES:
                challenge = FoodChallenge(
                    name=challenge_data['name'],
                    description=challenge_data['description'],
                    difficulty_level=challenge_data['difficulty_level'],
                    badge_reward=challenge_data['badge_reward'],
                    completion_count=0,
                    social_share_count=0
                )
                db.session.add(challenge)
            db.session.commit()
            print('Sample food challenges created')
        
        # Create uploads directories for challenges and other features
        os.makedirs(os.path.join(app.static_folder, 'uploads', 'challenges'), exist_ok=True)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
