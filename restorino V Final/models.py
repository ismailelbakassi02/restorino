from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'tourist', 'restaurant_owner', 'admin'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_image = db.Column(db.String(255), nullable=True)  # Path to profile image
    bio = db.Column(db.Text, nullable=True)  # Short bio or description
    
    # Relationships
    tourist = db.relationship('Tourist', backref='user', uselist=False, cascade='all, delete-orphan')
    restaurant_owner = db.relationship('RestaurantOwner', backref='user', uselist=False, cascade='all, delete-orphan')
    photos = db.relationship('Photo', backref='uploader', foreign_keys='Photo.uploaded_by')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class Tourist(db.Model):
    __tablename__ = 'tourists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    instagram = db.Column(db.String(100), nullable=True)
    twitter = db.Column(db.String(100), nullable=True)
    facebook = db.Column(db.String(100), nullable=True)
    tiktok = db.Column(db.String(100), nullable=True)
    
    # Relationships
    reviews = db.relationship('Review', backref='tourist', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Tourist {self.user.name} from {self.country}>'


class RestaurantOwner(db.Model):
    __tablename__ = 'restaurant_owners'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_super_user = db.Column(db.Boolean, default=False)
    
    # Relationships
    restaurants = db.relationship('Restaurant', backref='owner', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<RestaurantOwner {self.user.name}>'


class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # cuisine type
    location = db.Column(db.String(100), nullable=False)  # Agadir district name
    location_id = db.Column(db.Integer, db.ForeignKey('agadir_locations.id'), nullable=True)  # Reference to AgadirLocation
    address = db.Column(db.String(255), nullable=True)  # Full address
    latitude = db.Column(db.Float, nullable=True)  # For map location
    longitude = db.Column(db.Float, nullable=True)  # For map location
    google_maps_link = db.Column(db.String(500), nullable=True)  # Direct link to Google Maps
    open_time = db.Column(db.String(10), nullable=False)
    close_time = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text, nullable=True)
    contact_number = db.Column(db.String(20), nullable=False)
    whatsapp_number = db.Column(db.String(20), nullable=True)
    average_rating = db.Column(db.Float, default=0.0)
    owner_id = db.Column(db.Integer, db.ForeignKey('restaurant_owners.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    price_range = db.Column(db.String(10), nullable=True)  # $, $$, $$$, $$$$
    website = db.Column(db.String(255), nullable=True)
    instagram = db.Column(db.String(100), nullable=True)
    facebook = db.Column(db.String(100), nullable=True)
    vibe_inside = db.Column(db.String(255), nullable=True)  # Comma-separated tags
    vibe_outside = db.Column(db.String(255), nullable=True)  # Comma-separated tags
    is_claimed = db.Column(db.Boolean, default=False)
    features = db.Column(db.String(500), nullable=True)  # Comma-separated features (e.g., 'Outdoor seating, Dogs allowed')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    
    # Relationships
    menu_items = db.relationship('MenuItem', backref='restaurant', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='restaurant', cascade='all, delete-orphan')
    photos = db.relationship('Photo', backref='restaurant', cascade='all, delete-orphan')
    
    def update_average_rating(self):
        """Calculate and update the average rating based on all reviews"""
        reviews = Review.query.filter_by(restaurant_id=self.id).all()
        if reviews:
            total = sum(review.rating for review in reviews)
            self.average_rating = round(total / len(reviews), 1)
        else:
            self.average_rating = 0.0
        db.session.commit()
    
    def __repr__(self):
        return f'<Restaurant {self.name}>'


class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)  # Path to dish photo
    ingredients = db.Column(db.Text, nullable=True)  # List of ingredients
    preparation_time = db.Column(db.String(20), nullable=True)  # Estimated preparation time
    is_vegetarian = db.Column(db.Boolean, default=False)
    is_vegan = db.Column(db.Boolean, default=False)
    is_gluten_free = db.Column(db.Boolean, default=False)
    spice_level = db.Column(db.Integer, default=0)  # 0-4 scale
    average_rating = db.Column(db.Float, default=0.0)  # Average rating based on reviews
    
    # Relationships
    reviews = db.relationship('MenuItemReview', backref='menu_item', cascade='all, delete-orphan')
    
    def update_average_rating(self):
        """Update the average rating based on all reviews"""
        reviews = MenuItemReview.query.filter_by(menu_item_id=self.id).all()
        if not reviews:
            self.average_rating = 0.0
            db.session.commit()
            return
            
        total_rating = sum(review.rating for review in reviews)
        self.average_rating = round(total_rating / len(reviews), 1)
        db.session.commit()
    
    def __repr__(self):
        return f'<MenuItem {self.name} - {self.price} MAD>'


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    tourist_id = db.Column(db.Integer, db.ForeignKey('tourists.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    images = db.relationship('ReviewImage', backref='review', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Review {self.rating} stars>'


class Photo(db.Model):
    __tablename__ = 'photos'
    
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255), nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Photo {self.image_url}>'


class ReviewImage(db.Model):
    __tablename__ = 'review_images'
    
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255), nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ReviewImage {self.image_url}>'


class MenuItemReviewImage(db.Model):
    __tablename__ = 'menu_item_review_images'
    
    id = db.Column(db.Integer, primary_key=True)
    menu_item_review_id = db.Column(db.Integer, db.ForeignKey('menu_item_reviews.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255), nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MenuItemReviewImage {self.image_url}>'


# MenuItemReview class is defined later in the file


# New Game-Changing Models

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    restaurants = db.relationship('Restaurant', backref='category')
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Translation(db.Model):
    __tablename__ = 'translations'
    
    id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(db.String(20), nullable=False)  # 'menu', 'description', 'review'
    content_id = db.Column(db.Integer, nullable=False)  # Foreign Key to the content being translated
    language = db.Column(db.String(2), nullable=False)  # 'ar', 'fr', 'en', 'es', 'de'
    translated_text = db.Column(db.Text, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)  # Verified by native speakers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Translation {self.language}: {self.content_type} {self.content_id}>'


class LocalGuide(db.Model):
    __tablename__ = 'local_guides'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    neighborhood_expert = db.Column(db.String(100), nullable=False)  # Agadir area
    verification_badge = db.Column(db.Boolean, default=False)
    guide_points = db.Column(db.Integer, default=0)  # Gamification points
    specialties = db.Column(db.String(255), nullable=True)  # Comma-separated specialties
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='local_guide', uselist=False)
    help_sessions = db.relationship('TouristHelp', backref='guide', foreign_keys='TouristHelp.guide_id')
    
    def __repr__(self):
        return f'<LocalGuide {self.user.name} - {self.neighborhood_expert}>'


class TouristHelp(db.Model):
    __tablename__ = 'tourist_help'
    
    id = db.Column(db.Integer, primary_key=True)
    tourist_id = db.Column(db.Integer, db.ForeignKey('tourists.id'), nullable=False)
    guide_id = db.Column(db.Integer, db.ForeignKey('local_guides.id'), nullable=False)
    request_type = db.Column(db.String(20), nullable=False)  # 'translation', 'recommendation', 'directions'
    status = db.Column(db.String(10), nullable=False, default='pending')  # 'pending', 'active', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    request_details = db.Column(db.Text, nullable=True)
    response = db.Column(db.Text, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    tourist = db.relationship('Tourist', backref='help_requests')
    
    def __repr__(self):
        return f'<TouristHelp {self.request_type} - {self.status}>'


class FoodChallenge(db.Model):
    __tablename__ = 'food_challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # "Try 5 Tagines Challenge", "Argan Oil Adventure"
    description = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.Integer, nullable=False)  # 1-5
    badge_reward = db.Column(db.String(100), nullable=False)
    completion_count = db.Column(db.Integer, default=0)
    social_share_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    image_url = db.Column(db.String(255), nullable=True)  # Challenge badge image
    
    # Relationships
    participants = db.relationship('ChallengeParticipant', backref='challenge', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<FoodChallenge {self.name} - Level {self.difficulty_level}>'


class ChallengeParticipant(db.Model):
    __tablename__ = 'challenge_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('food_challenges.id'), nullable=False)
    tourist_id = db.Column(db.Integer, db.ForeignKey('tourists.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)  # Progress percentage
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    shared_socially = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comment = db.Column(db.Text, nullable=True)
    social_post_url = db.Column(db.String(255), nullable=True)
    
    # Relationships
    tourist = db.relationship('Tourist', backref='challenges')
    posts = db.relationship('ChallengePost', backref='participant', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ChallengeParticipant {self.tourist.user.name} - {self.challenge.name} - {self.progress}%>'


class ChallengePost(db.Model):
    __tablename__ = 'challenge_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('challenge_participants.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes_count = db.Column(db.Integer, default=0)
    
    # Relationships
    comments = db.relationship('ChallengeComment', backref='post', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ChallengePost {self.id} - {self.participant.tourist.user.name}>'


class ChallengeComment(db.Model):
    __tablename__ = 'challenge_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('challenge_posts.id'), nullable=False)
    tourist_id = db.Column(db.Integer, db.ForeignKey('tourists.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tourist = db.relationship('Tourist', backref='comments')
    
    def __repr__(self):
        return f'<ChallengeComment {self.id} - {self.tourist.user.name}>'


# LocalImpact model removed


class AgadirLocation(db.Model):
    __tablename__ = 'agadir_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    restaurants = db.relationship('Restaurant', backref='district', lazy='dynamic')
    
    def __repr__(self):
        return f'<AgadirLocation {self.name}>'


class MenuItemReview(db.Model):
    __tablename__ = 'menu_item_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    tourist_id = db.Column(db.Integer, db.ForeignKey('tourists.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tourist = db.relationship('Tourist', backref='menu_item_reviews')
    images = db.relationship('MenuItemReviewImage', backref='review', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<MenuItemReview {self.rating} stars>'
