from app import app
from models import db, User

with app.app_context():
    user = User.query.filter_by(email="alex.johnson@77.com").first()
    if user:
        user.is_admin = True
        db.session.commit()
        print("Done:", user.email, "is now admin:", user.is_admin)
    else:
        print("User not found!")