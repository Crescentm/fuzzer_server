import logging

import mysql.connector
from config.config_value import *

connection = None

connect_config = {
    'user': MYSQL_CONFIG['user'],
    'password': MYSQL_CONFIG['password'],
    'host': MYSQL_CONFIG['host'],
    'database': MYSQL_CONFIG['database'],
    'raise_on_warnings': MYSQL_CONFIG.getboolean('raise_on_warnings'),
    'buffered': MYSQL_CONFIG.getboolean('buffered'),
    'autocommit': MYSQL_CONFIG.getboolean('autocommit')
}


def db_connect():
    con = None
    try:
        con = mysql.connector.connect(**connect_config)
    except mysql.connector.Error as err:
        logging.error(err)

    return con


def get_cursor(**kwargs):
    global connection
    if connection is None:
        connection = db_connect()

    try:
        connection.ping(reconnect=True, attempts=3, delay=5)
    except mysql.connector.Error:
        connection = db_connect()

    return connection.cursor(**kwargs)


connection = db_connect()

if connection is None:
    logging.error("No sql")
    exit(1)
