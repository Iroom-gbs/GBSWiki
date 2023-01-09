from .tool.func import *


def login_find_id_2(conn):
    curs = conn.cursor()

    if flask.request.method == 'POST':
        user_email = flask.request.form.get('email', '')

        curs.execute(db_change('select id from user_set where data = ? and name = "email"'), [user_email])
        id = curs.fetchall()
        if not id:
            return re_error('/error/12')
        id = id[0][0]

        if send_email(user_email, 'GBSWiki ID 찾기', f"아이디: {id}") == 0:
            return re_error('/error/18')
        return redirect('/')

    else:
        return easy_minify(flask.render_template(skin_check(),
                                                 imp=['ID 찾기', wiki_set(), wiki_custom(),
                                                      wiki_css([0, 0])],
                                                 data='''
                                                 ID는 이메일로 발송됩니다.<br><br>
                <form method="post">
                    <input placeholder="이메일" name="email" type="text">
                    <button type="submit">''' + load_lang('save') + '''</button>
                </form>
            ''',
                                                 menu=[['user', load_lang('return')]]
                                                 ))