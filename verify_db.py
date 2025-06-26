from app import app, db, User
from sqlalchemy import text
import logging

def verify_database():
    with app.app_context():
        try:
            # Test database connection
            db.session.execute(text("SELECT 1"))
            print("Database connection successful")
            
            # List all users
            users = User.query.all()
            print("\nRegistered Users:")
            print("-" * 50)
            for user in users:
                print(f"Username: {user.username}")
                print(f"ID: {user.id}")
                print(f"Password hash: {user.password_hash}")
                print("-" * 50)
            
            # Create a test user with a known password
            test_username = "testuser"
            test_password = "testpass"
            
            # Check if test user exists
            existing_user = User.query.filter_by(username=test_username).first()
            if existing_user:
                print(f"\nTest user '{test_username}' already exists")
                # Verify password
                if existing_user.check_password(test_password):
                    print("Password verification successful")
                else:
                    print("Password verification failed")
            else:
                print(f"\nCreating test user '{test_username}'")
                new_user = User(username=test_username)
                new_user.set_password(test_password)
                db.session.add(new_user)
                db.session.commit()
                print("Test user created successfully")
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    verify_database() 