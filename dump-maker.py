import sqlite3
import shutil

conn = sqlite3.connect('./data.db')
curs = conn.cursor()

curs.execute("SELECT name FROM sqlite_master WHERE type='table';")
for i in curs.fetchall():
    if i[0]!='data' and i[0]!='acl' and i[0]!='history':
        curs.execute(f"drop table {i[0]}")

curs.execute("select title from data")
titles = curs.fetchall()
for i in titles:
    title = i[0]
    if title.startswith('file:'):
        curs.execute("delete from data where title=?", [title])
    curs.execute("select data from acl where title=? and type='close'", [title])
    close = curs.fetchall()
    if close:
        if close[0][0] == 1:
            curs.execute("delete from data where title=?", [title])
            continue
    curs.execute("select data from acl where title=? and type='view'", [title])
    view = curs.fetchall()
    if view:
        if view[0][0]:
            curs.execute("delete from data where title=?", [title])
curs.execute("drop table acl")

curs.execute("create table contributor (title longtext, name longtext)")
curs.execute("select title from data")
titles = curs.fetchall()
for i in titles:
    title = i[0]
    curs.execute("select distinct title, ip from history where title=?", [title])
    contributors = curs.fetchall()
    curs.executemany("insert into contributor values (?, ?)", contributors)
curs.execute("drop table history")
conn.commit()
