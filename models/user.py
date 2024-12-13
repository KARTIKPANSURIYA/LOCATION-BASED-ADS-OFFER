from utils.db_connection import create_connection


class User:
    def __init__(self, username, email, password, user_type):
        """
        Initialize the User object.

        Args:
            username (str): The username of the user.
            email (str): The email address of the user.
            password (str): The password of the user.
            user_type (str): The type of user ('business' or 'personal').
        """
        self.username = username
        self.email = email
        self.password = password
        self.user_type = user_type

    def save_to_db(self):
        """
        Save the user to the database.
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
        Authenticate the user by email and password.

        Args:
            email (str): The email address of the user.
            password (str): The password of the user.

        Returns:
            tuple: The user record if authentication is successful, None otherwise.
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
        Fetch a user by their ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            tuple: The user record if found, None otherwise.
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
        Check if an email is already registered in the database.

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
