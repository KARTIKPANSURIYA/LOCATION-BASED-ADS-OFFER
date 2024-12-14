import pytest
from models.user import User
from utils.db_connection import create_connection

TEST_EMAIL = "business@test.com"

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """
    Seting up the database before each test and clean up afterward.
    """
    conn = create_connection()
    cursor = conn.cursor()
    try:
        # Ensuring to test email does not exist before the test
        cursor.execute("DELETE FROM users WHERE email = ?", (TEST_EMAIL,))
        conn.commit()
    finally:
        conn.close()  # Ensuring the connection is always closed

    yield  # Running the test

    conn = create_connection()
    cursor = conn.cursor()
    try:
        # Cleaning up the test email after the test
        cursor.execute("DELETE FROM users WHERE email = ?", (TEST_EMAIL,))
        conn.commit()
    finally:
        conn.close()  # Ensuring the connection is always closed


def test_user_creation():
    """
    Test the creation of a user and saving to the database.
    """
    user = User("Test Business", TEST_EMAIL, "password123", "business")
    user.save_to_db()
    assert user is not None, "User creation failed!"
    print("User creation test passed!")


def test_user_login():
    """
    Test user login functionality.
    """
    user = User("Test Business", TEST_EMAIL, "password123", "business")
    user.save_to_db()
    logged_in_user = User.login(TEST_EMAIL, "password123")
    assert logged_in_user is not None, "User login failed!"
    print("User login test passed!")


if __name__ == "__main__":
    pytest.main()
