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


def create_table(conn, query):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param query: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(query)
    except Error as e:
        print(e)


def insert_into_table(conn, table, fields, values):
    """
    Create a new task
    :param conn:
    :param table: table name
    :param values: records
    :param fields: columns
    :return:
    """

    sql = ''' INSERT INTO {}({})
              VALUES(?,?) '''.format(table, fields)
    cur = conn.cursor()
    try:
        cur.execute(sql, values)
        conn.commit()
    except Exception as e:
        print(e)
    return cur.lastrowid


def get_table(conn, table):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :param table: table name
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM {}".format(table))
    return cur.fetchall()


def check_password(conn, username, password):
    """
    check if a username's real password is as same as input password.
    :param conn:
    :param username:
    :param password:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM users_info WHERE username=\'{}\'".format(username))
    result = cur.fetchall()
    # print(result[0][1] == password)
    return result[0][1] == password

def delete_user_from_database(conn, username):
    cur = conn.cursor()
    cur.execute("DELETE FROM users_info WHERE username=\'{}\'".format(username))
    conn.commit()


def check_if_user_exists(conn, username):
    """
    check if data is in the table
    :param conn: the Connection object
    :param username:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM users_info WHERE username=?", (username,))
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