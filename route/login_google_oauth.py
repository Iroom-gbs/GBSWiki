import os

from flask import request
from oauthlib.oauth2 import WebApplicationClient

import custom_route.tools
from .tool.func import *


GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", os.environ.get("GOOGLE_CLIENT_SECRET"))
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
client = WebApplicationClient(GOOGLE_CLIENT_ID)



def login_google_oauth_2(conn):
    curs = conn.cursor()

    if ban_check(None, 'login') == 1:
        return re_error('/ban')

    ip = ip_check()
    admin = admin_check()
    if admin != 1 and ip_or_user(ip) == 0:
        return redirect('/user')

    if admin != 1:
        curs.execute(db_change('select data from other where name = "reg"'))
        set_d = curs.fetchall()
        if set_d and set_d[0][0] == 'on':
            return re_error('/ban')

    if "auth" not in request.args.to_dict():
        return easy_minify(flask.render_template(skin_check(),
            imp = ["학생 인증", wiki_set(), wiki_custom(), wiki_css([0, 0])],
            data = '''
            학교 계정(@ggh.goe.go.kr)로 로그인해서 인증을 받으세요.<br>
            졸업생/합격생/기타 학교 계정이 없는 경우, <a href="https://open.kakao.com/o/sv9iXhbf" target="_blank">여기</a>로 문의하세요.<br>
            <br><br>
            <a class="btn btn-secondary tools-btn" href="/auth/google?auth=1"><height=30%><img src="/views/LibertyForNorth/img/google_login.png"/></a>  
            ''',
            menu = [['user', load_lang('return')]]
        ))
    return login()


def login():
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    return flask.redirect(client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url.replace("http:", "https:") + "/callback",
        scope=["openid", "email", "profile"],
    ))


def login_google_oauth_callback_2(conn):
    code = request.args.get("code")
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url.replace("http:", "https:"),
        redirect_url=request.base_url.replace("http:", "https:"),
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    print(userinfo_response.json())
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
        hd = userinfo_response.json()["hd"]
        if not (users_email.startswith("gbs.") and hd.endswith("ggh.goe.go.kr")):
            return custom_route.custom_re_error("/custom/경기북과학고등학교 계정이 아닙니다.")

        curs = conn.cursor()
        curs.execute(db_change("select data from user_set where name = email"))
        if emails:=curs.fetchall():
            emails = map(emails, lambda x: x[0].lower().strip())
            if users_email.lower().strip() in emails:
                return custom_route.custom_re_error("/custom/이미 가입된 이메일입니다.")

        curs.execute(db_change("select data from user_set where name = ?"), [ip_check()])
        if curs.fetchall():
            curs.execute(db_change("insert into user_set (name, id, data) values (?, ?, ?)"), ["email", ip_check(), users_email])
            curs.execute(db_change("insert into user_set (name, id, data) values  (?, ?, ?)"), ["google_name", ip_check(), users_name])
            conn.commit()
    else:
        return custom_route.custom_re_error("/custom/인증된 계정이 아닙니다.")

    return redirect("/login/register/google/register")