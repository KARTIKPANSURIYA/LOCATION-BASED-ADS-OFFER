from models.user import User

def test_user_creation():
    """
    Test the creation of a user and saving to the database.
    """
    user = User("Test Business", "business@test.com", "password123", "business")
    user.save_to_db()
    print("User created successfully!")

def test_user_login():
    """
    Test user login functionality.
    """
    user = User.login("business@test.com", "password123")
    assert user, "User login failed"
    print("User logged in successfully:", user)

if __name__ == "__main__":
    test_user_creation()
    test_user_login()
