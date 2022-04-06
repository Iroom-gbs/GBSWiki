import sqlite3
import json
from shutil import copyfile

print("Copping...")
copyfile('./data.db', './dump.db')

conn = sqlite3.connect('./dump.db')
curs = conn.cursor()

curs.execute("SELECT name FROM sqlite_master WHERE type='table';")
for i in curs.fetchall():
    if i[0]!='data' and i[0]!='acl' and i[0]!='history':
        curs.execute(f"drop table {i[0]}")

print("Dropped Tables")

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

print("DB Generated")

jsondata = []
for i in titles:
    title = i[0]
    curs.execute("select distinct title, ip from history where title=?", [title])
    contributors = curs.fetchall()
    curs.executemany("insert into contributor values (?, ?)", contributors)
    curs.execute("select data from data where title=?",[title])
    contributors_dict = []
    for j in contributors:
        contributors_dict.append(j[1])
    jd = {'title': title, 'text': curs.fetchall()[0][0], 'contributor': contributors_dict}
    jsondata.append(jd)
curs.execute("drop table history")
conn.commit()
conn.close()
with open("dump.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(jsondata, ensure_ascii=False))
