import sqlite3
import shutil

conn = sqlite3.connect('./data.db')
curs = conn.cursor()
curs.execute("SELECT name FROM sqlite_master WHERE type='table';")
for i in curs.fetchall():
    if i[0]!='data' and i[0]!='acl':
        curs.execute(f"drop table {i[0]}")

curs.execute("select title from data")
titles = curs.fetchall()
for i in titles:
    title = i[0]
    if title.startswith('file:') or title.startswith('user:'):
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
curs.execute("drop table acl");
conn.commit()
conn.close()

shutil.copy('./data.db', './gen.db')
shutil.copy('./data.db', './all.db')

# 일반 문서
conn = sqlite3.connect('./gen.db')
curs = conn.cursor()
curs.execute("select title from data")
titles = curs.fetchall()
for i in titles:
    title = i[0]
    if title.startswith('틀:') or title.startswith('category:') or title.startswith('템플릿:'):
        curs.execute("delete from data where title=?", [title])
        continue
    curs.execute("select data from data where title=?", [title])
    data = curs.fetchall()[0][0]
    if data.startswith('#redirect') or data.startswith('#Redirect') or data.startswith('#넘겨주기'):
        curs.execute("delete from data where title=?", [title])
conn.commit()
