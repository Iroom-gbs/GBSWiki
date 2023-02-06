import datetime

from .tool.func import *

'''
DB 구조
OAuth2 테이블
    client_name, client_id, client_secret, client_uri, redirect_uri, scope
OAuth2_Code 테이블
    client_id, scope, code, user, expire
OAuth2_Token 테이블
    client_id, access_token, refresh_token, user, scope, expire
'''
scope_info = {
    'id': '사용자 ID',
    'id_email': '사용자 ID와 이메일'
}


def oauth2_login_2(conn):
    curs = conn.cursor()

    if flask.request.method == 'GET':
        try:
            args = flask.request.args.to_dict()
            client_id = args['client_id']
            redirect_uri = args['redirect_uri']
            scope = args['scope']
        except:
            return "Error: missing parameters", 400

        # client 확인
        curs.execute(db_change("select client_name, redirect_uri, scope from OAuth2 where client_id = ?"), [client_id])
        client = curs.fetchall()
        if not client:
            return "Error: client not found", 400
        client = client[0]

        if redirect_uri not in client[1].replace('\r','').split('\n'):
            return "Error: redirect_uri not match", 400
        if client[2] != scope:
            return "Error: scpoe not match", 400

        if ip_or_user() == 0:
            return easy_minify(
                flask.render_template(skin_check(),
                imp = ["GBSWiki로 로그인", wiki_set(), wiki_custom(), wiki_css([0, 0])],
                data =  '''
                        <h2>''' + client[0] + '''에 로그인</h2> 해당 서비스에서 에서 다음과 같은 권한을 요구합니다.<br><br>
                        <li> ''' + scope_info[scope] + '''</li>
                        <li> 유저 상태 </li><br><br>
                        <form method="post">
                            ''' + captcha_get() + '''
                            <button type="submit">''' + ip_check() + '''(으)로 ''' + load_lang('login') + '''</button>
                            ''' + http_warning() + '''
                        </form>
                        '''
                ))

        return easy_minify(
            flask.render_template(skin_check(),
                imp = ["GBSWiki로 로그인", wiki_set(), wiki_custom(), wiki_css([0, 0])],
                data =  '''
                        <h2>''' + client[0] + '''에 로그인</h2> 해당 서비스에서 에서 다음과 같은 권한을 요구합니다.<br><br>
                        <li> ''' + scope_info[scope] + '''</li>
                        <li> 유저 상태 </li><br><br>
                        <form method="post">
                            <input placeholder="''' + load_lang('id') + '''" name="id" type="text">
                            <hr class="main_hr">
                            <input placeholder="''' + load_lang('password') + '''" name="pw" type="password">
                            <hr class="main_hr">
                            ''' + captcha_get() + '''
                            <button type="submit">''' + load_lang('login') + '''</button>
                            ''' + http_warning() + '''
                        </form>
                        '''
            ))

    if flask.request.method == "POST":
        try:
            args = flask.request.args.to_dict()
            client_id = args['client_id']
            redirect_uri = args['redirect_uri']
            scope = args['scope']
        except:
            return "Error: missing parameters"

        # client 확인
        curs.execute(db_change("select client_name, redirect_uri, scope from OAuth2 where client_id = ?"), [client_id])
        client = curs.fetchall()
        if not client:
            return "Error: client not found", 400
        client = client[0]
        if redirect_uri not in client[1].replace('\r','').split('\n'):
            return "Error: redirect_uri not match", 400
        if client[2] != scope:
            return "Error: scpoe not match", 400

        if ip_or_user() == 0:
            user_id = ip_check()

        else:
            # 로그인
            user_id = flask.request.form.get('id', '')
            user_data = {}

            curs.execute(db_change(
                'select name, data from user_set where id = ? and name = "pw" or name = "encode"'
            ), [user_id])
            sql_data = curs.fetchall()
            if not sql_data:
                return re_error('/error/2')

            for i in sql_data:
                user_data[i[0]] = i[1]

            if len(user_data) < 2:
                return re_error('/error/2')

            if pw_check(
                    flask.request.form.get('pw', ''),
                    user_data['pw'],
                    user_data['encode'],
                    user_id
            ) != 1:
                return re_error('/error/10')

        # code 생성
        code = load_random_key(32)
        curs.execute(db_change("insert into OAuth2_Code (client_id, scope, code, user, expire) values (?, ?, ?, ?, ?)"), [
            client_id, scope, code, user_id, (datetime.datetime.today() + datetime.timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
        ])
        conn.commit()
        uri = redirect_uri + "?code=" + code
        return flask.redirect(uri)


def oauth2_auth_2(conn):
    curs = conn.cursor()
    try:
        args = flask.request.args.to_dict()
        client_id = args['client_id']
        scope = args['scope']
        client_secret = flask.request.form.get('client_secret', '')
    except:
        return "Error: missing parameters", 400

    # client 확인
    curs.execute(db_change("select client_secret, redirect_uri, scope from OAuth2 where client_id = ?"), [client_id])
    client = curs.fetchall()
    if not client:
        return "Error: client not found", 400
    client = client[0]

    if client[0] != pw_encode(client_secret):
        return "Error: client_secret not match", 400
    if client[2] != scope:
        return "Error: scope not match", 400

    # code 확인
    code = flask.request.form['code']
    curs.execute(db_change("select user, expire from OAuth2_Code where client_id = ? and code = ?"), [
        client_id, code
    ])
    code_data = curs.fetchall()
    if not code_data:
        return "Error: code not found", 400
    if datetime.datetime.strptime(code_data[0][1], '%Y-%m-%d %H:%M:%S') < datetime.datetime.today():
        curs.execute(db_change("delete from OAuth2_Code where client_id = ? and code = ?"), [
            client_id, code
        ])
        conn.commit()
        return "Error: code expired", 400

    # access code 발급
    access_code = load_random_key(32)
    refresh_code = load_random_key(32)
    expire = datetime.datetime.today() + datetime.timedelta(minutes=60)
    curs.execute(db_change("insert into OAuth2_Token (client_id, access_token, refresh_token, user, scope, expire) values (?, ?, ?, ?, ?, ?)"), [
        client_id, access_code, refresh_code, code_data[0][0], scope, expire.strftime("%Y-%m-%d %H:%M:%S")
    ])
    curs.execute(db_change("delete from OAuth2_Code where client_id = ? and code = ?"), [
        client_id, code
    ])
    conn.commit()
    return {
        "access_token": access_code,
        "refresh_token": refresh_code,
        "scope": scope,
        "expire": expire.strftime("%Y-%m-%d %H:%M:%S"),
        "expire_refresh": (expire + datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
    }


def oauth2_refresh_2(conn):
    curs = conn.cursor()

    try:
        args = flask.request.args.to_dict()
        client_id = args['client_id']
        scope = args['scope']
        client_secret = flask.request.form.get('client_secret', '')
    except:
        return "Error: missing parameters", 400

    # client 확인
    curs.execute(db_change("select client_secret, redirect_uri, scope from OAuth2 where client_id = ?"), [client_id])
    client = curs.fetchall()
    if not client:
        return "Error: client not found", 400

    client = client[0]
    if client[0] != pw_encode(client_secret):
        return "Error: client_secret not match", 400
    if client[2] != scope:
        return "Error: scpoe not match", 400

    # code 확인
    refresh_token = flask.request.form['refresh_token']
    curs.execute(db_change("select user, expire from OAuth2_Token where client_id = ? and refresh_token = ?"), [
        client_id, refresh_token
    ])
    code_data = curs.fetchall()
    if not code_data:
        return "Error: token not found", 400
    if datetime.datetime.strptime(code_data[0][1], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(minutes=30) < datetime.datetime.today():
        curs.execute(db_change("delete from OAuth2_Token where client_id = ? and refresh_token = ?"), [
            client_id, refresh_token
        ])
        return "Error: Token expired", 400

    # access code 발급
    access_code = load_random_key(32)
    refresh_code = load_random_key(32)
    expire = datetime.datetime.today() + datetime.timedelta(minutes=60)
    # 기존 토큰 삭제
    curs.execute(db_change(
        "delete from OAuth2_Token where client_id = ? and refresh_token = ?"), [
            client_id, refresh_token
    ])
    curs.execute(db_change(
        "insert into OAuth2_Token (client_id, access_token, refresh_token, user, scope, expire) values (?, ?, ?, ?, ?, ?)"),
                 [
                     client_id, access_code, refresh_code, code_data[0][0], scope, expire.strftime("%Y-%m-%d %H:%M:%S")
                 ])
    conn.commit()
    return {
        "access_token": access_code,
        "refresh_token": refresh_code,
        "scope": scope,
        "expire": expire.strftime("%Y-%m-%d %H:%M:%S"),
        "expire_refresh": (expire + datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
    }