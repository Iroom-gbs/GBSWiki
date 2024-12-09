from route.tool.func import *
from custom_route.tools import *


def generate_student_doc(conn, request_id):
    # 학생 문서 생성
    curs = conn.cursor()
    curs.execute(db_change("select name, gen, email from personal_doc where request_id=?"),[request_id])
    data = curs.fetchall()
    name = data[0][0]
    gen = data[0][1]
    email = data[0][1]
    print(gen)

    curs.execute(db_change("select data from data where title = ?"), [name + '(' + gen + ')'])
    doc = curs.fetchall()
    if doc:
        return custom_re_error('/already_exist')

    curs.execute(db_change("select data from data where title = ?"), ['템플릿:학생'])
    template = curs.fetchall()
    if not template:
        return custom_re_error('/custom/템플릿이 없습니다.')
    content = template[0][0]
    content = content.replace('(이름)', name).replace('(기수)', gen).replace('[[분류:템플릿]]', '')
    edit_doc(conn, name + "(" + gen + ")", content, "학생 문서", "학생 문서")

    # ACL 설정
    set_acl(conn, name + "(" + gen + ")", "학생 문서", "email", "email", "email")
    set_close(conn, name + "(" + gen + ")", 1)

    # 기수 문서에 추가
    curs.execute(db_change("select data from data where title = ?"), [gen])
    doc = curs.fetchall()
    if not doc:
        curs.execute(db_change("select data from data where title = ?"), ['템플릿:기수'])
        template = curs.fetchall()
        if not template:
            return custom_re_error('/custom/템플릿이 없습니다.')
        content = template[0][0]
        content = content.replace('(이름)((기수)기)', name + "(" + gen + ")").replace('[[분류:템플릿]]', '')

        edit_doc(conn, gen, content, "학생 문서", "학생 문서")
        set_acl(conn, gen, "학생 문서", "email", "email", "email")
        set_close(conn, gen, 1)
    else:
        gen_doc = doc[0][0]
        student_list = gen_doc.split("'''가나다순'''으로 작성한다.")[1].split("\n")
        student_list.append(f'* [[{name + "(" + gen + ")"}]]')
        student_list.sort()
        content = gen_doc.split("'''가나다순'''으로 작성한다.")[0] + "'''가나다순'''으로 작성한다." + "\n".join(student_list)
        edit_doc(conn, gen, content, "학생 문서", "학생 문서")
        set_acl(conn, gen, "학생 문서", "email", "email", "email")
        set_close(conn, gen, 1)
    curs.execute(db_change("update personal_doc set status = ? where request_id = ?"), [f"accepted({ip_check()}, {get_time()})" ,request_id])

    conn.commit()

    send_email(email, '학생 문서 생성됨', f"{name}님의 학생 문서 바로가기: https://gbs.wiki/w/{name+'('+gen+')'}")

    return redirect('/w/' + url_pas(name + "(" + gen + ")"))


def generate_student_2(conn):
    if admin_check(0) != 1 and admin_check(7) != 1:
        return re_error('/error/3')
    try:
        name = flask.request.form['name']
        gen = int(flask.request.form['gen'])
    except Exception:
        return easy_minify(flask.render_template(skin_check(),
            imp=['학생 문서 생성', wiki_set(1), wiki_custom(), wiki_css([0, 0])],
            data='''
            <a href="/generate_student/list">신청 목록</a>
            <hr class=\"main_hr\">
            <form method="post">
            <input placeholder="''' + '학생 이름' + '''" name="name" type="text">
            <hr class=\"main_hr\">
            <input placeholder="''' + '기수(숫자만)' + '''" name="gen" type="text">
            <hr class=\"main_hr\">
            <button type="submit">''' + '생성' + '''</button>
            </form>
            ''',
            menu=[['manager', load_lang('return')]]
            ))
    return generate_student_doc(conn, name, gen)


def request_generate_student_2(conn):
    curs = conn.cursor()
    today = get_time()
    ip = ip_check()
    curs.execute(db_change("select data from user_set where id= ? and name='email' order by id + 0 desc"), [ip])
    email = curs.fetchall()
    if not email:
        return custom_re_error("/email")
    try:
        name = flask.request.form['name']
        gen = str(int(flask.request.form['gen'])) + '기'
    except Exception:
        return easy_minify(flask.render_template(skin_check(),
            imp=['학생문서 생성 신청', wiki_set(1), wiki_custom(), wiki_css([0, 0])],
            data='''
            본인이 직접 신청하여야 합니다.<br><br>
            <form method="post">
            <input placeholder="''' + '학생 이름' + '''" name="name" type="text">
            <hr class=\"main_hr\">
            <input placeholder="''' + '기수(숫자만)' + '''" name="gen" type="text">
            <hr class=\"main_hr\">
            <button type="submit">''' + '생성' + '''</button>
            </form>
            ''',
            menu=[['manager', load_lang('return')]]
            ))

    curs.execute(db_change("select request_id from personal_doc ORDER BY time desc LIMIT 1"))
    last_request_id = curs.fetchall()
    if not last_request_id:
        last_request_id = 0
    else:
        last_request_id = last_request_id[0][0]

    curs.execute(db_change("insert into personal_doc (request_id, name, id, email, time, gen, status) values (?, ?, ?, ?, ?, ?, ?)"),
                 [str(int(last_request_id)+1), name, ip, email[0][0], today, gen, 'pending'])
    conn.commit()
    send_email('dhhwang423@gmail.com', '학생 문서 생성 신청 들어옴', f"ㅈㄱㄴ")
    return redirect('/generate_student/list')


def list_student_request_2(conn):
    curs = conn.cursor()
    ip = ip_check()
    div = ''
    if admin_check(0) != 1 and admin_check(7) != 1:
        curs.execute(db_change("select request_id from personal_doc where status = 'pending' and id = ? order by request_id asc"), [ip])
        request_ids = curs.fetchall()
        curs.execute(db_change("select name from personal_doc where status = 'pending' and id = ? order by request_id asc"), [ip])
        names = curs.fetchall()
        curs.execute(db_change("select id from personal_doc where status = 'pending' and id = ? order by request_id asc"), [ip])
        ids = curs.fetchall()
        curs.execute(db_change("select email from personal_doc where status = 'pending' and id = ? order by request_id asc"), [ip])
        emails = curs.fetchall()
        curs.execute(db_change("select time from personal_doc where status = 'pending' and id = ? order by request_id asc"), [ip])
        times = curs.fetchall()
        curs.execute(db_change("select gen from personal_doc where status = 'pending' and id = ? order by request_id asc"), [ip])
        gens = curs.fetchall()
    else:
        curs.execute(db_change("select request_id from personal_doc where status = 'pending' order by request_id asc"))
        request_ids = curs.fetchall()
        print(request_ids)
        curs.execute(db_change("select name from personal_doc where status = 'pending' order by request_id asc"))
        names = curs.fetchall()
        curs.execute(db_change("select id from personal_doc where status = 'pending' order by request_id asc"))
        ids = curs.fetchall()
        curs.execute(db_change("select email from personal_doc where status = 'pending' order by request_id asc"))
        emails = curs.fetchall()
        curs.execute(db_change("select time from personal_doc where status = 'pending' order by request_id asc"))
        times = curs.fetchall()
        curs.execute(db_change("select gen from personal_doc where status = 'pending' order by request_id asc"))
        gens = curs.fetchall()
    conn.commit()
    div += '' + \
           '<a href="/generate_student/history">신청 내역</a><br>' + \
           '생성 요청 수' + ' : ' + str(len(request_ids)) + \
           '<hr class="main_hr">' + \
           '<ul class="inside_ul">'
    for i in range(len(names)):
        div += f'<li> {ids[i][0]} | {gens[i][0]} {names[i][0]} | {emails[i][0]} | {times[i][0]} | <a href="/generate_student/accept/{request_ids[i][0]}">수락</a> <a href="/generate_student/delete/{request_ids[i][0]}">삭제</a> </li>'
    div += '</ul>'
    return easy_minify(flask.render_template(skin_check(),
        imp=['학생문서 생성 신청 목록', wiki_set(), wiki_custom(), wiki_css([0, 0])],
        data=div,
        menu=[['other', load_lang('return')]]
    ))


def accept_student_request_2(conn, request_id):
    if admin_check(0) != 1 and admin_check(7) != 1:
        return re_error('/error/3')
    curs = conn.cursor()
    curs.execute(db_change("select * from personal_doc where request_id=?"),[request_id])
    if curs.fetchall():
        return generate_student_doc(conn, request_id)
    else: return custom_re_error('/custom/ 일치하는 요청이 없습니다.')


def delete_student_request_2(conn, request_id):
    if admin_check(0) != 1 and admin_check(7) != 1:
        return re_error('/error/3')
    curs = conn.cursor()
    curs.execute(db_change("select * from personal_doc where request_id=?"),[request_id])
    print(request_id)
    if curs.fetchall():
        curs.execute(db_change("update personal_doc set status=? where request_id=?"), [f"rejected({ip_check()}, {get_time()})" ,request_id])
        conn.commit()
        return redirect('/generate_student/list')
    else:
        return custom_re_error('/custom/일치하는 요청이 없습니다.')


def show_student_request_history_2(conn):
    ip = ip_check()
    if not admin_check(0) and not admin_check(7):
        return re_error('/error/3')
    curs = conn.cursor()
    curs.execute(db_change("select request_id, name, id, email, time, gen, status from personal_doc order by time desc"))
    reqs = curs.fetchall()
    print(reqs)
    conn.commit()

    div = '' + \
          '생성 요청 수' + ' : ' + str(len(reqs)) + \
          '<hr class="main_hr">' + \
          '<ul class="inside_ul">'
    for i in reqs:
        div += f'<li> {i[0]} | {i[1]} {i[2]} | {i[3]} | {i[4]} | {i[5]} </li>'
    div += '</ul>'
    return easy_minify(flask.render_template(skin_check(),
        imp=['학생문서 생성 신청 기록', wiki_set(), wiki_custom(), wiki_css([0, 0])],
        data=div,
        menu=[['other', load_lang('return')]]
    ))
