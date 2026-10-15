import os
import secrets
import string

import psycopg
from psycopg.rows import TupleRow

def generate_slug() -> str:
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(6))


def get_db_conn() -> psycopg.Connection[TupleRow]:
    return psycopg.connect(os.environ["DATABASE_URL"])
