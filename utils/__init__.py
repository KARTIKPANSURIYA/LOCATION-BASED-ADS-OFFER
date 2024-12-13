# Test this snippet to check the connection speed
import time
from utils.db_connection import create_connection

start_time = time.time()
conn = create_connection()
conn.close()
print("Database connection time:", time.time() - start_time)
