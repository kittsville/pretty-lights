import sqlite3

def setupDb(con):
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS color
               (modified_at INTEGER)''')

    con.commit()
    con.close()

def connect():
    return sqlite3.connect('state.db')
