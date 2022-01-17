from route.tool.func import *


def custom_run(conn, app):
    def generate_student_doc(name,gen):
        # 학생 문서 생성
        gen = str(gen) + '기'

        curs = conn.cursor()
        curs.execute(db_change("select id from history where title = ? order by id + 0 desc"), [name + '(' + gen + ')'])
        doc_ver = curs.fetchall()
        if doc_ver:
            return re_error('/gbswiki_error/already_exist')

        curs.execute(db_change("select data from history where title = ? order by id + 0 desc"), ['템플릿:학생'])
        template = curs.fetchall()
        if not template:
            return re_error('/custom/템플릿이 없습니다.')
        content = template[0][0]
        content = content.replace('(이름)', name).replace('(기수)', gen).replace('[[분류:템플릿]]', '')
        leng = '+' + str(len(content))
        name = name + '(' + gen + ')'

        curs.execute(db_change("insert into data (title, data) values (?, ?)"), [name, content])
        curs.execute(db_change('select data from other where name = "count_all_title"'))
        curs.execute(db_change("update other set data = ? where name = 'count_all_title'"),
                     [str(int(curs.fetchall()[0][0]) + 1)])

        today = get_time()
        ip = ip_check()
        history_plus(
            name,
            content,
            today,
            ip,
            flask.request.form.get('send', ''),
            leng
        )
        curs.execute(db_change("delete from back where link = ?"), [name])
        curs.execute(db_change("delete from back where title = ? and type = 'no'"), [name])

        render_set(
            doc_name=name,
            doc_data=content,
            data_type='backlink'
        )

        # ACL 설정
        acl_type = ['decu', 'dis', 'view']
        for i in acl_type:
            curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [name, 'email', i])
        curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [name, '학생 문서', 'why'])

        # 기수 문서에 추가
        curs.execute(db_change("select data from history where title = ? order by id + 0 desc"), [gen])
        gen_doc = curs.fetchall()
        if not gen_doc:
            curs.execute(db_change("select data from history where title = ? order by id + 0 desc"), ['템플릿:기수'])
            template = curs.fetchall()
            if not template:
                return re_error('/custom/템플릿이 없습니다.')
            content = template[0][0]
            content = content.replace('(이름)((기수)기)', name).replace('[[분류:템플릿]]', '')
            leng = '+' + str(len(content))

            curs.execute(db_change("insert into data (title, data) values (?, ?)"), [gen, content])
            curs.execute(db_change('select data from other where name = "count_all_title"'))
            curs.execute(db_change("update other set data = ? where name = 'count_all_title'"),
                         [str(int(curs.fetchall()[0][0]) + 1)])

            today = get_time()
            ip = ip_check()
            history_plus(
                gen,
                content,
                today,
                ip,
                flask.request.form.get('send', ''),
                leng
            )

            curs.execute(db_change("delete from back where link = ?"), [gen])
            curs.execute(db_change("delete from back where title = ? and type = 'no'"), [gen])

            # ACL 설정
            acl_type = ['decu', 'dis', 'view']
            for i in acl_type:
                curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [gen, 'email', i])
            curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [gen, '학생 문서', 'why'])

            curs.execute(db_change("delete from back where link = ?"), [gen])
            curs.execute(db_change("delete from back where title = ? and type = 'no'"), [gen])

            render_set(
                doc_name=gen,
                doc_data=content,
                data_type='backlink'
            )
        else:
            gen_doc = gen_doc[0][0]
            student_list = gen_doc.split("'''가나다순'''으로 작성한다.")[1].split("\n")
            student_list.append(f'* [[{name}]]')
            student_list.sort()
            content = gen_doc.split("'''가나다순'''으로 작성한다.")[0] + "'''가나다순'''으로 작성한다." + "\n".join(student_list)
            leng = leng_check(len(gen_doc), len(content))
            curs.execute(db_change("update data set data = ? where title = ?"), [content, gen])
            today = get_time()
            ip = ip_check()
            history_plus(
                gen,
                content,
                today,
                ip,
                flask.request.form.get('send', ''),
                leng
            )

            curs.execute(db_change("delete from back where link = ?"), [gen])
            curs.execute(db_change("delete from back where title = ? and type = 'no'"), [gen])

            render_set(
                doc_name=gen,
                doc_data=content,
                data_type='backlink'
            )
        curs.execute(db_change("delete from gbswiki where name='student_gen' and p1=? and p2=?"),[name.replace(f'({gen})', ''),gen])

        conn.commit()

        return redirect('/w/' + url_pas(name))

    @app.route('/generate_student', methods=['POST', 'GET'])
    def generate_student():
        if admin_check(0) != 1:
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
        return generate_student_doc(name,gen)

    @app.route('/generate_student/request', methods=['POST', 'GET'])
    def request_generate_student():
        curs = conn.cursor()
        today = get_time()
        ip = ip_check()
        curs.execute(db_change("select data from user_set where id= ? and name='email' order by id + 0 desc"), [ip])
        email = curs.fetchall()
        '''
        if not email:
            return re_error("/gbswiki_error/email")
        '''
        try:
            name = flask.request.form['name']
            gen = str(int(flask.request.form['gen'])) + '기'
        except Exception:
            return easy_minify(flask.render_template(skin_check(),
                imp=['학생문서 생성 신청', wiki_set(1), wiki_custom(), wiki_css([0, 0])],
                data='''
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
        curs.execute(db_change("insert into gbswiki (name, ip, data, p1, p2) values (?, ?, ?, ?, ?)"), ['student_gen', ip, ip + ' | ' + name + '(' + gen + ') | ' + email[0][0] + ' | ' + today, name, gen])
        conn.commit()
        return redirect('/generate_student/list')

    @app.route('/generate_student/list', methods=['POST', 'GET'])
    def list_student_request():
        curs = conn.cursor()
        ip = ip_check()
        div = ''
        if admin_check(0) != 1:
            curs.execute(db_change("select data from gbswiki where ip=? and name='student_gen' order by ip + 0 desc"), [ip])
            request_data = curs.fetchall()
            curs.execute(db_change("select p1 from gbswiki where ip=? and name='student_gen' order by ip + 0 desc"), [ip])
            names = curs.fetchall()
            curs.execute(db_change("select p2 from gbswiki where ip=? and name='student_gen' order by ip + 0 desc"), [ip])
            gens = curs.fetchall()
        else:
            curs.execute(db_change("select data from gbswiki where name='student_gen' order by ip + 0 desc"))
            request_data = curs.fetchall()
            curs.execute(db_change("select p1 from gbswiki where name='student_gen' order by ip + 0 desc"))
            names = curs.fetchall()
            curs.execute(db_change("select p2 from gbswiki where name='student_gen' order by ip + 0 desc"))
            gens = curs.fetchall()
        div += '' + \
               '생성 요청 수' + ' : ' + str(len(request_data)) + \
               '<hr class="main_hr">' + \
               '<ul class="inside_ul">'
        for i in range(len(request_data)):
            div += f'<li> {request_data[i][0]} | <a href="/generate_student/accept/{names[i][0]}/{gens[i][0]}">수락</a> <a href="/generate_student/delete/{names[i][0]}/{gens[i][0]}">삭제</a> </li>'
        div += '</ul>'
        return easy_minify(flask.render_template(skin_check(),
            imp=['학생문서 생성 신청 목록', wiki_set(), wiki_custom(), wiki_css([0, 0])],
            data=div,
            menu=[['other', load_lang('return')]]
        ))

    @app.route('/generate_student/accept/<everything:name>/<everything:gen>', methods=['POST','GET'])
    def accept_student_request(name, gen):
        if admin_check(0) != 1:
            return re_error('/error/3')
        curs = conn.cursor()
        curs.execute(db_change("select data from gbswiki where name='student_gen' and p1=? and p2=? order by ip + 0 desc"),[name,gen])
        if curs.fetchall():
            return generate_student_doc(name,gen.replace('기',''))
        else: return re_error('/custom/ 일치하는 요청이 없습니다.')

    @app.route('/generate_student/delete/<everything:name>/<everything:gen>', methods=['POST','GET'])
    def delete_student_request(name, gen):
        if admin_check(0) != 1:
            return re_error('/error/3')
        curs = conn.cursor()
        curs.execute(
            db_change("select data from gbswiki where name='student_gen' and p1=? and p2=? order by ip + 0 desc"),
            [name, gen])
        if curs.fetchall():
            curs.execute(db_change("delete from gbswiki where name='student_gen' and p1=? and p2=?"), [name, gen])
            conn.commit()
            return redirect('/generate_student/list')
        else:
            return re_error('/custom/일치하는 요청이 없습니다.')