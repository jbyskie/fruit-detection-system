from app import app, db, User, Fruit, Detection
import os

def init_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create test user if it doesn't exist
        if not User.query.filter_by(username='test').first():
            test_user = User(username='test')
            test_user.set_password('test')
            db.session.add(test_user)
            db.session.commit()
            print("Test user created successfully")
        else:
            print("Test user already exists")
        
        # Create test fruit if it doesn't exist
        if not Fruit.query.filter_by(name='Mangosteen').first():
            test_fruit = Fruit(name='Mangosteen', description='A tropical fruit', image_path=None)
            db.session.add(test_fruit)
            db.session.commit()
            print("Test fruit created successfully")
        else:
            print("Test fruit already exists")
        
        # List all users
        users = User.query.all()
        print("\nRegistered Users:")
        print("-" * 50)
        for user in users:
            print(f"Username: {user.username}")
            print(f"ID: {user.id}")
            print("-" * 50)

# This script initializes the mangosteen.db database with all tables

if __name__ == "__main__":
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    init_database() 