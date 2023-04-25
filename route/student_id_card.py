from route.tool.func import *

def student_id_card_2(conn):
    if ip_or_user() == 1:
        return re_error('/error/3')
    return easy_minify(flask.render_template(skin_check(),
        imp=["학생증", wiki_set(), wiki_custom(), wiki_css([0, 0])],
        data='''<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/jsbarcode/3.3.20/JsBarcode.all.min.js"></script>
    <link href="https://hangeul.pstatic.net/hangeul_static/css/nanum-gothic.css" rel="stylesheet">
    이름: <input type="text" id="name_input"><br>
    학번: <input type="text" id="student_id_input" maxlength="4"><br>
    도서대출증 번호: <input type="text" id="lib_id" onfocusout="generate_id_card()"><br>
    <a href="https://docs.google.com/spreadsheets/d/1qyk3eju4K-JwvkoOQfTPEuyCuns2ZFMu-oh7vqJH5xs">도서대출증 번호 찾기</a>
    <br><br>
    <div style="background-color: #f0fafc;background-image: url(https://gbs.wiki/image/b6d60d561a0165f501455fbd9f26a0fb2ee0c893c6697a25e7dc86a8.png);background-size: 360px;background-position-y: center;background-repeat: no-repeat;text-align: center;height: 600px;width: 366px">
        <div style="background-color: #2b52bb;height: 70px;font-size: 12px;color: #ffffff">
            <div style="height: 8px"></div>
            <div style="margin-left: 8px;margin-right: 8px;border: solid black;border-width: 2px 2px 0 2px;border-top-left-radius: 3px;border-top-right-radius: 3px">
                <br>
                <b style="font-size: 30px;font-family: 'NanumGothic';">디지털 학생증</b>
            </div>
        </div>
        <div style="margin: 0 8px 8px 8px;border: solid black;border-width: 0 2px 2px 2px;border-radius: 0 0 3px 3px">
            <br>
            <div style="width: 200px;height: 205px;margin: auto;">
                <img src="https://gbs.wiki/image/7d81c607d24e007aa9fff0170f47bcac39f6d4c831fd8d6b5915d461.png">
            </div><br>
            <b><p id="name" style="font-size: 24px;font-family: 'NanumGothic'">이름</p></b>
            <svg id="code128"></svg>
            <i style="text-align: center;font-size: 9px"><br>
                ※ 이 학생증은 각종 증명/증빙 제출 목적으로 사용할 수 없습니다.</i>
            <img src="	https://gbs-h.goeujb.kr/upload/gbs-h/logo/img_99fe7219-b3e5-407b-a374-84a8e77cabbb1669080473121.png">
        </div>
    </div>
    <br>
    <script>
        function generate_id_card() {
            if(document.getElementById("name_input").value&&document.getElementById("student_id_input"))
                $("p").html(document.getElementById("student_id_input").value + "<br><br>" + document.getElementById("name_input").value);
            else alert("이름과 학번을 입력하세요.")
            JsBarcode("#code128", document.getElementById("lib_id").value, {
                format: "CODE128",
                lineColor: "#000",
                width: 2,
                height: 60,
                displayValue: true,
                background: "#f0fafc",
            });
        }

    </script>
        ''',
        menu=[['manager', load_lang('return')]]
        ))
