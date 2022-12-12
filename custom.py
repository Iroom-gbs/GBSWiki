from route.tool.func import *
from custom_route.tools import *
from custom_route.generate_student import *


def custom_run(conn, app):
    #학생 문서 생성
    @app.route('/generate_student', methods=['POST', 'GET'])
    def generate_student():
        return generate_student_2(conn)

    @app.route('/generate_student/request', methods=['POST', 'GET'])
    def request_generate_student():
        return request_generate_student_2(conn)

    @app.route('/generate_student/list', methods=['POST', 'GET'])
    def list_student_request():
        return list_student_request_2(conn)

    @app.route('/generate_student/accept/<everything:request_id>', methods=['POST','GET'])
    def accept_student_request(request_id):
        return accept_student_request_2(conn, request_id=request_id)

    @app.route('/generate_student/delete/<everything:request_id>', methods=['POST','GET'])
    def delete_student_request(request_id):
        return delete_student_request_2(conn, request_id=request_id)

    @app.route('/generate_student/history', methods=['GET'])
    def generate_student_history():
        return show_student_request_history_2(conn)

    @app.route('/test', methods=['GET'])
    def test_func():
        get_email(conn, "1")
        return redirect("/")