import os
import secrets
from PIL import Image
from flask import current_app

def save_picture(form_picture, folder='menu_items', size=(800, 600)):
    """
    Save a picture uploaded through a form
    
    Args:
        form_picture: The uploaded file from the form
        folder: The subfolder in static/uploads to save to (default: menu_items)
        size: Tuple of (width, height) to resize the image to (default: 800x600)
        
    Returns:
        The filename of the saved picture (to be stored in the database)
    """
    # Create a random filename to avoid collisions
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_ext.lower()  # Convert extension to lowercase
    
    # Create the upload directory if it doesn't exist
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', folder)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the picture path
    picture_path = os.path.join(upload_dir, picture_filename)
    
    # Resize and save the image
    img = Image.open(form_picture)
    img.thumbnail(size)
    img.save(picture_path)
    
    # Return the relative path to be stored in the database
    return os.path.join('uploads', folder, picture_filename).replace('\\', '/')


def save_profile_picture(form_picture, size=(200, 200)):
    """
    Save a profile picture uploaded through a form
    
    Args:
        form_picture: The uploaded file from the form
        size: Tuple of (width, height) to resize the image to (default: 200x200)
        
    Returns:
        The filename of the saved picture (to be stored in the database)
    """
    return save_picture(form_picture, folder='profile_pics', size=size)


def save_multiple_pictures(form_pictures, folder='review_images', size=(800, 600)):
    """
    Save multiple pictures uploaded through a form
    
    Args:
        form_pictures: List of uploaded files from the form
        folder: The subfolder in static/uploads to save to (default: review_images)
        size: Tuple of (width, height) to resize the images to (default: 800x600)
        
    Returns:
        List of filenames of the saved pictures (to be stored in the database)
    """
    saved_filenames = []
    
    for picture in form_pictures:
        if picture and hasattr(picture, 'filename') and picture.filename:
            filename = save_picture(picture, folder=folder, size=size)
            saved_filenames.append(filename)
    
    return saved_filenames
