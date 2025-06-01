# Restorino - Restaurant Management System for Agadir Tourism

Restorino is a web application designed to promote restaurants in Agadir, Morocco, and enhance the tourism experience. This project encourages local restaurant field development and helps tourists discover authentic dining experiences.

## Features

### For Tourists
- Browse restaurants by cuisine type
- Search by location in Agadir
- View restaurant details with photos
- Filter by rating, price range, open hours
- Write and read restaurant reviews
- View detailed menu items with photos and descriptions
- Filter dishes by dietary preferences (vegetarian, vegan, gluten-free)
- See spice level indicators for each dish
- Write dish-specific reviews

### For Restaurant Owners
- Add new restaurants
- Upload restaurant photos
- Manage detailed menu items with:
  - Photos for each dish
  - Ingredients lists
  - Preparation time
  - Dietary options (vegetarian, vegan, gluten-free)
  - Spice level indicators
  - Price in MAD
- Receive and view dish-specific reviews
- Update restaurant information

### For Admins
- Verify restaurant owners
- Moderate reviews
- Manage all restaurants

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Authentication**: Flask-Login
- **File Upload**: Flask-WTF

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/restorino.git
cd restorino
```

2. Create a virtual environment:
```
python -m venv venv
```

3. Activate the virtual environment:
- On Windows:
```
venv\Scripts\activate
```
- On macOS/Linux:
```
source venv/bin/activate
```

4. Install the required packages:
```
pip install -r requirements.txt
```

5. Run the application:
```
python app.py
```

6. Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

### Default Admin Account
- Email: admin@restorino.com
- Password: admin123

## Project Structure
```
restorino/
├── app.py (main application)
├── models.py (database models)
├── routes.py (URL routes)
├── forms.py (WTForms)
├── config.py (configuration)
├── requirements.txt
├── static/
│   ├── css/
│   │   └── style.css (Yelp-inspired styling)
│   ├── js/
│   │   └── main.js
│   └── uploads/ (restaurant photos)
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── restaurant_detail.html
│   └── add_restaurant.html
└── instance/
    └── database.db
```

## Team Credits & Contributions

- **Zaynab El AIADI** (Model): Database design and backend logic
- **Selya Bathahi** (View): Frontend design and user interface
- **Yasmine Mouhib** (View): UI/UX design and styling
- **Adnan El Aiadi** (Controller): Backend API and business logic
- **Adam Villar** (Controller): Server-side functionality
- **Adam Skouri** (Model): Database modeling
- **Ibrahim El Mansouri** (Controller): Application flow control
- **Yahya Alloucha** (Model): Data management

## License

This project is created for educational purposes.
