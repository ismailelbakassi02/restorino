import os
import secrets
import json
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import (db, User, Tourist, RestaurantOwner, LocalGuide, Restaurant,
                   MenuItem, Review, MenuItemReview, FoodChallenge, Translation,
                   AgadirLocation, TouristHelp, Photo, ReviewImage, MenuItemReviewImage,
                   ChallengeParticipant, ChallengePost, ChallengeComment)
from forms import (LoginForm, RegistrationForm, TouristProfileForm, RestaurantOwnerProfileForm,
                  RestaurantForm, MenuItemForm, ReviewForm, PhotoUploadForm, SearchForm, 
                  MenuItemReviewForm, ProfileSettingsForm, LocalGuideForm, TranslationForm, TouristHelpForm,
                  FoodChallengeForm, JoinChallengeForm, ChallengeProgressForm)
from utils import save_picture, save_profile_picture, save_multiple_pictures

# Create blueprint
main = Blueprint('main', __name__)

# Routes for the application

# Helper function to delete image file
def delete_image_file(image_path):
    """Delete an image file from the filesystem"""
    if not image_path:
        return False
    
    # Get the full path to the image
    full_path = os.path.join(current_app.root_path, 'static', image_path)
    
    # Check if the file exists
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    return False

# Routes
@main.route('/')
def index():
    """Homepage with featured restaurants"""
    # Get top-rated restaurants
    top_restaurants = Restaurant.query.order_by(Restaurant.average_rating.desc()).limit(6).all()
    
    # Get newest restaurants
    new_restaurants = Restaurant.query.order_by(Restaurant.created_at.desc()).limit(6).all()


# First add_restaurant route removed to fix duplicate route issue
    search_form = SearchForm()
    
    return render_template('index.html', 
                          top_restaurants=top_restaurants,
                          new_restaurants=new_restaurants,
                          search_form=search_form,
                          cuisine_types=current_app.config['CUISINE_TYPES'],
                          locations=current_app.config['AGADIR_LOCATIONS'])

@main.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            user_type=form.user_type.data,
            is_active=True
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        # Log in the user
        login_user(user)
        
        # Redirect to complete profile based on user type
        if user.user_type == 'tourist':
            return redirect(url_for('main.complete_tourist_profile'))
        else:
            return redirect(url_for('main.complete_owner_profile'))
    
    return render_template('register.html', form=form)

@main.route('/complete-tourist-profile', methods=['GET', 'POST'])
@login_required
def complete_tourist_profile():
    """Complete tourist profile after registration"""
    if current_user.user_type != 'tourist':
        return redirect(url_for('main.dashboard'))
    
    if Tourist.query.filter_by(user_id=current_user.id).first():
        return redirect(url_for('main.dashboard'))
    
    form = TouristProfileForm()
    if form.validate_on_submit():
        tourist = Tourist(
            user_id=current_user.id,
            country=form.country.data
        )
        db.session.add(tourist)
        db.session.commit()
        flash('Your profile has been completed!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('complete_tourist_profile.html', form=form)

@main.route('/complete-owner-profile', methods=['GET', 'POST'])
@login_required
def complete_owner_profile():
    """Complete restaurant owner profile after registration"""
    if current_user.user_type != 'owner':
        return redirect(url_for('main.dashboard'))
    
    if RestaurantOwner.query.filter_by(user_id=current_user.id).first():
        return redirect(url_for('main.dashboard'))
    
    form = RestaurantOwnerProfileForm()
    if form.validate_on_submit():
        owner = RestaurantOwner(
            user_id=current_user.id,
            contact_number=form.contact_number.data,
            is_verified=False,
            is_super_user=False
        )
        db.session.add(owner)
        db.session.commit()
        flash('Your profile has been completed! Your account will be verified by an admin soon.', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('complete_owner_profile.html', form=form)

@main.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    if current_user.user_type == 'tourist':
        # Get tourist profile
        tourist = Tourist.query.filter_by(user_id=current_user.id).first()
        if not tourist:
            return redirect(url_for('main.complete_tourist_profile'))
        
        # Get reviews by this tourist
        reviews = Review.query.filter_by(tourist_id=tourist.id).order_by(Review.date.desc()).all()
        
        return render_template('dashboard.html', 
                              tourist=tourist, 
                              reviews=reviews)
    else:
        # Get owner profile
        owner = RestaurantOwner.query.filter_by(user_id=current_user.id).first()
        if not owner:
            return redirect(url_for('main.complete_owner_profile'))
        
        # Get restaurants owned by this user
        restaurants = Restaurant.query.filter_by(owner_id=owner.id).all()
        
        return render_template('dashboard.html', 
                              owner=owner, 
                              restaurants=restaurants)

@main.route('/restaurant/<int:id>')
def restaurant_detail(id):
    """Restaurant details page"""
    restaurant = Restaurant.query.get_or_404(id)
    menu_items = MenuItem.query.filter_by(restaurant_id=id).all()
    reviews = Review.query.filter_by(restaurant_id=id).order_by(Review.date.desc()).all()
    photos = Photo.query.filter_by(restaurant_id=id).all()
    
    # Check if current user can review (must be a tourist and not already reviewed)
    can_review = False
    if current_user.is_authenticated and current_user.user_type == 'tourist':
        tourist = Tourist.query.filter_by(user_id=current_user.id).first()
        if tourist:
            existing_review = Review.query.filter_by(restaurant_id=id, tourist_id=tourist.id).first()
            can_review = not existing_review
    
    review_form = ReviewForm() if can_review else None
    
    return render_template('restaurant_detail.html',
                          restaurant=restaurant,
                          menu_items=menu_items,
                          reviews=reviews,
                          photos=photos,
                          review_form=review_form)

@main.route('/add-restaurant', methods=['GET', 'POST'])
@login_required
def add_restaurant():
    """Add a new restaurant (for restaurant owners only)"""
    # Check if user is a restaurant owner
    if current_user.user_type != 'owner':
        flash('Only restaurant owners can add restaurants.', 'warning')
        return redirect(url_for('main.index'))
    
    # Check if owner is verified
    owner = RestaurantOwner.query.filter_by(user_id=current_user.id).first()
    if not owner.is_verified:
        flash('Your account needs to be verified before you can add a restaurant.', 'warning')
        return redirect(url_for('main.index'))
    
    form = RestaurantForm()
    if form.validate_on_submit():
        # Create new restaurant with form data
        restaurant = Restaurant(
            name=form.name.data,
            type=form.type.data,
            location=form.location.data,
            address=form.address.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            google_maps_link=form.google_maps_link.data,
            description=form.description.data,
            price_range=form.price_range.data,
            instagram=form.instagram.data,
            facebook=form.facebook.data,
            owner_id=owner.id,
            # Add default values for required fields that are no longer in the form
            open_time="09:00",
            close_time="22:00",
            contact_number=owner.contact_number,
            is_claimed=True
        )
        
        # Associate with Agadir location if selected
        if form.location_id.data and form.location_id.data > 0:
            restaurant.location_id = form.location_id.data
            # Get the location name for display
            location = AgadirLocation.query.get(form.location_id.data)
            if location:
                restaurant.location = location.name
        
        db.session.add(restaurant)
        db.session.commit()
        
        flash('Restaurant added successfully! It will be reviewed by our team.', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('add_restaurant.html', form=form)

@main.route('/restaurant/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_restaurant(id):
    # Ensure the user is a restaurant owner
    if current_user.user_type != 'restaurant_owner':
        flash('Only restaurant owners can edit restaurants.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get the restaurant
    restaurant = Restaurant.query.get_or_404(id)
    
    # Check if the current user is the owner of this restaurant
    owner = RestaurantOwner.query.filter_by(user_id=current_user.id).first()
    if not owner or restaurant.owner_id != owner.id:
        flash('You can only edit your own restaurants.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Create form and populate it with restaurant data
    form = RestaurantForm()
    
    # Populate the location_id field choices
    form.location_id.choices = [(l.id, l.name) for l in AgadirLocation.query.order_by(AgadirLocation.name).all()]
    form.location_id.choices.insert(0, (0, 'Select a district (optional)'))
    
    if form.validate_on_submit():
        # Update restaurant with form data
        restaurant.name = form.name.data
        restaurant.type = form.type.data
        restaurant.location = form.location.data
        restaurant.address = form.address.data
        restaurant.latitude = form.latitude.data
        restaurant.longitude = form.longitude.data
        restaurant.google_maps_link = form.google_maps_link.data
        restaurant.description = form.description.data
        restaurant.price_range = form.price_range.data
        restaurant.instagram = form.instagram.data
        restaurant.facebook = form.facebook.data
        
        # Associate with Agadir location if selected
        if form.location_id.data and form.location_id.data > 0:
            restaurant.location_id = form.location_id.data
        else:
            restaurant.location_id = None
        
        db.session.commit()
        
        flash('Restaurant updated successfully!', 'success')
        return redirect(url_for('main.restaurant_detail', id=restaurant.id))
    
    # Populate form with existing restaurant data
    if request.method == 'GET':
        form.name.data = restaurant.name
        form.type.data = restaurant.type
        form.location.data = restaurant.location
        form.address.data = restaurant.address
        form.latitude.data = restaurant.latitude
        form.longitude.data = restaurant.longitude
        form.google_maps_link.data = restaurant.google_maps_link
        form.description.data = restaurant.description
        form.price_range.data = restaurant.price_range
        form.instagram.data = restaurant.instagram
        form.facebook.data = restaurant.facebook
        form.location_id.data = restaurant.location_id or 0
    
    return render_template('edit_restaurant.html', form=form, restaurant=restaurant)

@main.route('/restaurant/<int:id>/delete', methods=['POST'])
@login_required
def delete_restaurant(id):
    # Ensure the user is a restaurant owner
    if current_user.user_type != 'restaurant_owner':
        flash('Only restaurant owners can delete restaurants.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get the restaurant
    restaurant = Restaurant.query.get_or_404(id)
    
    # Check if the current user is the owner of this restaurant
    owner = RestaurantOwner.query.filter_by(user_id=current_user.id).first()
    if not owner or restaurant.owner_id != owner.id:
        flash('You can only delete your own restaurants.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Store the name for the flash message
    restaurant_name = restaurant.name
    
    # Delete the restaurant
    db.session.delete(restaurant)
    db.session.commit()
    
    flash(f'Restaurant "{restaurant_name}" has been deleted successfully.', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/restaurant/<int:id>/add-menu-item', methods=['GET', 'POST'])
@login_required
def add_menu_item(id):
    """Add a menu item to a restaurant (owner only)"""
    restaurant = Restaurant.query.get_or_404(id)
    owner = RestaurantOwner.query.filter_by(user_id=current_user.id).first()
    
    # Check if current user is the owner
    if not owner or restaurant.owner_id != owner.id:
        flash('You can only add menu items to your own restaurants.', 'danger')
        return redirect(url_for('main.restaurant_detail', id=id))
    
    form = MenuItemForm()
    if form.validate_on_submit():
        # Create menu item with basic info
        menu_item = MenuItem(
            restaurant_id=id,
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            ingredients=form.ingredients.data,
            preparation_time=form.preparation_time.data,
            is_vegetarian=form.is_vegetarian.data,
            is_vegan=form.is_vegan.data,
            is_gluten_free=form.is_gluten_free.data,
            spice_level=int(form.spice_level.data)
        )
        
        # Handle photo upload if provided
        if form.photo.data:
            photo_filename = save_picture(form.photo.data)
            menu_item.image_url = photo_filename
        
        db.session.add(menu_item)
        db.session.commit()
        flash('Menu item added successfully!', 'success')
        return redirect(url_for('main.menu_item_detail', id=menu_item.id))
    
    return render_template('add_menu_item.html', form=form, restaurant=restaurant)

@main.route('/restaurant/<int:id>/add-photo', methods=['GET', 'POST'])
@login_required
def add_photo(id):
    """Add a photo to a restaurant"""
    restaurant = Restaurant.query.get_or_404(id)
    
    # Check if current user is the owner
    is_owner = False
    if current_user.user_type == 'owner':
        owner = RestaurantOwner.query.filter_by(user_id=current_user.id).first()
        if owner and restaurant.owner_id == owner.id:
            is_owner = True
    
    # Only owners or tourists can add photos
    if not (current_user.user_type == 'tourist' or is_owner):
        flash('You must be a tourist or the restaurant owner to add photos.', 'danger')
        return redirect(url_for('main.restaurant_detail', id=id))
    
    form = PhotoUploadForm()
    if form.validate_on_submit():
        if form.photo.data:
            photo_file = save_picture(form.photo.data, folder='restaurant_photos')
            photo = Photo(
                restaurant_id=id,
                image_url=photo_file,
                caption=form.caption.data,
                uploaded_by=current_user.id
            )
            db.session.add(photo)
            db.session.commit()
            flash('Photo uploaded successfully!', 'success')
            return redirect(url_for('main.restaurant_detail', id=id))
    
    return render_template('add_photo.html', form=form, restaurant=restaurant)

@main.route('/delete/photo/<int:photo_id>', methods=['POST'])
@login_required
def delete_restaurant_photo(photo_id):
    """Delete a restaurant photo"""
    photo = Photo.query.get_or_404(photo_id)
    restaurant = Restaurant.query.get_or_404(photo.restaurant_id)
    
    # Check if the current user is authorized to delete this photo
    is_owner = False
    if current_user.user_type == 'owner':
        owner = RestaurantOwner.query.filter_by(user_id=current_user.id).first()
        if owner and restaurant.owner_id == owner.id:
            is_owner = True
    
    # Only the uploader or the restaurant owner can delete photos
    if photo.uploaded_by == current_user.id or is_owner:
        # Delete the image file
        delete_image_file(photo.image_url)
        
        # Delete the database record
        db.session.delete(photo)
        db.session.commit()
        
        flash('Photo deleted successfully!', 'success')
    else:
        flash('You are not authorized to delete this photo.', 'danger')
    
    return redirect(url_for('main.restaurant_detail', id=restaurant.id))

@main.route('/delete/review-image/<int:image_id>', methods=['POST'])
@login_required
def delete_review_image(image_id):
    """Delete a review image"""
    image = ReviewImage.query.get_or_404(image_id)
    review = Review.query.get_or_404(image.review_id)
    
    # Check if the current user is the reviewer
    tourist = Tourist.query.filter_by(user_id=current_user.id).first()
    
    if tourist and review.tourist_id == tourist.id:
        # Delete the image file
        delete_image_file(image.image_url)
        
        # Delete the database record
        db.session.delete(image)
        db.session.commit()
        
        flash('Image deleted successfully!', 'success')
    else:
        flash('You are not authorized to delete this image.', 'danger')
    
    return redirect(url_for('main.restaurant_detail', id=review.restaurant_id))

@main.route('/delete/menu-item-review-image/<int:image_id>', methods=['POST'])
@login_required
def delete_menu_item_review_image(image_id):
    """Delete a menu item review image"""
    image = MenuItemReviewImage.query.get_or_404(image_id)
    review = MenuItemReview.query.get_or_404(image.menu_item_review_id)
    menu_item = MenuItem.query.get_or_404(review.menu_item_id)
    
    # Check if the current user is the reviewer
    tourist = Tourist.query.filter_by(user_id=current_user.id).first()
    
    if tourist and review.tourist_id == tourist.id:
        # Delete the image file
        delete_image_file(image.image_url)
        
        # Delete the database record
        db.session.delete(image)
        db.session.commit()
        
        flash('Image deleted successfully!', 'success')
    else:
        flash('You are not authorized to delete this image.', 'danger')
    
    return redirect(url_for('main.menu_item_detail', id=menu_item.id))

@main.route('/delete/menu-item/<int:id>', methods=['POST'])
@login_required
def delete_menu_item(id):
    """Delete a menu item (restaurant owner only)"""
    menu_item = MenuItem.query.get_or_404(id)
    restaurant = Restaurant.query.get_or_404(menu_item.restaurant_id)
    
    # Check if current user is the restaurant owner
    is_owner = False
    if current_user.user_type == 'owner':
        owner = RestaurantOwner.query.filter_by(user_id=current_user.id).first()
        if owner and restaurant.owner_id == owner.id:
            is_owner = True
    
    if not is_owner:
        flash('You must be the restaurant owner to delete menu items.', 'danger')
        return redirect(url_for('main.restaurant_detail', id=restaurant.id))
    
    # Delete the menu item image if it exists
    if menu_item.image_url:
        delete_image_file(menu_item.image_url)
    
    # Delete all reviews for this menu item
    reviews = MenuItemReview.query.filter_by(menu_item_id=id).all()
    for review in reviews:
        # Delete all images for this review
        images = MenuItemReviewImage.query.filter_by(menu_item_review_id=review.id).all()
        for image in images:
            delete_image_file(image.image_url)
            db.session.delete(image)
        db.session.delete(review)
    
    # Delete the menu item
    db.session.delete(menu_item)
    db.session.commit()
    
    flash('Menu item deleted successfully!', 'success')
    return redirect(url_for('main.restaurant_detail', id=restaurant.id))

@main.route('/menu-item/<int:id>/add-image', methods=['GET', 'POST'])
@login_required
def add_menu_item_image(id):
    """Add an image to a menu item (restaurant owner only)"""
    menu_item = MenuItem.query.get_or_404(id)
    restaurant = Restaurant.query.get_or_404(menu_item.restaurant_id)
    
    # Check if current user is the restaurant owner
    is_owner = False
    if current_user.user_type == 'owner':
        owner = RestaurantOwner.query.filter_by(user_id=current_user.id).first()
        if owner and restaurant.owner_id == owner.id:
            is_owner = True
    
    if not is_owner:
        flash('You must be the restaurant owner to add images to menu items.', 'danger')
        return redirect(url_for('main.menu_item_detail', id=id))
    
    form = PhotoUploadForm()
    if form.validate_on_submit():
        if form.photo.data:
            # Delete old image if it exists
            if menu_item.image_url:
                delete_image_file(menu_item.image_url)
            
            # Save new image
            photo_file = save_picture(form.photo.data, folder='menu_items')
            menu_item.image_url = photo_file
            db.session.commit()
            
            flash('Menu item image updated successfully!', 'success')
            return redirect(url_for('main.menu_item_detail', id=id))
    
    return render_template('add_menu_item_image.html', form=form, menu_item=menu_item)

# This section was removed to avoid duplicate routes

@main.route('/profile/settings', methods=['GET', 'POST'])
@login_required
def profile_settings():
    """User profile settings"""
    form = ProfileSettingsForm(obj=current_user)
    if form.validate_on_submit():
        # Verify current password if trying to change password
        if form.new_password.data and not check_password_hash(current_user.password_hash, form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('profile_settings.html', form=form)
        
        # Update basic information
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        
        # Update password if provided
        if form.new_password.data and form.current_password.data:
            current_user.password_hash = generate_password_hash(form.new_password.data)
        
        # Handle profile image upload
        if form.profile_image.data:
            profile_image = save_profile_picture(form.profile_image.data)
            current_user.profile_image = profile_image
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.profile_settings'))
    
    return render_template('profile_settings.html', form=form)

@main.route('/restaurant/<int:id>/add-review', methods=['POST'])
@login_required
def add_review(id):
    """Add a review to a restaurant (tourist only)"""
    if current_user.user_type != 'tourist':
        flash('Only tourists can add reviews.', 'danger')
        return redirect(url_for('main.restaurant_detail', id=id))
    
    tourist = Tourist.query.filter_by(user_id=current_user.id).first()
    if not tourist:
        return redirect(url_for('main.complete_tourist_profile'))
    
    # Check if already reviewed
    existing_review = Review.query.filter_by(restaurant_id=id, tourist_id=tourist.id).first()
    if existing_review:
        flash('You have already reviewed this restaurant.', 'warning')
        return redirect(url_for('main.restaurant_detail', id=id))
    
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            restaurant_id=id,
            tourist_id=tourist.id,
            rating=int(form.rating.data),
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        
        # Handle image uploads if provided
        if form.images.data and any(image.filename for image in form.images.data):
            image_filenames = save_multiple_pictures(form.images.data, folder='review_images')
            
            # Create ReviewImage objects for each uploaded image
            for filename in image_filenames:
                review_image = ReviewImage(
                    review_id=review.id,
                    image_url=filename
                )
                db.session.add(review_image)
            
            db.session.commit()
        
        # Update restaurant's average rating
        restaurant = Restaurant.query.get(id)
        restaurant.update_average_rating()
        
        flash('Your review has been added!', 'success')
    
    return redirect(url_for('main.restaurant_detail', id=id))

@main.route('/menu-item/<int:id>')
def menu_item_detail(id):
    """Menu item details page"""
    menu_item = MenuItem.query.get_or_404(id)
    restaurant = Restaurant.query.get_or_404(menu_item.restaurant_id)
    reviews = MenuItemReview.query.filter_by(menu_item_id=id).order_by(MenuItemReview.date.desc()).all()
    
    # Check if current user can review (must be a tourist and not already reviewed)
    can_review = False
    if current_user.is_authenticated and current_user.user_type == 'tourist':
        tourist = Tourist.query.filter_by(user_id=current_user.id).first()
        if tourist:
            existing_review = MenuItemReview.query.filter_by(menu_item_id=id, tourist_id=tourist.id).first()
            can_review = not existing_review
    
    review_form = MenuItemReviewForm() if can_review else None
    
    # Get other menu items from the same restaurant
    other_items = MenuItem.query.filter_by(restaurant_id=restaurant.id).filter(MenuItem.id != id).limit(4).all()
    
    return render_template('menu_item_detail.html',
                          menu_item=menu_item,
                          restaurant=restaurant,
                          reviews=reviews,
                          review_form=review_form,
                          other_items=other_items)

@main.route('/menu-item/<int:id>/add-review', methods=['POST'])
@login_required
def add_menu_item_review(id):
    """Add a review to a menu item (tourist only)"""
    if current_user.user_type != 'tourist':
        flash('Only tourists can add reviews.', 'danger')
        return redirect(url_for('main.menu_item_detail', id=id))
    
    tourist = Tourist.query.filter_by(user_id=current_user.id).first()
    if not tourist:
        return redirect(url_for('main.complete_tourist_profile'))
    
    # Check if already reviewed
    existing_review = MenuItemReview.query.filter_by(menu_item_id=id, tourist_id=tourist.id).first()
    if existing_review:
        flash('You have already reviewed this dish.', 'warning')
        return redirect(url_for('main.menu_item_detail', id=id))
    
    form = MenuItemReviewForm()
    if form.validate_on_submit():
        review = MenuItemReview(
            menu_item_id=id,
            tourist_id=tourist.id,
            rating=int(form.rating.data),
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        
        # Handle image uploads if provided
        if form.images.data and any(image.filename for image in form.images.data):
            image_filenames = save_multiple_pictures(form.images.data, folder='review_images')
            
            # Create MenuItemReviewImage objects for each uploaded image
            for filename in image_filenames:
                review_image = MenuItemReviewImage(
                    menu_item_review_id=review.id,
                    image_url=filename
                )
                db.session.add(review_image)
            
            db.session.commit()
        
        # Update menu item's average rating
        menu_item = MenuItem.query.get(id)
        menu_item.update_average_rating()
        
        flash('Your review has been added!', 'success')
    
    return redirect(url_for('main.menu_item_detail', id=id))

@main.route('/menu-item/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_menu_item(id):
    """Edit a menu item (owner only)"""
    menu_item = MenuItem.query.get_or_404(id)
    restaurant = Restaurant.query.get_or_404(menu_item.restaurant_id)
    
    # Check if current user is the owner
    owner = RestaurantOwner.query.filter_by(user_id=current_user.id).first()
    if not owner or restaurant.owner_id != owner.id:
        flash('You can only edit your own menu items.', 'danger')
        return redirect(url_for('main.menu_item_detail', id=id))
    
    form = MenuItemForm(obj=menu_item)
    if form.validate_on_submit():
        # Update menu item details
        menu_item.name = form.name.data
        menu_item.description = form.description.data
        menu_item.price = form.price.data
        menu_item.ingredients = form.ingredients.data
        menu_item.preparation_time = form.preparation_time.data
        menu_item.is_vegetarian = form.is_vegetarian.data
        menu_item.is_vegan = form.is_vegan.data
        menu_item.is_gluten_free = form.is_gluten_free.data
        menu_item.spice_level = int(form.spice_level.data)
        
        # Handle photo upload if provided
        if form.photo.data:
            photo_filename = save_picture(form.photo.data)
            menu_item.image_url = photo_filename
        
        db.session.commit()
        flash('Menu item updated successfully!', 'success')
        return redirect(url_for('main.menu_item_detail', id=id))
    
    return render_template('edit_menu_item.html', form=form, menu_item=menu_item, restaurant=restaurant)

@main.route('/search')
def search():
    """Search for restaurants"""
    query = request.args.get('query', '')
    cuisine = request.args.get('cuisine', '')
    location = request.args.get('location', '')
    rating = request.args.get('rating', '')
    
    # Base query
    restaurants = Restaurant.query
    
    # Apply filters
    if query:
        restaurants = restaurants.filter(Restaurant.name.ilike(f'%{query}%') | 
                                        Restaurant.description.ilike(f'%{query}%'))
    if cuisine:
        restaurants = restaurants.filter(Restaurant.type == cuisine)
    if location:
        restaurants = restaurants.filter(Restaurant.location == location)
    if rating:
        restaurants = restaurants.filter(Restaurant.average_rating >= float(rating))
    
    # Execute query
    results = restaurants.all()
    
    # Create search form for the navbar
    search_form = SearchForm()
    search_form.query.data = query
    search_form.cuisine.data = cuisine
    search_form.location.data = location
    search_form.rating.data = rating
    
    return render_template('search_results.html', 
                          restaurants=results, 
                          search_form=search_form,
                          query=query)

@main.route('/admin-dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard for super users"""
    # Check if user is a super user
    if current_user.user_type != 'owner' or not current_user.restaurant_owner.is_super_user:
        flash('You do not have permission to access the admin dashboard.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get unverified restaurant owners
    unverified_owners = RestaurantOwner.query.filter_by(is_verified=False).all()
    
    # Get all restaurants
    restaurants = Restaurant.query.order_by(Restaurant.created_at.desc()).all()
    
    # Get recent reviews
    recent_reviews = Review.query.order_by(Review.date.desc()).limit(10).all()
    
    # Get all Agadir locations with restaurant count
    locations = []
    for location in AgadirLocation.query.order_by(AgadirLocation.name).all():
        location_data = {
            'id': location.id,
            'name': location.name,
            'description': location.description,
            'restaurant_count': location.restaurants.count()
        }
        locations.append(location_data)
    
    return render_template('admin_dashboard.html',
                          unverified_owners=unverified_owners,
                          restaurants=restaurants,
                          recent_reviews=recent_reviews,
                          locations=locations)


@main.route('/admin/add-location', methods=['POST'])
@login_required
def add_location():
    """Add a new Agadir location"""
    # Check if user is a super user
    if current_user.user_type != 'owner' or not current_user.restaurant_owner.is_super_user:
        flash('You do not have permission to add locations.', 'danger')
        return redirect(url_for('main.index'))
    
    name = request.form.get('name')
    description = request.form.get('description')
    
    if not name:
        flash('Location name is required.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    
    # Check if location already exists
    existing_location = AgadirLocation.query.filter_by(name=name).first()
    if existing_location:
        flash(f'Location "{name}" already exists.', 'warning')
        return redirect(url_for('main.admin_dashboard'))
    
    # Create new location
    location = AgadirLocation(name=name, description=description)
    db.session.add(location)
    db.session.commit()
    
    flash(f'Location "{name}" has been added successfully.', 'success')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/admin/edit-location', methods=['POST'])
@login_required
def edit_location():
    """Edit an existing Agadir location"""
    # Check if user is a super user
    if current_user.user_type != 'owner' or not current_user.restaurant_owner.is_super_user:
        flash('You do not have permission to edit locations.', 'danger')
        return redirect(url_for('main.index'))
    
    location_id = request.form.get('id')
    name = request.form.get('name')
    description = request.form.get('description')
    
    if not location_id or not name:
        flash('Location ID and name are required.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    
    # Get the location
    location = AgadirLocation.query.get_or_404(location_id)
    
    # Check if new name already exists (if name is changed)
    if name != location.name:
        existing_location = AgadirLocation.query.filter_by(name=name).first()
        if existing_location:
            flash(f'Location "{name}" already exists.', 'warning')
            return redirect(url_for('main.admin_dashboard'))
    
    # Update location
    location.name = name
    location.description = description
    db.session.commit()
    
    flash(f'Location "{name}" has been updated successfully.', 'success')
    return redirect(url_for('main.admin_dashboard'))


# ===== MULTILINGUAL TRANSLATION SYSTEM =====

@main.route('/translate/<content_type>/<int:content_id>', methods=['GET', 'POST'])
@login_required
def translate_content(content_type, content_id):
    """Translate restaurant content (menu items, descriptions, reviews)"""
    # Get the original content based on type
    original_text = ""
    content_owner = None
    
    if content_type == 'menu':
        item = MenuItem.query.get_or_404(content_id)
        original_text = item.description
        content_owner = item.restaurant.owner.user_id
    elif content_type == 'description':
        restaurant = Restaurant.query.get_or_404(content_id)
        original_text = restaurant.description
        content_owner = restaurant.owner.user_id
    elif content_type == 'review':
        review = Review.query.get_or_404(content_id)
        original_text = review.comment
        content_owner = review.tourist.user_id
    else:
        flash('Invalid content type for translation.', 'danger')
        return redirect(url_for('main.index'))
    
    # Check for existing translations
    existing_translations = Translation.query.filter_by(
        content_type=content_type,
        content_id=content_id
    ).all()
    
    form = TranslationForm()
    form.original_text.data = original_text
    
    if form.validate_on_submit():
        # Check if translation for this language already exists
        existing = Translation.query.filter_by(
            content_type=content_type,
            content_id=content_id,
            language=form.language.data
        ).first()
        
        if existing:
            existing.translated_text = form.translated_text.data
            existing.is_verified = current_user.id == content_owner  # Auto-verify if owner
            db.session.commit()
            flash('Translation updated successfully!', 'success')
        else:
            translation = Translation(
                content_type=content_type,
                content_id=content_id,
                language=form.language.data,
                translated_text=form.translated_text.data,
                is_verified=current_user.id == content_owner  # Auto-verify if owner
            )
            db.session.add(translation)
            db.session.commit()
            flash('Translation added successfully!', 'success')
        
        # If user is a local guide, add points
        guide = LocalGuide.query.filter_by(user_id=current_user.id).first()
        if guide:
            guide.guide_points += 5  # 5 points for each translation
            db.session.commit()
            flash('You earned 5 guide points for your translation!', 'info')
        
        return redirect(url_for('main.translate_content', content_type=content_type, content_id=content_id))
    
    return render_template('translate.html', 
                          form=form, 
                          content_type=content_type,
                          content_id=content_id,
                          original_text=original_text,
                          existing_translations=existing_translations)


@main.route('/api/get-translation/<content_type>/<int:content_id>/<language>')
def get_translation_api(content_type, content_id, language):
    """API endpoint to get translation for a specific content"""
    translation = Translation.query.filter_by(
        content_type=content_type,
        content_id=content_id,
        language=language
    ).first()
    
    if translation:
        return jsonify({
            'success': True,
            'translated_text': translation.translated_text,
            'is_verified': translation.is_verified
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Translation not found'
        })


# ===== LOCAL GUIDE SYSTEM =====

@main.route('/become-local-guide', methods=['GET', 'POST'])
@login_required
def become_local_guide():
    """Apply to become a local guide"""
    # Check if user is already a guide
    existing_guide = LocalGuide.query.filter_by(user_id=current_user.id).first()
    if existing_guide:
        flash('You are already a local guide!', 'info')
        return redirect(url_for('main.local_guide_dashboard'))
    
    form = LocalGuideForm()
    
    if form.validate_on_submit():
        # Create new local guide
        guide = LocalGuide(
            user_id=current_user.id,
            neighborhood_expert=form.neighborhood_expert.data,
            verification_badge=False,  # Needs admin verification
            guide_points=10,  # Starting points
            specialties=','.join(form.specialties.data)  # Convert list to comma-separated string
        )
        db.session.add(guide)
        db.session.commit()
        
        flash('Your application to become a local guide has been submitted! An admin will review it soon.', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('become_local_guide.html', form=form)


@main.route('/local-guide-dashboard')
@login_required
def local_guide_dashboard():
    """Dashboard for local guides"""
    guide = LocalGuide.query.filter_by(user_id=current_user.id).first()
    if not guide:
        flash('You are not registered as a local guide.', 'warning')
        return redirect(url_for('main.become_local_guide'))
    
    # Get active help requests for this guide
    active_requests = TouristHelp.query.filter_by(
        guide_id=guide.id,
        status='active'
    ).all()
    
    # Get pending help requests in guide's neighborhood
    pending_requests = TouristHelp.query.filter_by(
        status='pending'
    ).join(Tourist).all()
    
    # Get completed help requests
    completed_requests = TouristHelp.query.filter_by(
        guide_id=guide.id,
        status='completed'
    ).order_by(TouristHelp.completed_at.desc()).limit(10).all()
    
    # Get translations by this guide
    translations = Translation.query.filter_by(
        is_verified=False  # Only show unverified translations
    ).all()
    
    return render_template('local_guide_dashboard.html',
                          guide=guide,
                          active_requests=active_requests,
                          pending_requests=pending_requests,
                          completed_requests=completed_requests,
                          translations=translations)


@main.route('/admin/verify-guide/<int:id>', methods=['POST'])
@login_required
def verify_guide(id):
    """Verify a local guide (admin only)"""
    # Check if user is an admin
    owner = RestaurantOwner.query.filter_by(user_id=current_user.id).first()
    if not owner or not owner.is_super_user:
        abort(403)
    
    guide = LocalGuide.query.get_or_404(id)
    guide.verification_badge = True
    db.session.commit()
    
    flash(f'Guide {guide.user.name} has been verified!', 'success')
    return redirect(url_for('main.admin_dashboard'))


# ===== TOURIST HELP SYSTEM =====

@main.route('/request-help', methods=['GET', 'POST'])
@login_required
def request_help():
    """Tourist requests help from local guides"""
    # Check if user is a tourist
    if current_user.user_type != 'tourist':
        flash('Only tourists can request help.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    tourist = Tourist.query.filter_by(user_id=current_user.id).first()
    if not tourist:
        return redirect(url_for('main.complete_tourist_profile'))
    
    form = TouristHelpForm()
    
    if form.validate_on_submit():
        # Find an available guide in the area
        guides = LocalGuide.query.filter_by(
            neighborhood_expert=form.location.data,
            verification_badge=True  # Only verified guides
        ).all()
        
        if not guides:
            flash('No guides are currently available in this area. Please try another location or try again later.', 'warning')
            return redirect(url_for('main.request_help'))
        
        # Assign to guide with fewest active requests
        selected_guide = min(guides, key=lambda g: TouristHelp.query.filter_by(guide_id=g.id, status='active').count())
        
        help_request = TouristHelp(
            tourist_id=tourist.id,
            guide_id=selected_guide.id,
            request_type=form.request_type.data,
            status='pending',
            request_details=form.request_details.data
        )
        db.session.add(help_request)
        db.session.commit()
        
        flash('Your help request has been submitted! A local guide will assist you soon.', 'success')
        return redirect(url_for('main.view_help_request', id=help_request.id))
    
    return render_template('request_help.html', form=form)


@main.route('/help-request/<int:id>')
@login_required
def view_help_request(id):
    """View a specific help request"""
    help_request = TouristHelp.query.get_or_404(id)
    
    # Check if user is authorized to view this request
    is_tourist = current_user.user_type == 'tourist' and Tourist.query.filter_by(user_id=current_user.id).first().id == help_request.tourist_id
    is_guide = LocalGuide.query.filter_by(user_id=current_user.id).first() and LocalGuide.query.filter_by(user_id=current_user.id).first().id == help_request.guide_id
    is_admin = RestaurantOwner.query.filter_by(user_id=current_user.id, is_super_user=True).first()
    
    if not (is_tourist or is_guide or is_admin):
        abort(403)
    
    return render_template('help_request.html', help_request=help_request)


@main.route('/accept-help-request/<int:id>', methods=['POST'])
@login_required
def accept_help_request(id):
    """Local guide accepts a help request"""
    help_request = TouristHelp.query.get_or_404(id)
    guide = LocalGuide.query.filter_by(user_id=current_user.id).first()
    
    if not guide:
        abort(403)
    
    # Update request status
    help_request.status = 'active'
    help_request.guide_id = guide.id
    db.session.commit()
    
    flash('You have accepted this help request. Please assist the tourist promptly.', 'success')
    return redirect(url_for('main.view_help_request', id=id))


@main.route('/complete-help-request/<int:id>', methods=['POST'])
@login_required
def complete_help_request(id):
    """Mark a help request as completed"""
    help_request = TouristHelp.query.get_or_404(id)
    guide = LocalGuide.query.filter_by(user_id=current_user.id).first()
    
    if not guide or guide.id != help_request.guide_id:
        abort(403)
    
    # Update request status
    help_request.status = 'completed'
    help_request.completed_at = datetime.utcnow()
    
    # Award points to guide
    guide.guide_points += 20  # 20 points for completing a help request
    db.session.commit()
    
    flash('Help request marked as completed. You earned 20 guide points!', 'success')
    return redirect(url_for('main.local_guide_dashboard'))


# ===== FOOD CHALLENGE SYSTEM =====

# ===== CHALLENGE COMMUNITY FEATURES =====

@main.route('/add-challenge-post', methods=['POST'])
@login_required
def add_challenge_post():
    """Add a new post for a completed food challenge"""
    if current_user.user_type != 'tourist':
        flash('Only tourists can share challenge experiences.', 'warning')
        return redirect(url_for('main.food_challenges'))
    
    participant_id = request.form.get('participant_id')
    challenge_id = request.form.get('challenge_id')
    content = request.form.get('content')
    social_post_url = request.form.get('social_post_url')
    
    if not participant_id or not challenge_id or not content:
        flash('Missing required information.', 'danger')
        return redirect(url_for('main.food_challenge_detail', id=challenge_id))
    
    # Verify the participant exists and belongs to the current user
    participant = ChallengeParticipant.query.get_or_404(participant_id)
    tourist = Tourist.query.filter_by(user_id=current_user.id).first()
    
    if participant.tourist_id != tourist.id:
        flash('You can only share your own experiences.', 'danger')
        return redirect(url_for('main.food_challenge_detail', id=challenge_id))
    
    # Verify the participant has completed the challenge
    if not participant.completed:
        flash('You must complete the challenge before sharing your experience.', 'warning')
        return redirect(url_for('main.food_challenge_detail', id=challenge_id))
    
    # Create a new post
    post = ChallengePost(
        participant_id=participant_id,
        content=content,
        created_at=datetime.utcnow(),
        likes_count=0
    )
    
    # Save image if provided
    if 'image' in request.files and request.files['image'].filename:
        image_filename = save_picture(request.files['image'], 'uploads/challenges')
        post.image_url = image_filename
    
    # Update social post URL if provided
    if social_post_url:
        participant.social_post_url = social_post_url
    
    db.session.add(post)
    db.session.commit()
    
    flash('Your experience has been shared with the community!', 'success')
    return redirect(url_for('main.food_challenge_detail', id=challenge_id))


@main.route('/add-challenge-comment', methods=['POST'])
@login_required
def add_challenge_comment():
    """Add a comment to a challenge post"""
    if current_user.user_type != 'tourist':
        flash('Only tourists can comment on challenge posts.', 'warning')
        return redirect(url_for('main.food_challenges'))
    
    post_id = request.form.get('post_id')
    content = request.form.get('content')
    
    if not post_id or not content:
        flash('Missing required information.', 'danger')
        return redirect(url_for('main.food_challenges'))
    
    # Get the post and related challenge
    post = ChallengePost.query.get_or_404(post_id)
    challenge_id = post.participant.challenge_id
    
    # Create a new comment
    tourist = Tourist.query.filter_by(user_id=current_user.id).first()
    if not tourist:
        return redirect(url_for('main.complete_tourist_profile'))
    
    comment = ChallengeComment(
        post_id=post_id,
        tourist_id=tourist.id,
        content=content,
        created_at=datetime.utcnow()
    )
    
    db.session.add(comment)
    db.session.commit()
    
    flash('Your comment has been added!', 'success')
    return redirect(url_for('main.food_challenge_detail', id=challenge_id))


@main.route('/like-challenge-post/<int:post_id>', methods=['POST'])
@login_required
def like_challenge_post(post_id):
    """Like a challenge post"""
    if current_user.user_type != 'tourist':
        return jsonify({'success': False, 'message': 'Only tourists can like posts'})
    
    post = ChallengePost.query.get_or_404(post_id)
    
    # Increment like count
    post.likes_count += 1
    db.session.commit()
    
    return jsonify({
        'success': True,
        'likes_count': post.likes_count
    })


@main.route('/user-profile/<int:user_id>')
def user_profile(user_id):
    """View a user's profile with their challenge achievements"""
    user = User.query.get_or_404(user_id)
    
    # Only show tourist profiles
    if user.user_type != 'tourist':
        flash('Only tourist profiles can be viewed.', 'warning')
        return redirect(url_for('main.index'))
    
    tourist = Tourist.query.filter_by(user_id=user_id).first_or_404()
    
    # Get completed challenges
    completed_challenges = ChallengeParticipant.query.filter_by(
        tourist_id=tourist.id,
        completed=True
    ).all()
    
    # Get challenge posts
    challenge_posts = ChallengePost.query.join(ChallengeParticipant).filter(
        ChallengeParticipant.tourist_id == tourist.id
    ).order_by(ChallengePost.created_at.desc()).all()
    
    return render_template('user_profile.html',
                          user=user,
                          tourist=tourist,
                          completed_challenges=completed_challenges,
                          challenge_posts=challenge_posts)


@main.route('/food-challenges')
def food_challenges():
    """List all food challenges and show the challenge social wall"""
    # Get all active food challenges
    challenges = FoodChallenge.query.order_by(FoodChallenge.difficulty_level).all()
    
    # Check if user is participating in any challenges
    participating = []
    if current_user.is_authenticated and current_user.user_type == 'tourist':
        tourist = Tourist.query.filter_by(user_id=current_user.id).first()
        if tourist:
            participating = [p.challenge_id for p in ChallengeParticipant.query.filter_by(tourist_id=tourist.id).all()]
    
    # Get challenge posts for the social wall
    challenge_posts = ChallengePost.query\
        .join(ChallengeParticipant, ChallengePost.participant_id == ChallengeParticipant.id)\
        .join(Tourist, ChallengeParticipant.tourist_id == Tourist.id)\
        .join(User, Tourist.user_id == User.id)\
        .order_by(ChallengePost.created_at.desc())\
        .limit(12).all()
    
    # Get top participants - using a simpler query to avoid join ambiguity
    top_participants = ChallengeParticipant.query\
        .filter(ChallengeParticipant.completed == True)\
        .order_by(ChallengeParticipant.completed_at.desc())\
        .limit(5).all()
    
    return render_template('food_challenges.html', 
                          challenges=challenges,
                          participating=participating,
                          challenge_posts=challenge_posts,
                          top_participants=top_participants)


@main.route('/food-challenge/<int:id>', methods=['GET', 'POST'])
def food_challenge_detail(id):
    """View a specific food challenge"""
    challenge = FoodChallenge.query.get_or_404(id)
    
    # Get participants
    participants = ChallengeParticipant.query.filter_by(challenge_id=challenge.id).all()
    
    # Get challenge posts
    challenge_posts = ChallengePost.query.join(ChallengeParticipant).filter(
        ChallengeParticipant.challenge_id == challenge.id
    ).order_by(ChallengePost.created_at.desc()).all()
    
    # Check if current user is participating
    user_progress = None
    join_form = JoinChallengeForm()
    progress_form = ChallengeProgressForm()
    
    if current_user.is_authenticated and current_user.user_type == 'tourist':
        tourist = Tourist.query.filter_by(user_id=current_user.id).first()
        if tourist:
            user_progress = ChallengeParticipant.query.filter_by(
                challenge_id=challenge.id,
                tourist_id=tourist.id
            ).first()
    
    # Handle join challenge form
    if join_form.validate_on_submit() and request.form.get('action') == 'join':
        if not current_user.is_authenticated:
            flash('Please log in to join a challenge.', 'warning')
            return redirect(url_for('main.login'))
        
        if current_user.user_type != 'tourist':
            flash('Only tourists can participate in food challenges.', 'warning')
            return redirect(url_for('main.food_challenge_detail', id=id))
        
        tourist = Tourist.query.filter_by(user_id=current_user.id).first()
        if not tourist:
            return redirect(url_for('main.complete_tourist_profile'))
        
        # Check if already participating
        if user_progress:
            flash('You are already participating in this challenge!', 'info')
        else:
            # Join the challenge
            participant = ChallengeParticipant(
                challenge_id=challenge.id,
                tourist_id=tourist.id,
                progress=0,
                completed=False,
                created_at=datetime.utcnow()
            )
            db.session.add(participant)
            db.session.commit()
            flash('You have joined the challenge! Start your culinary adventure!', 'success')
            return redirect(url_for('main.food_challenge_detail', id=id))
    
    # Handle progress update form
    if progress_form.validate_on_submit() and request.form.get('action') == 'update':
        if not user_progress:
            flash('You must join the challenge before updating progress.', 'warning')
        else:
            # Save proof image
            if progress_form.proof_image.data:
                image_filename = save_picture(progress_form.proof_image.data, 'uploads/challenges')
            
            # Update progress
            user_progress.progress = progress_form.progress_update.data
            user_progress.comments = progress_form.comments.data
            
            # Save social post URL if provided
            if request.form.get('social_post_url'):
                user_progress.social_post_url = request.form.get('social_post_url')
            
            # Check if challenge is completed
            if user_progress.progress >= 100:
                user_progress.completed = True
                user_progress.completed_at = datetime.utcnow()
                user_progress.shared_socially = progress_form.share_socially.data
                
                # Update challenge completion count
                challenge.completion_count += 1
                
                # Update social share count if shared
                if progress_form.share_socially.data:
                    challenge.social_share_count += 1
                
                flash('Congratulations! You have completed the challenge!', 'success')
            else:
                flash('Your progress has been updated!', 'success')
            
            db.session.commit()
            return redirect(url_for('main.food_challenge_detail', id=id))
    
    return render_template('food_challenge_detail.html',
                          challenge=challenge,
                          participants=participants,
                          challenge_posts=challenge_posts,
                          user_progress=user_progress,
                          join_form=join_form,
                          progress_form=progress_form)


@main.route('/create-food-challenge', methods=['GET', 'POST'])
@login_required
def create_food_challenge():
    """Create a new food challenge (admin only)"""
    # Check if user is an admin
    owner = RestaurantOwner.query.filter_by(user_id=current_user.id).first()
    if not owner or not owner.is_super_user:
        abort(403)
    
    form = FoodChallengeForm()
    
    if form.validate_on_submit():
        # Save challenge image
        image_filename = save_picture(form.challenge_image.data, 'uploads/challenges')
        
        challenge = FoodChallenge(
            name=form.name.data,
            description=form.description.data,
            difficulty_level=form.difficulty_level.data,
            badge_reward=form.badge_reward.data,
            image_url=image_filename
        )
        db.session.add(challenge)
        db.session.commit()
        
        flash('New food challenge created successfully!', 'success')
        return redirect(url_for('main.food_challenges'))
    
    return render_template('create_food_challenge.html', form=form)


# Restaurant impact route removed

@main.route('/admin/delete-review/<int:id>', methods=['POST'])
@login_required
def delete_review(id):
    """Delete an inappropriate review (admin only)"""
    # Check if user is an admin
    owner = RestaurantOwner.query.filter_by(user_id=current_user.id).first()
    if not owner or not owner.is_super_user:
        abort(403)
    admin = RestaurantOwner.query.filter_by(user_id=current_user.id).first()
    if not admin or not admin.is_super_user:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))
    
    review = Review.query.get_or_404(id)
    restaurant_id = review.restaurant_id
    
    db.session.delete(review)
    db.session.commit()
    
    # Update restaurant's average rating
    restaurant = Restaurant.query.get(restaurant_id)
    restaurant.update_average_rating()
    
    flash('Review has been deleted.', 'success')
    return redirect(url_for('main.admin_dashboard'))
