from app import app, db, User
import logging

def check_users():
    with app.app_context():
        # Get all users
        users = User.query.all()
        print("\nRegistered Users:")
        print("-" * 50)
        for user in users:
            print(f"Username: {user.username}")
            print(f"ID: {user.id}")
            print("-" * 50)
        
        # Check if database exists
        try:
            db.session.execute("SELECT 1")
            print("\nDatabase connection successful")
        except Exception as e:
            print(f"\nDatabase error: {str(e)}")

if __name__ == "__main__":
    check_users() 