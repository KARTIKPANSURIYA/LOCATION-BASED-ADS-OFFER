from utils.db_connection import create_connection

class User:
    def __init__(self, username, email, password, user_type):
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
        Returns the user record if credentials are valid.
        """
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM users WHERE email = ? AND password = ?
        """, (email, password))
        user = cursor.fetchone()
        conn.close()
        return user
