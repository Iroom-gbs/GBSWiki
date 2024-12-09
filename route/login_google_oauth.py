import os

from flask import request

from custom_route.tools import *
from .tool.func import *

GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, client = get_google_oauth_client()
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


def login_google_oauth_2(conn):
    curs = conn.cursor()

    ip = ip_check()
    if ip_or_user(ip) == 0:
        return redirect('/user')

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

    if userinfo_response.json().get("email_verified"):
        if "hd" not in userinfo_response.json():
            return custom_re_error("/custom/경기북과학고등학교 계정이 아닙니다.")
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
        hd = userinfo_response.json()["hd"]
        if not (users_email.startswith("gbs.") and hd.endswith("ggh.goe.go.kr")):
            return custom_re_error("/custom/경기북과학고등학교 계정이 아닙니다.")

    curs = conn.cursor()
    curs.execute(db_change("select id from user_set where data = ? and name = 'google_uid'"), [unique_id])
    user_data = curs.fetchall()

    if user_data:
        user_id = user_data[0][0]
        flask.session['id'] = user_id
        ua_plus(user_id, get_ip(), flask.request.headers.get('User-Agent', ''), get_time())
        return redirect("/user")

    return easy_minify(flask.render_template(skin_check(),
            imp = ["가입되 계정이 없습니다.", wiki_set(), wiki_custom(), wiki_css([0, 0])],
            data = '''
            가입된 계정이 없습니다. 이미 계정이 있다면 ID로 로그인 후 계정에 연동하세요. <a href="/login"> 로그인하러 가기 </a><br>
            아직 계정이 없다면, <a href="/register">여기</a>에서 가입하세요.<br>
            ''',
            menu = [['user', load_lang('return')]]
        ))