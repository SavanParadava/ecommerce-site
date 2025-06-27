import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="test",
        user="savan",
        password="savan123",
        port=5433
    )
