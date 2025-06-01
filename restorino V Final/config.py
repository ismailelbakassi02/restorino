import os
from datetime import timedelta

class Config:
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'agadir-restorino-secret-key'
    
    # SQLite database
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(BASE_DIR, "instance", "database.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Cuisine types available in Agadir
    CUISINE_TYPES = [
        'Moroccan Traditional',
        'Seafood',
        'Mediterranean',
        'International',
        'Fast Food',
        'Café/Tea House',
        'Berber Cuisine'
    ]
    
    # Google Maps API Key
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY') or 'AIzaSyC9PlJYavX2e-7EwvAIeXCQVRNHHnCFLXM'
    
    # Agadir locations
    AGADIR_LOCATIONS = [
        'Agadir Marina',
        'Souk El Had',
        'Agadir Beach',
        'Founty Beach',
        'Cite Suisse',
        'Talborjt',
        'Secteur Touristique'
    ]
    
    # Countries for tourist registration
    COUNTRIES = [
        'Morocco', 'France', 'Spain', 'Germany', 'United Kingdom', 
        'United States', 'Canada', 'Italy', 'Belgium', 'Netherlands',
        'Russia', 'China', 'Japan', 'Australia', 'Other'
    ]
    
    # Languages for translations
    LANGUAGES = [
        ('ar', 'Arabic'),
        ('fr', 'French'),
        ('en', 'English'),
        ('es', 'Spanish'),
        ('de', 'German')
    ]
    
    # Local guide specialties
    GUIDE_SPECIALTIES = [
        'Seafood',
        'Traditional Moroccan',
        'Budget-Friendly',
        'Family-Friendly',
        'Vegetarian/Vegan',
        'Street Food',
        'Luxury Dining',
        'Cultural Experiences'
    ]
    
    # Tourist help request types
    HELP_REQUEST_TYPES = [
        ('translation', 'Translation Help'),
        ('recommendation', 'Restaurant Recommendation'),
        ('directions', 'Directions to Restaurant'),
        ('menu', 'Menu Explanation'),
        ('cultural', 'Cultural Information')
    ]
    
    # Food challenge difficulty levels
    CHALLENGE_DIFFICULTY = [
        (1, 'Easy - Perfect for Beginners'),
        (2, 'Casual - Some Experience Needed'),
        (3, 'Moderate - For Food Enthusiasts'),
        (4, 'Hard - For Adventurous Eaters'),
        (5, 'Expert - For Culinary Daredevils')
    ]
    
    # Sample food challenges
    SAMPLE_CHALLENGES = [
        {
            'name': 'Tagine Tour',
            'description': 'Try 5 different authentic Moroccan tagines from different restaurants in Agadir.',
            'difficulty_level': 2,
            'badge_reward': 'Tagine Master'
        },
        {
            'name': 'Seafood Safari',
            'description': 'Sample the freshest catches from the Atlantic at 3 different seafood spots along Agadir Beach.',
            'difficulty_level': 1,
            'badge_reward': 'Ocean Explorer'
        },
        {
            'name': 'Spice Seeker',
            'description': 'Brave the heat! Try 5 increasingly spicy Moroccan dishes and document your journey.',
            'difficulty_level': 4,
            'badge_reward': 'Fire Breather'
        },
        {
            'name': 'Tea Time Trek',
            'description': 'Visit 7 traditional tea houses and try different variations of Moroccan mint tea.',
            'difficulty_level': 3,
            'badge_reward': 'Tea Connoisseur'
        },
        {
            'name': 'Argan Oil Adventure',
            'description': 'Try 5 different dishes featuring Argan oil, a Moroccan specialty from the region.',
            'difficulty_level': 2,
            'badge_reward': 'Argan Ambassador'
        }
    ]
