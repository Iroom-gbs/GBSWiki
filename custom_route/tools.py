from route.tool.func import *

def edit_doc(conn, title, content, ip, send):
    curs = conn.cursor()
    curs.execute(db_change("select id from history where title = ? order by id + 0 desc"), [title])
    doc_ver = curs.fetchall()
    if doc_ver:
        curs.execute(db_change("select data from history where title = ? order by id + 0 desc"), [title])
        content_pre = curs.fetchall()[0][0]
        leng = leng_check(len(content_pre), len(content))
        curs.execute(db_change("update data set data = ? where title = ?"), [content, title])

        today = get_time()
        # ip = ip_check()
        history_plus(
            title,
            content,
            today,
            ip,
            send,
            leng
        )

        curs.execute(db_change("delete from back where link = ?"), [title])
        curs.execute(db_change("delete from back where title = ? and type = 'no'"), [title])

        render_set(
            doc_name=title,
            doc_data=content,
            data_type='backlink'
        )

        conn.commit()
    else:
        leng = '+'+str(len(content))
        curs.execute(db_change("insert into data (title, data) values (?, ?)"), [title, content])
        curs.execute(db_change("insert into data (title, data) values (?, ?)"), [title, content])
        curs.execute(db_change('select data from other where name = "count_all_title"'))
        curs.execute(db_change("update other set data = ? where name = 'count_all_title'"),
                     [str(int(curs.fetchall()[0][0]) + 1)])

        today = get_time()
        # ip = ip_check()
        history_plus(
            title,
            content,
            today,
            ip,
            send,
            leng
        )
        curs.execute(db_change("delete from back where link = ?"), [title])
        curs.execute(db_change("delete from back where title = ? and type = 'no'"), [title])

        render_set(
            doc_name=title,
            doc_data=content,
            data_type='backlink'
        )

        conn.commit()

    return redirect('/w/' + url_pas(title))


def set_acl(curs, title, why, decu, dis, view):
    curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [title, decu, "decu"])
    curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [title, dis, "dis"])
    curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [title, view, "view"])
    curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [title, why, 'why'])

    return 1