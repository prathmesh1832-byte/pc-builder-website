from app import app
from models import db, User

with app.app_context():
    user = User.query.filter_by(email="alex.johnson@77.com").first()
    if user:
        user.set_password("Test1234")
        db.session.commit()
        print("Password reset! New password is: Test1234")
    else:
        print("User not found!")