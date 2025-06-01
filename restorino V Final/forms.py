from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired, MultipleFileField
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FloatField, TimeField, BooleanField, EmailField, IntegerField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional
from config import Config
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    user_type = SelectField('I am a', choices=[('tourist', 'Tourist'), ('owner', 'Restaurant Owner')])
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one or login.')

class TouristProfileForm(FlaskForm):
    country = SelectField('Country', choices=[(country, country) for country in Config.COUNTRIES], validators=[DataRequired()])
    submit = SubmitField('Complete Registration')

class RestaurantOwnerProfileForm(FlaskForm):
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=8, max=20)])
    submit = SubmitField('Complete Registration')

class RestaurantForm(FlaskForm):
    name = StringField('Restaurant Name', validators=[DataRequired(), Length(min=2, max=100)])
    type = StringField('Restaurant Type', validators=[DataRequired(), Length(min=2, max=50)])
    location = StringField('Location in Agadir', validators=[DataRequired(), Length(min=2, max=100)])
    location_id = SelectField('District', coerce=int, validators=[Optional()])
    address = StringField('Full Address', validators=[Optional(), Length(max=255)])
    latitude = FloatField('Latitude', validators=[Optional()])
    longitude = FloatField('Longitude', validators=[Optional()])
    google_maps_link = StringField('Google Maps Link', validators=[Optional(), Length(max=500)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=2000)])
    price_range = SelectField('Price Range', choices=[
        ('$', 'Budget ($)'),
        ('$$', 'Moderate ($$)'),
        ('$$$', 'Expensive ($$$)'),
        ('$$$$', 'Very Expensive ($$$$)')
    ], validators=[DataRequired()])
    instagram = StringField('Instagram', validators=[Optional(), Length(max=100)])
    facebook = StringField('Facebook', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Add Restaurant')
    
    def __init__(self, *args, **kwargs):
        super(RestaurantForm, self).__init__(*args, **kwargs)
        # Populate the location_id choices from the database
        from models import AgadirLocation
        from app import db
        self.location_id.choices = [(0, 'Select a district')] + [
            (location.id, location.name) for location in 
            AgadirLocation.query.order_by(AgadirLocation.name).all()
        ]

class MenuItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Length(max=1000)])
    price = FloatField('Price (MAD)', validators=[DataRequired(), NumberRange(min=0)])
    photo = FileField('Dish Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    ingredients = TextAreaField('Ingredients', validators=[Length(max=500)])
    preparation_time = StringField('Preparation Time (e.g., 15-20 min)', validators=[Length(max=20)])
    is_vegetarian = BooleanField('Vegetarian')
    is_vegan = BooleanField('Vegan')
    is_gluten_free = BooleanField('Gluten Free')
    spice_level = SelectField('Spice Level', choices=[
        ('0', 'Not Spicy'), 
        ('1', 'Mild'), 
        ('2', 'Medium'), 
        ('3', 'Hot'), 
        ('4', 'Very Hot')
    ])
    submit = SubmitField('Add Menu Item')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(str(i), f'{i} Stars') for i in range(1, 6)], validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[Length(max=500)])
    images = MultipleFileField('Upload Images (Optional)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Submit Review')

class PhotoUploadForm(FlaskForm):
    photo = FileField('Restaurant Photo', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    caption = StringField('Caption', validators=[Length(max=255)])
    submit = SubmitField('Upload Photo')

class SearchForm(FlaskForm):
    query = StringField('Search Restaurants', validators=[Length(max=100)])
    cuisine = SelectField('Cuisine Type', choices=[('', 'All Cuisines')] + [(cuisine, cuisine) for cuisine in Config.CUISINE_TYPES])
    location = SelectField('Location', choices=[('', 'All Locations')] + [(location, location) for location in Config.AGADIR_LOCATIONS])
    rating = SelectField('Minimum Rating', choices=[('', 'Any Rating')] + [(str(i), f'{i}+ Stars') for i in range(1, 6)])
    submit = SubmitField('Search')

class MenuItemReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(str(i), f'{i} Stars') for i in range(1, 6)], validators=[DataRequired()])
    comment = TextAreaField('Your Review', validators=[Length(max=500)])
    images = MultipleFileField('Upload Images (Optional)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Submit Review')


class ProfileSettingsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    profile_image = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    current_password = PasswordField('Current Password', validators=[Length(min=6, max=60)])
    new_password = PasswordField('New Password (Optional)', validators=[Optional(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password')])
    submit = SubmitField('Save Changes')


# Custom widget for multi-select checkboxes
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


# New Forms for Game-Changing Features

class LocalGuideForm(FlaskForm):
    neighborhood_expert = SelectField('Area of Expertise', 
                                    choices=[(location, location) for location in Config.AGADIR_LOCATIONS], 
                                    validators=[DataRequired()])
    specialties = MultiCheckboxField('Specialties', 
                                   choices=[(specialty, specialty) for specialty in Config.GUIDE_SPECIALTIES],
                                   validators=[DataRequired()])
    bio = TextAreaField('Tell us about yourself and your knowledge of Agadir', 
                       validators=[DataRequired(), Length(min=50, max=500)])
    contact_number = StringField('Contact Number for Tourists', validators=[DataRequired(), Length(min=8, max=20)])
    languages = MultiCheckboxField('Languages You Speak', 
                                 choices=Config.LANGUAGES,
                                 validators=[DataRequired()])
    submit = SubmitField('Apply to Become a Local Guide')


class TranslationForm(FlaskForm):
    language = SelectField('Language', choices=Config.LANGUAGES, validators=[DataRequired()])
    original_text = TextAreaField('Original Text', render_kw={'readonly': True})
    translated_text = TextAreaField('Translation', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Submit Translation')


class TouristHelpForm(FlaskForm):
    request_type = SelectField('What do you need help with?', 
                             choices=Config.HELP_REQUEST_TYPES, 
                             validators=[DataRequired()])
    request_details = TextAreaField('Please provide details about your request', 
                                  validators=[DataRequired(), Length(min=10, max=500)])
    location = SelectField('Your current location in Agadir', 
                         choices=[(location, location) for location in Config.AGADIR_LOCATIONS], 
                         validators=[DataRequired()])
    preferred_language = SelectField('Preferred language for response', 
                                   choices=Config.LANGUAGES, 
                                   validators=[DataRequired()])
    submit = SubmitField('Request Help')


class FoodChallengeForm(FlaskForm):
    name = StringField('Challenge Name', validators=[DataRequired(), Length(min=5, max=100)])
    description = TextAreaField('Challenge Description', validators=[DataRequired(), Length(min=20, max=500)])
    difficulty_level = SelectField('Difficulty Level', 
                                 choices=Config.CHALLENGE_DIFFICULTY, 
                                 coerce=int,
                                 validators=[DataRequired()])
    badge_reward = StringField('Badge Name', validators=[DataRequired(), Length(min=3, max=100)])
    challenge_image = FileField('Challenge Badge Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Create Food Challenge')


class JoinChallengeForm(FlaskForm):
    submit = SubmitField('Join This Challenge')


class ChallengeProgressForm(FlaskForm):
    progress_update = IntegerField('Update Progress (%)', 
                                 validators=[DataRequired(), NumberRange(min=0, max=100)])
    proof_image = FileField('Upload Photo Proof', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    comments = TextAreaField('Your Experience', validators=[Length(max=500)])
    share_socially = BooleanField('Share on Social Media')
    submit = SubmitField('Update Progress')


# LocalImpactForm removed
