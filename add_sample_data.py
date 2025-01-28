from app import app, db, Admin, Mobile, Banner
import os
from werkzeug.security import generate_password_hash

def add_sample_data():
    with app.app_context():
        # Create tables
        db.create_all()

        # Add admin if not exists
        if not Admin.query.filter_by(username="rajib7677").first():
            admin = Admin(
                username="rajib7677",
                password_hash=generate_password_hash("rajib7677")
            )
            db.session.add(admin)

        # Add sample mobiles
        sample_mobiles = [
            {
                "name": "iPhone 13",
                "condition": "Excellent",
                "price": 45000,
                "specs": """RAM: 4GB
Storage: 128GB
Screen: 6.1-inch Super Retina XDR
Camera: Dual 12MP
Battery: 3240mAh
Color: Midnight
Original Price: 79,900
Purchase Date: 1 year old""",
                "images": "iphone13.jpg"
            },
            {
                "name": "Samsung Galaxy S21",
                "condition": "Good",
                "price": 35000,
                "specs": """RAM: 8GB
Storage: 256GB
Screen: 6.2-inch Dynamic AMOLED
Camera: Triple 12MP+12MP+64MP
Battery: 4000mAh
Color: Phantom Gray
Original Price: 69,999
Purchase Date: 1.5 years old""",
                "images": "s21.jpg"
            }
        ]

        # Add sample mobiles if none exist
        if not Mobile.query.first():
            for mobile_data in sample_mobiles:
                mobile = Mobile(**mobile_data)
                db.session.add(mobile)

        # Add sample banner if none exist
        if not Banner.query.first():
            banner = Banner(image="banner1.jpg", active=True)
            db.session.add(banner)

        db.session.commit()

if __name__ == "__main__":
    add_sample_data()
