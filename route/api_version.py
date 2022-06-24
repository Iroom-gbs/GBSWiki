from .tool.func import *

def api_version_2(conn, r_ver, c_ver):
    curs = conn.cursor()

    n_ver = ''
    data = None

    curs.execute(db_change('select data from other where name = "update"'))
    up_data = curs.fetchall()
    up_data = up_data[0][0] if up_data and up_data[0][0] in ['stable', 'beta', 'dev'] else 'stable'

    try:
        data = urllib.request.urlopen('https://raw.githubusercontent.com/2du/openNAMU/beta/version.json')
    except:
        data = None

    if data and data.getcode() == 200:
        try:
            json_data = json.loads(data.read().decode())
            if up_data in json_data:
                n_ver = json_data[up_data]['r_ver']
        except:
            pass

    json_data = { "version" : r_ver, "db_version" : c_ver, "lastest_version" : n_ver  }

    return flask.jsonify(json_data)