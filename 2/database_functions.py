import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn_user_password = None
    try:
        conn_user_password = sqlite3.connect(db_file,  check_same_thread=False)
        return conn_user_password
    except Error as e:
        print(e)
    return conn_user_password


def create_table(conn_user_password, query):
    """ create a table from the create_table_sql statement
    :param conn_user_password: Connection object
    :param query: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn_user_password.cursor()
        c.execute(query)
    except Error as e:
        print(e)


def insert_into_table(conn_user_password, table, fields, values):
    """
    Create a new task
    :param conn_user_password:
    :param table: table name
    :param values: records
    :param fields: columns
    :return:
    """
    question_marks = '?'
    for i in range(len(values)-1):
        question_marks += ',?'

    sql = ''' INSERT INTO {}({})
              VALUES({}) '''.format(table, fields, question_marks)
    cur = conn_user_password.cursor()
    try:
        cur.execute(sql, values)
        conn_user_password.commit()
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


def check_password(conn_user_password, username, password):
    """
    change password
    :param conn_user_password:
    :param username:
    :param password:
    :return:
    """
    cur = conn_user_password.cursor()
    cur.execute("SELECT * FROM users_passwords WHERE username=\'{}\'".format(username))
    result = cur.fetchall()
    return result[0][1] == password


def delete_user_from_database(conn_user_password, username):
    """
    delete a user from db
    :param conn_user_password:
    :param username:
    :return:
    """
    cur = conn_user_password.cursor()
    cur.execute("DELETE FROM users_passwords WHERE username=\'{}\'".format(username))
    conn_user_password.commit()
    cur.execute("DELETE FROM users_repositories WHERE username=\'{}\'".format(username))
    conn_user_password.commit()


def check_if_user_exists(conn_user_password, username):
    """
    check if data is in the table
    :param conn_user_password: the Connection object
    :param username:
    :return:
    """
    cur = conn_user_password.cursor()
    cur.execute("SELECT * FROM users_passwords WHERE username=?", (username,))
    rows = cur.fetchall()
    return not len(rows) == 0


def update_password(conn_user_password, new_password, username):
    """
    update password
    :param conn_user_password:
    :param new_password:
    :param username:
    :return:
    """

    sql = "UPDATE users_passwords SET password = {} WHERE username = {}".format(new_password, username)

    cur = conn_user_password.cursor()
    try:
        cur.execute(sql)
        conn_user_password.commit()
    except Exception as e:
        print(e)
    return cur.lastrowid


def update_contributor(conn_user_password, contributor, repo_name, username):
    """
    Create a new task
    :param conn_user_password:
    :param contributor:
    :param username:
    :param repo_name:
    :return:
    """

    sql = "UPDATE users_repositories SET contributor = \"{}\" WHERE repo_name = {} AND username = {}".format(contributor, repo_name, username)

    cur = conn_user_password.cursor()
    try:
        cur.execute(sql)
        conn_user_password.commit()
    except Exception as e:
        print(e)
    return cur.lastrowid

