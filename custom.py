from route.tool.func import *


def custom_run(conn, app):
    @app.route('/generate_student', methods=['POST', 'GET'])
    def generate_student():
        if admin_check(0) != 1:
            return re_error('/error/3')
        try:
            name = flask.request.form['name']
            gen = flask.request.form['gen']
        except Exception:
            return easy_minify(flask.render_template(skin_check(),
                imp=['학생 문서 생성', wiki_set(1), wiki_custom(), wiki_css([0, 0])],
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
        gen = str(gen) + '기'

        curs = conn.cursor()
        curs.execute(db_change("select id from history where title = ? order by id + 0 desc"), [name + '(' + gen + ')'])
        doc_ver = curs.fetchall()
        if doc_ver:
            return re_error('/gbswiki_error/already_exist')

        curs.execute(db_change("select data from history where title = ? order by id + 0 desc"), ['템플릿:학생'])
        template = curs.fetchall()
        if not template:
            return re_error('Unknown Error')
        content = template[0][0]
        print(content)
        content = content.replace('(이름)', name).replace('(기수)', gen)
        leng = '+' + str(len(content))
        name = name + '(' + gen + ')'

        curs.execute(db_change("insert into data (title, data) values (?, ?)"), [name, content])
        curs.execute(db_change('select data from other where name = "count_all_title"'))
        curs.execute(db_change("update other set data = ? where name = 'count_all_title'"), [str(int(curs.fetchall()[0][0]) + 1)])

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

        acl_type = ['decu', 'dis', 'view']
        for i in acl_type:
            curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [name, 'email', i])
        curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [name, '학생 문서', 'why'])

        render_set(
            doc_name=name,
            doc_data=content,
            data_type='backlink'
        )

        conn.commit()

        return redirect('/w/' + url_pas(name))
