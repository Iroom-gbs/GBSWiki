from oauthlib.oauth2 import WebApplicationClient
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
        leng = '+' + str(len(content))
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


def set_acl(conn, title, why, decu, dis, view):
    curs = conn.cursor()
    curs.execute(db_change("select data from acl where title=?"), [title])
    exist = curs.fetchall()
    if exist:
        curs.execute(db_change("update acl set data = ? where title = ? and type = ?"), [decu, title, "decu"])
        curs.execute(db_change("update acl set data = ? where title = ? and type = ?"), [dis, title, "dis"])
        curs.execute(db_change("update acl set data = ? where title = ? and type = ?"), [view, title, "view"])
        curs.execute(db_change("update acl set data = ? where title = ? and type = ?"), [why, title, 'why'])
    else:
        curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [title, decu, "decu"])
        curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [title, dis, "dis"])
        curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [title, view, "view"])
        curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [title, why, 'why'])
    return 1


def set_close(conn, title, data):
    curs = conn.cursor()
    curs.execute(db_change("select data from acl where title = ? and type = 'close'"), [title])
    exist = curs.fetchall()
    if exist:
        curs.execute(db_change("update acl set data = ? where title = ? and type = 'close'"), [data, title])
    else:
        curs.execute(db_change("insert into acl (title, data, type) values (?, ?, 'close')"), [title, data])
    return


def custom_re_error(error_code):
    if error_code.startswith('/custom'):
        return easy_minify(flask.render_template(skin_check(),
                                                 imp=[load_lang('error'), wiki_set(1), wiki_custom(), wiki_css([0, 0])],
                                                 data='' + \
                                                      '<h2>' + load_lang('error') + '</h2>' + \
                                                      '<ul class="inside_ul">' + \
                                                      '<li>' + error_code.replace('/custom/', '') + '</li>' + \
                                                      '</ul>' + \
                                                      '',
                                                 menu=0
                                                 )), 400
    if error_code == '/no_input':
        data = '제목 또는 내용이 없습니다.'
    elif error_code == '/not_changed':
        data = '변경사항이 없습니다.'
    elif error_code == '/already_exist':
        data = '이미 문서가 존재합니다.'
    elif error_code == '/email':
        data = '이메일 인증이 필요합니다.'
    elif error_code == '/email_filter':
        data = '학교 이메일(gbs.*@ggh.goe.go.kr)만 사용 가능합니다. 학생/교사 중 이메일이 없는 경우 관리자에게 별도 문의하세요.'
    elif error_code == '/unknown':
        data = '알수 없는 오류'
    return easy_minify(flask.render_template(skin_check(),
                                             imp=[load_lang('error'), wiki_set(1), wiki_custom(), wiki_css([0, 0])],
                                             data='' + \
                                                  '<h2>' + load_lang('error') + '</h2>' + \
                                                  '<ul class="inside_ul">' + \
                                                  '<li>' + data + '</li>' + \
                                                  '</ul>' + \
                                                  '',
                                             menu=0
                                             )), 400


def get_email(conn, ip):
    curs = conn.cursor()
    curs.execute(db_change("select data from user_set where id= ? and name='email' order by id + 0 desc"), [ip])
    email = curs.fetchall()
    if not email: return ""
    return str(email[0][0])


def check_close(conn, title):
    curs = conn.cursor()
    curs.execute(db_change("select data from acl where title = ? and type = 'close'"), [title])
    data = curs.fetchall()
    if data:
        if data[0][0] == '1':
            return True
    return False


def get_google_oauth_client():
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", open("../.google_client_id").read().strip())
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", open("../.google_client_secret").read().strip())
    client = WebApplicationClient(GOOGLE_CLIENT_ID)

    return GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, client