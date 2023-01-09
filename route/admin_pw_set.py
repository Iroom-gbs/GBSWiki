from .tool.func import *

def admin_pw_set_2(conn, name):
    curs = conn.cursor()

    if flask.request.method == 'GET':
        if not admin_check(0):
            return re_error('/error/3')

        return easy_minify(flask.render_template(skin_check(),
            imp = ['비밀번호 변겅', wiki_set(), wiki_custom(), wiki_css([0, 0])],
            data = '''
                <form method="post">
                    <input placeholder="변경할 텍스트" name="pw" type="password">
                    <hr class=\"main_hr\">
                    <button type="submit">확인</button>
                </form>
            ''',
            menu = [['manager', load_lang('return')]]
        ))
    elif flask.request.method == 'POST':
        if not admin_check(0):
            return re_error('/error/3')

        pw = flask.request.form.get('pw', '')

        if pw:
            curs.execute(db_change("update user_set set data = ? where id = ? and name = 'pw'"), [pw_encode(pw), name])
            conn.commit()

            return redirect('/manager')
        else:
            return redirect('/user/admin/pw_set')