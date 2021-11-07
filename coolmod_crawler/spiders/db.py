import mariadb

__connection = None


def getSqlConnector():
    global __connection
    if not __connection:
        __connection = mariadb.connect(
            user="root",
            password="root",
            host="localhost",
            port=3306,
            database="coolmod_crawler"
        )
    return __connection
