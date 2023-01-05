from .tool.func import *


def ex_user_info_2(conn):
    curs = conn.cursor()
    token = flask.request.form.get('token', '')
    client_id = flask.request.form.get('client_id', '')

    if not token or not client_id:
        return 'Error: no token or client', 400

    curs.execute(db_change('select user, scope, expire from OAuth2_Token where access_token = ? and client_id = ?'), [token, client_id])
    data = curs.fetchall()
    if not data:
        return 'Error: token not found', 403
    data = data[0]

    if datetime.datetime.strptime(data[2], '%Y-%m-%d %H:%M:%S') < datetime.datetime.today():
        return 'Error: token expired', 403

    curs.execute(db_change('select data from user_set where id = ? and name = "acl"'), [data[0]])
    acl = curs.fetchall()[0][0]
    curs.execute(db_change('select data from user_set where id = ? and name = "email"'), [data[0]])
    email = curs.fetchall()[0][0]

    if data[1] == 'id':
        return {
            'id': data[0],
            'acl': acl
        }
    elif data[1] == 'id_email':
        return {
            'id': data[0],
            'email': email,
            'acl': acl
        }