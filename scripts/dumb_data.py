#coding=utf-8

import yaml
import MySQLdb
import uuid

cur = None

# load db config file
db_config = yaml.load(open("/Users/chen/lalamove/data/db.yml"))['ldev']['all']['all']

#connect db
def db_connect():
    global cur
    conn = MySQLdb.connect(host=db_config['host'], user=db_config['user'], passwd=db_config['passwd'], db='test')
    conn.autocommit(True)
    cur = conn.cursor(MySQLdb.cursors.DictCursor)
    return conn

#close connection
def db_close(conn):
    global cur
    cur.close()
    conn.close()

# dump 100,000 record at a time
def dump():
    input = []
    for x in range(0,100000):
        a = str(uuid.uuid4())[0:20]
        b = str(uuid.uuid4())[0:20]
        input.append("('"+ a + "', '" + b + "')")
    values = ','.join(input)
    cur.execute("INSERT INTO b(`a`,`b`) values " + values)

def run():
    conn = db_connect()
    for x in range(0,10):
        dump()
    db_close(conn)

run()
