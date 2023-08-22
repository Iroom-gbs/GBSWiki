from .tool.func import *
from custom_route.tools import *

def user_info_2(conn, name):
    curs = conn.cursor()

    if name == '':
        ip = ip_check()
    else:
        ip = name

    login_menu = ''
    tool_menu = ''
    
    if name == '':
        curs.execute(db_change("select count(*) from alarm where name = ?"), [ip])
        count = curs.fetchall()
        if count and count[0][0] != 0:
            tool_menu += '<li><a id="not_thing" href="/alarm">' + load_lang('alarm') + ' (' + str(count[0][0]) + ')</a></li>'
        else:
            tool_menu += '<li><a href="/alarm">' + load_lang('alarm') + '</a></li>'

        if ip_or_user(ip) == 0:
            login_menu += '''
                <li><a href="/logout">''' + load_lang('logout') + '''</a></li>
                <li><a href="/change">''' + load_lang('user_setting') + '''</a></li>
                <li> <a href="/auth/google"> Google 계정 연동하기 </a> </li>
            '''

            tool_menu += '<li><a href="/watch_list">' + load_lang('watchlist') + '</a></li>'
            tool_menu += '<li><a href="/star_doc">' + load_lang('star_doc') + '</a></li>'
            tool_menu += '<li><a href="/acl/user:' + url_pas(ip) + '">' + load_lang('user_document_acl') + '</a></li>'
        else:
            login_menu += '''
                <li> SNS 로그인 <br>
                <a href="/login/google"><img src="/views/LibertyForNorth/img/google_login.png"></a> </li>
                <li> ID 로그인
                <form method="post" action="/login" >
                    <input placeholder="''' + load_lang('id') + '''" name="id" type="text">
                    <hr class="main_hr">
                    <input placeholder="''' + load_lang('password') + '''" name="pw" type="password">
                    <hr class="main_hr">
                    ''' + captcha_get() + '''
                    <button type="submit">''' + load_lang('login') + '''</button> 
                    <button type="button" onclick="location.href='/register'"> ''' + load_lang('register') + ''' </button><br>
                    <a href="/login/find">ID/PW 찾기</a>
                </form></li>
            '''
            
        tool_menu += '<li><a href="/change/head">' + load_lang('user_head') + '</a></li>'
            
        login_menu = '<h2>' + load_lang('login') + '</h2><ul class="inside_ul">' + login_menu + '</ul>'
        tool_menu = '<h2>' + load_lang('tool') + '</h2><ul class="inside_ul">' + tool_menu + '</ul>'

    if admin_check(1) == 1:
        curs.execute(db_change("select block from rb where block = ? and ongoing = '1'"), [ip])
        ban_name = load_lang('release') if curs.fetchall() else load_lang('ban')
        
        admin_menu = '''
            <h2>''' + load_lang('admin') + '''</h2>
            <ul class="inside_ul">
                <li>이메일 : ''' + get_email(conn, ip) + ''' <a href="/user/manage/email/''' + url_pas(ip) + '''">변경</a></li>
                <li>비밀번호 재설정: <a href="/user/admin/pw_set/''' + url_pas(ip) + '''">재설정하기</a></li>
                <li><a href="/ban/''' + url_pas(ip) + '''">''' + ban_name + '''</a></li>
                <li><a href="/check/''' + url_pas(ip) + '''">''' + load_lang('check') + '''</a></li>
            </ul>
        '''
    else:
        admin_menu = ''
            
    return easy_minify(flask.render_template(skin_check(),
        imp = [load_lang('user_tool'), wiki_set(), wiki_custom(), wiki_css([0, 0])],
        data = '''
            <h2>''' + load_lang('state') + '''</h2>
            <div id="get_user_info"></div>
            <script>load_user_info("''' + ip + '''");</script>
            ''' + login_menu + '''
            ''' + tool_menu + '''
            <h2>''' + load_lang('other') + '''</h2>
            <ul class="inside_ul">
                <li><a href="/record/''' + url_pas(ip) + '''">''' + load_lang('record') + '''</a></li>
                <li><a href="/record/topic/''' + url_pas(ip) + '''">''' + load_lang('discussion_record') + '''</a></li>
                <li><a href="/topic/user:''' + url_pas(ip) + '''">''' + load_lang('user_discussion') + '''</a></li>
                <li><a href="/count/''' + url_pas(ip) + '''">''' + load_lang('count') + '''</a></li>
            </ul>
            ''' + admin_menu + '''
        ''',
        menu = 0
    ))