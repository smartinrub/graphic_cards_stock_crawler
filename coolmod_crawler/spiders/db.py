import mariadb
import os

__connection = None


def get_sql_connector():
    global __connection
    if not __connection:
        __connection = mariadb.connect(
            user=os.getenv("MARIADB_USER"),
            password=os.getenv("MARIADB_PASSWORD"),
            host="localhost",
            port=3306,
            database="coolmod_crawler"
        )
    return __connection
