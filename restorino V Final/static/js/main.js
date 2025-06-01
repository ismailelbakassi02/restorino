/**
 * Restorino - Restaurant Management System for Agadir Tourism
 * Main JavaScript file
 */

document.addEventListener('DOMContentLoaded', function() {
    // Close flash messages
    const closeButtons = document.querySelectorAll('.close-btn');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    });

    // User type selection in registration form
    const touristRadio = document.getElementById('tourist');
    const ownerRadio = document.getElementById('owner');
    
    if (touristRadio && ownerRadio) {
        touristRadio.addEventListener('change', function() {
            document.querySelectorAll('.user-type-option label').forEach(label => {
                label.classList.remove('selected');
            });
            this.parentElement.querySelector('label').classList.add('selected');
        });
        
        ownerRadio.addEventListener('change', function() {
            document.querySelectorAll('.user-type-option label').forEach(label => {
                label.classList.remove('selected');
            });
            this.parentElement.querySelector('label').classList.add('selected');
        });
    }

    // Star rating display
    const ratingSelect = document.getElementById('rating');
    if (ratingSelect) {
        ratingSelect.addEventListener('change', function() {
            updateStarDisplay(this.value);
        });
        
        // Initialize star display
        if (ratingSelect.value) {
            updateStarDisplay(ratingSelect.value);
        }
    }

    // Photo gallery lightbox
    const galleryItems = document.querySelectorAll('.gallery-item img');
    galleryItems.forEach(item => {
        item.addEventListener('click', function() {
            openLightbox(this.src, this.parentElement.querySelector('.caption')?.textContent);
        });
    });

    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            document.querySelector('.navbar-menu').classList.toggle('active');
        });
    }

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(this)) {
                event.preventDefault();
            }
        });
    });
});

/**
 * Update the visual star display based on rating value
 */
function updateStarDisplay(rating) {
    const ratingDisplay = document.querySelector('.rating-display');
    if (!ratingDisplay) return;
    
    ratingDisplay.innerHTML = '';
    
    for (let i = 1; i <= 5; i++) {
        const star = document.createElement('i');
        if (i <= rating) {
            star.className = 'fas fa-star';
        } else {
            star.className = 'far fa-star';
        }
        ratingDisplay.appendChild(star);
    }
}

/**
 * Open lightbox for photo gallery
 */
function openLightbox(src, caption) {
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    
    lightbox.innerHTML = `
        <div class="lightbox-content">
            <span class="close-lightbox">&times;</span>
            <img src="${src}" alt="${caption || 'Restaurant photo'}">
            ${caption ? `<div class="lightbox-caption">${caption}</div>` : ''}
        </div>
    `;
    
    document.body.appendChild(lightbox);
    document.body.style.overflow = 'hidden';
    
    // Close lightbox when clicking on background or close button
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox || e.target.className === 'close-lightbox') {
            document.body.removeChild(lightbox);
            document.body.style.overflow = '';
        }
    });
}

/**
 * Basic form validation
 */
function validateForm(form) {
    let valid = true;
    
    // Check required fields
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            
            // Create error message if it doesn't exist
            let errorDiv = field.nextElementSibling;
            if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = 'This field is required';
                field.parentNode.insertBefore(errorDiv, field.nextSibling);
            }
            
            valid = false;
        } else {
            field.classList.remove('is-invalid');
            
            // Remove error message if it exists
            const errorDiv = field.nextElementSibling;
            if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
                errorDiv.remove();
            }
        }
    });
    
    // Check email format
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value.trim() && !validateEmail(field.value)) {
            field.classList.add('is-invalid');
            
            // Create error message if it doesn't exist
            let errorDiv = field.nextElementSibling;
            if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = 'Please enter a valid email address';
                field.parentNode.insertBefore(errorDiv, field.nextSibling);
            }
            
            valid = false;
        }
    });
    
    // Check password match if confirm password exists
    const password = form.querySelector('input[name="password"]');
    const confirmPassword = form.querySelector('input[name="confirm_password"]');
    
    if (password && confirmPassword && password.value !== confirmPassword.value) {
        confirmPassword.classList.add('is-invalid');
        
        // Create error message if it doesn't exist
        let errorDiv = confirmPassword.nextElementSibling;
        if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = 'Passwords do not match';
            confirmPassword.parentNode.insertBefore(errorDiv, confirmPassword.nextSibling);
        }
        
        valid = false;
    }
    
    return valid;
}

/**
 * Validate email format
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}
