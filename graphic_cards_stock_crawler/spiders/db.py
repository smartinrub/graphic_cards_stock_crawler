import mariadb
import os

__connection = None


def get_sql_connector():
    global __connection
    if not __connection:
        __connection = mariadb.connect(
            user=os.getenv("MARIADB_USER"),
            password=os.getenv("MARIADB_PASSWORD"),
            host=os.getenv("MARIADB_HOST"),
            port=3306,
            database=os.getenv("MARIADB_SCHEMA")
        )
    return __connection
