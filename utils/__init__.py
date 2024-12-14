# Testing this  to check the connection speed for seeing output take how much time to connect
import time
from utils.db_connection import create_connection

start_time = time.time()
conn = create_connection()
conn.close()
print("Database connection time:", time.time() - start_time)
