import os

from flask import request
from oauthlib.oauth2 import WebApplicationClient
from .tool.func import *


GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", os.environ.get("GOOGLE_CLIENT_SECRET"))
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def login_register_google_2(conn):
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

    return login()

def login():
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    return flask.redirect(client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url.replace("http:", "https:") + "/callback",
        scope=["openid", "email", "profile"],
    ))


def login_register_google_callback_2(conn):
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
        if not (users_email.startswith("gbs.") and users_email.endswith("@ggh.goe.go.kr")):
            return "You are not a student of GBSHS", 403
    else:
        return "User email not available or not verified by Google.", 400

    return redirect("/login/register/google/register")