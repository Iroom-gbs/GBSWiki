from custom_route.tools import custom_re_error
from .tool.func import *

def user_manage_email_2(conn, name):
    curs = conn.cursor()
    if admin_check(1) == 1:
        if flask.request.method == 'GET':
            curs.execute(db_change("SELECT data FROM user_set WHERE name = 'email' AND id = ?"), [name,])
            original_email = curs.fetchall()
            if not original_email:
                original_email = ''
            else: original_email = original_email[0][0]

            return easy_minify(flask.render_template(skin_check(),
                imp=['이메일 변경', wiki_set(1), wiki_custom(), wiki_css([0, 0])],
                data='''
                    현재 이메일: ''' + original_email + '''<br><br>
                    <form method="post">
                    <input placeholder="''' + '변경할 이메일' + '''" name="email" type="text">
                    <hr class=\"main_hr\">
                    <button type="submit">''' + '변경' + '''</button>
                    </form>
                    ''',
                menu=[['manager', load_lang('return')]]
                ))
        elif flask.request.method == 'POST':
            new_email = flask.request.form.get('email')

            curs.execute(db_change("SELECT data FROM user_set WHERE name = 'email' AND id = ?"), [name, ])
            original_email = curs.fetchall()
            if not original_email:
                print(1)
                curs.execute(db_change("INSERT INTO user_set (test, name, id, data) values (?, ?, ?, ?)"), ['', 'email', name, new_email])
            else: curs.execute(db_change("UPDATE user_set SET data = ? WHERE name='email' AND id = ?"), [new_email, name, ])

            conn.commit()
            return redirect(f'/user/{name}')

    else:
        return re_error('/error/3')