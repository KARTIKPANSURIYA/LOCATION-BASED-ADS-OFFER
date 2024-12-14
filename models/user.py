"""
this code provides functionality for managing users in a location-based system. It defines the `User` class,
which includes methods for user registration, authentication, and fetching user details.
"""

from utils.db_connection import create_connection


class User:
    def __init__(self, username, email, password, user_type):
        """
        Initializing the User object.

        Args:
            username (str): the username of the user.
            email (str): the email address of the user.
            password (str): the password of the user.
            user_type (str): the type of user ('business' or 'personal').
        """
        self.username = username
        self.email = email
        self.password = password
        self.user_type = user_type

    def save_to_db(self):
        """
        Saving the users to the database.
        """
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (username, email, password, user_type)
            VALUES (?, ?, ?, ?)
        """, (self.username, self.email, self.password, self.user_type))

        conn.commit()
        conn.close()

    @staticmethod
    def login(email, password):
        """
        Authenticating the user by email and password.

        Args:
            email (str): The email address of the user.
            password (str): The password of the user.

        Returns:
            tuple: the user record if authentication is successful.
        """
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM users WHERE email = ? AND password = ?
        """, (email, password))
        user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        """
        Fetching a user by their ID.

        Args:
            user_id (int): the ID of the user.

        Returns:
            tuple: the user record if found, none otherwise.
        """
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM users WHERE id = ?
        """, (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def is_email_registered(email):
        """
        Checking if an email is already registered in the database.

        Args:
            email (str): The email address to check.

        Returns:
            bool: True if the email is registered, False otherwise.
        """
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM users WHERE email = ?
        """, (email,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
