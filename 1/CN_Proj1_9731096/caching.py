import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def add_new_data(conn, task):
    """
    Create a new task
    :param conn:
    :param task:
    :return:
    """

    sql = ''' INSERT INTO dns_cache(HOSTNAME_RECORD_RECURSION, RESPONSE)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()
    return cur.lastrowid


def get_cache(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM dns_cache")
    return cur.fetchall()


def check_if_exists(conn, hostname_record_recursion):
    """
    check if data is in the table
    :param conn: the Connection object
    :param hostname_record_recursion:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM dns_cache WHERE HOSTNAME_RECORD_RECURSION=?", (hostname_record_recursion,))
    rows = cur.fetchall()
    return not len(rows) == 0


def get_response_from_cache(conn, hostname_record_recursion):
    """
    use the cache
    :param conn: the Connection object
    :param hostname_record_recursion:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT RESPONSE FROM dns_cache WHERE HOSTNAME_RECORD_RECURSION=?", (hostname_record_recursion,))
    rows = cur.fetchall()
    return rows


def clear_cache(conn):
    """
    Delete all rows in the table
    :param conn: Connection to the SQLite database
    :return:
    """
    sql = 'DELETE FROM dns_cache'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
