import os
import secrets
import string

import psycopg


def generate_slug() -> str:
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(6))

def get_db_conn() :
    return psycopg.connect(os.environ['DATABASE_URL'])