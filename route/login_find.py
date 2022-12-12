from .tool.func import *

def login_find():
    return easy_minify(flask.render_template(skin_check(),
        imp = ["ID/PW 찾기", wiki_set(), wiki_custom(), wiki_css([0, 0])],
        data = '''
            <ul class="inside_ul">
                <li><a href="/login/find/email">이메일로 PW 찾기</a></li>
                <li><a href="/login/find/key">키로 PW 찾기</a></li>
                <li><a href="/login/find/id">ID 찾기</a></li>
            </ul>
        ''',
        menu = [['user', load_lang('return')]]
    ))