from app import app
from models import db, User

with app.app_context():
    user = User.query.filter_by(email="prathmesh1832@gmail.com").first()
    if user:
        user.is_admin = True
        db.session.commit()
        print("Done:", user.email, "is now admin:", user.is_admin)
    else:
        print("User not found!")