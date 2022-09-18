from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_restplus import Api, Resource, fields, reqparse
import pandas as pd
from io import BytesIO
import xlwt

import config

app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)

api = Api(app, version='1.0', title='新手村项目', description='教师-学生选课系统', )

ns = api.namespace('student', description='table of student')  # 模块命名空间

todo = api.model('Student', {  # 返回值模型
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details')
})

parser = reqparse.RequestParser()  # 参数模型
parser.add_argument('stu_Name', type=str, required=True, help="姓名")
parser.add_argument('Age', type=int, required=True, help="年龄")
parser.add_argument('Gender', type=str, required=True, help="性别")
parser.add_argument('Grade', type=str, required=True, help="年级")
parser.add_argument('stu_cla', type=int, required=True, help="班级")


class TodoDAO(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params = parser.parse_args()

    @ns.expect(parser)  # 用于解析对应文档参数，
    @ns.response(200, "success response", todo)  # 对应解析文档返回值
    def post(self):
        data = self.params
        inf = Students(stu_Name=data['stu_Name'], Age=int(data['Age']), Gender=data['Gender'], Grade=data['Grade'],
                       stu_cla=data['stu_cla'])
        db.session.add(inf)
        db.session.commit()
        return self.params


ns.add_resource(TodoDAO, "/add", endpoint="to_do")


class Students(db.Model):
    __tablename__ = "students"  # 表名称
    stu_id = db.Column(db.Integer, primary_key=True,
                       autoincrement=True)  # Column列，Integer整型，primary_key首键，autoincrement自动增长
    stu_Name = db.Column(db.String(200), nullable=False)  # String字符串，nullable是否能为空
    Age = db.Column(db.Integer, nullable=False)
    Gender = db.Column(db.String(200), nullable=False)
    Grade = db.Column(db.String(200), nullable=False)
    stu_cla = db.Column(db.Integer, db.ForeignKey('class.cla_id'))
    stu_sco = db.relationship("Score", backref="score")

    def to_dict(self):
        return {
            "id": self.stu_id,
            "name": self.stu_Name,
            "age": self.Age,
            "gender": self.Gender,
            "grade": self.Grade,
            "stu_cla": self.stu_cla,
        }


class Classes(db.Model):
    __tablename__ = "class"  # 表名称
    cla_id = db.Column(db.Integer, primary_key=True,
                       autoincrement=True)  # Column列，Integer整型，primary_key首键，autoincrement自动增长
    cla_Name = db.Column(db.String(200), nullable=False)  # String字符串，nullable是否能为空
    cla = db.relationship("Students", backref="class")

    def to_dict(self):
        return {
            "id": self.cla_id,
            "class": self.cla_Name,
        }


class Teachers(db.Model):
    __tablename__ = "teachers"  # 表名称
    tea_id = db.Column(db.Integer, primary_key=True,
                       autoincrement=True)  # Column列，Integer整型，primary_key首键，autoincrement自动增长
    tea_Name = db.Column(db.String(200), nullable=False)  # String字符串，nullable是否能为空
    Age = db.Column(db.Integer, nullable=False)
    Gender = db.Column(db.String(200), nullable=False)
    Subject = db.Column(db.String(200), nullable=False)
    tea = db.relationship("Courses", backref="subjects")

    def to_dict(self):
        return {
            "id": self.tea_id,
            "name": self.tea_Name,
            "age": self.Age,
            "gender": self.Gender,
            "subject": self.Subject,
        }


class Courses(db.Model):
    __tablename__ = "courses"  # 表名称
    cou_id = db.Column(db.Integer, primary_key=True,
                       autoincrement=True)  # Column列，Integer整型，primary_key首键，autoincrement自动增长
    cou_Name = db.Column(db.String(200), nullable=False)  # String字符串，nullable是否能为空
    cou_tea = db.Column(db.Integer, db.ForeignKey('teachers.tea_id'))

    def to_dict(self):
        return {
            "id": self.cou_id,
            "name": self.cou_Name,
            "cou_tea": self.cou_tea,
        }


class Score(db.Model):
    __tablename__ = "score"  # 表名称
    sco_id = db.Column(db.Integer, primary_key=True,
                       autoincrement=True)  # Column列，Integer整型，primary_key首键，autoincrement自动增长
    stu_id = db.Column(db.Integer, db.ForeignKey('students.stu_id'))
    cou_id = db.Column(db.Integer, db.ForeignKey('courses.cou_id'))
    cou_sco = db.Column(db.Integer, nullable=False)
    cou = db.relationship("Courses", foreign_keys=cou_id)

    def to_dict(self):
        return {
            "id": self.sco_id,
            "stu": self.stu_id,
            "cou_id": self.cou_id,
            "cou_sco": self.cou_sco,
        }


# db.drop_all()
db.create_all()


@app.route('/student/add', methods=['POST'])
def add_student():
    data = request.get_json()
    inf = Students(stu_Name=data['stu_Name'], Age=int(data['Age']), Gender=data['Gender'], Grade=data['Grade'],
                   stu_cla=data['stu_cla'])
    db.session.add(inf)
    db.session.commit()
    return jsonify({'message': 'add success', 'student': inf})


@app.route('/student/search', methods=['GET'])
def search_student():
    get_student = Students.query.all()
    students = []
    for item in get_student:
        students.append(item.to_dict())
    return jsonify({'message': 'get success', 'student': students})


@app.route('/student/<id>', methods=['PUT'])
def update_student_by_id(id):
    data = request.get_json()
    get_student = Students.query.get(id)
    if data.get('stu_Name'):
        get_student.stu_Name = data['stu_Name']
    if data.get('Age'):
        get_student.Age = data['Age']
    if data.get('Gender'):
        get_student.Gender = data['Gender']
    if data.get('Grade'):
        get_student.Grade = data['Grade']
    if data.get('stu_cla'):
        get_student.stu_cla = data['stu_cla']
    db.session.add(get_student)
    db.session.commit()
    return 'change success'


@app.route('/student/<id>', methods=['DELETE'])
def delete_student_by_id(id):
    get_student = Students.query.get(id)
    db.session.delete(get_student)
    db.session.commit()
    return 'delete success'


@app.route('/teacher/add', methods=['POST'])
def add_teacher():
    data = request.get_json()
    inf = Teachers(tea_Name=data['tea_Name'], Age=int(data['Age']), Gender=data['Gender'], Subject=data['Subject'])
    db.session.add(inf)
    db.session.commit()
    return 'add success'


@app.route('/teacher/search', methods=['GET'])
def search_teacher():
    get_teacher = Teachers.query.all()
    teachers = []
    for item in get_teacher:
        teachers.append(item.to_dict())
    return jsonify(teachers)


@app.route('/teacher/<id>', methods=['PUT'])
def update_teacher_by_id(id):
    data = request.get_json()
    get_teacher = Teachers.query.get(id)
    if data.get('tea_Name'):
        get_teacher.stu_Name = data['tea_Name']
    if data.get('Age'):
        get_teacher.Age = data['Age']
    if data.get('Gender'):
        get_teacher.Gender = data['Gender']
    if data.get('Subject'):
        get_teacher.Subject = data['Subject']
    db.session.add(get_teacher)
    db.session.commit()
    return 'change success'


@app.route('/teacher/<id>', methods=['DELETE'])
def delete_teacher_by_id(id):
    get_teacher = Teachers.query.get(id)
    db.session.delete(get_teacher)
    db.session.commit()
    return 'delete success'


@app.route('/course/add', methods=['POST'])
def add_course():
    data = request.get_json()
    inf = Courses(cou_Name=data['cou_Name'], cou_tea=data['cou_tea'])
    db.session.add(inf)
    db.session.commit()
    return 'add success'


@app.route('/course/search', methods=['GET'])
def search_course():
    get_course = Courses.query.all()
    courses = []
    for item in get_course:
        courses.append(item.to_dict())
    return jsonify(courses)


@app.route('/course/<id>', methods=['PUT'])
def update_course_by_id(id):
    data = request.get_json()
    get_course = Courses.query.get(id)
    if data.get('cou_Name'):
        get_course.cou_Name = data['cou_Name']
    if data.get('cou_tea'):
        get_course.cou_tea = data['cou_tea']
    db.session.add(get_course)
    db.session.commit()
    return 'change success'


@app.route('/course/<id>', methods=['DELETE'])
def delete_course_by_id(id):
    get_course = Courses.query.get(id)
    db.session.delete(get_course)
    db.session.commit()
    return 'delete success'


@app.route('/class/add', methods=['POST'])
def add_class():
    data = request.get_json()
    inf = Classes(cla_Name=data['cla_Name'])
    db.session.add(inf)
    db.session.commit()
    return 'add success'


@app.route('/class/search', methods=['GET'])
def search_class():
    get_class = Classes.query.all()
    classes = []
    for item in get_class:
        classes.append(item.to_dict())
    return jsonify(classes)


@app.route('/class/<id>', methods=['PUT'])
def update_class_by_id(id):
    data = request.get_json()
    get_class = Classes.query.get(id)
    if data.get('cla_Name'):
        get_class.cla_Name = data['cla_Name']
    if data.get('cla_stu'):
        get_class.cla_stu = data['cla_stu']
    db.session.add(get_class)
    db.session.commit()
    return 'change success'


@app.route('/class/<id>', methods=['DELETE'])
def delete_class_by_id(id):
    get_class = Classes.query.get(id)
    db.session.delete(get_class)
    db.session.commit()
    return 'delete success'


@app.route('/score/add', methods=['POST'])
def add_score():
    data = request.get_json()
    inf = Score(stu_id=data['stu_id'], cou_id=data['cou_id'], cou_sco=data['cou_sco'])
    db.session.add(inf)
    db.session.commit()
    return 'add success'


@app.route('/score/search', methods=['GET'])
def search_score():
    get_score = Score.query.all()
    score = []
    for item in get_score:
        score.append(item.to_dict())
    return jsonify(score)


@app.route('/score/<id>', methods=['PUT'])
def update_score_by_id(id):
    data = request.get_json()
    get_score = Score.query.get(id)
    if data.get('stu_id'):
        get_score.stu_id = data['stu_id']
    if data.get('cou_id'):
        get_score.cou1_id = data['cou_id']
    if data.get('cou_sco'):
        get_score.cou1_sco = data['cou_sco']

    db.session.add(get_score)
    db.session.commit()
    return 'change success'


@app.route('/score/<id>', methods=['DELETE'])
def delete_score_by_id(id):
    get_score = Score.query.get(id)
    db.session.delete(get_score)
    db.session.commit()
    return 'delete success'


@app.route('/task1/<id>', methods=['GET'])
def task1(id):
    get_subject = Teachers.query.filter(Teachers.tea_id == id).all()
    a = []
    for item in get_subject:
        a.append(item.to_dict())
    get_score = Score.query.join(Courses).join(Teachers).filter(Courses.cou_tea == Teachers.tea_id,
                                                                Courses.cou_id == Score.cou_id).filter(
        Teachers.tea_id == id).all()
    message = []
    for item in get_score:
        message.append(item.to_dict())
    b = len(message)
    c = 0
    for i in message:
        c = c + i['cou_sco']
    d = c / b
    return jsonify({'教师信息': a, "选修该课程学生人数": b, '学生总分': c, '学生平均分': d})


@app.route('/task2/<id>', methods=['GET'])
def task2(id):
    get_course = db.session.query(Score).join(Students).filter(
        Students.stu_cla == id).filter(
        Score.stu_id == Students.stu_id).all()
    message = []
    for item in get_course:
        message.append(item.to_dict())
    return jsonify(message)


@app.route('/task3/<id1>/<id2>', methods=['GET'])
def task3(id1, id2):
    get_student = db.session.query(Score).join(Students).filter(
        Students.stu_cla == id1).filter(
        Score.cou_id == id2).filter(
        Score.stu_id == Students.stu_id).all()
    message = []
    for item in get_student:
        message.append(item.to_dict())
    return jsonify(message)


@app.route('/score_to_execl', methods=['GET'])
def to_execl():
    get_score = Score.query.all()
    message = []
    for item in get_score:
        message.append(item.to_dict())
    message_pro = []
    for i in range(0, len(message)):
        if not message_pro:
            message_pro.append(message[i])
        sentinel = 0
        for a in range(0, len(message_pro)):
            if message[i]['stu'] != message_pro[a]['stu']:
                sentinel = sentinel + 1
            if sentinel == len(message_pro):
                message_pro.append(message[i])
    for i in range(0, len(message_pro)):
        for a in range(0, len(message)):
            if message_pro[i]['stu'] == message[a]['stu']:
                global b
                if message_pro[i]['id'] == message[a]['id']:
                    b = 0
                if message_pro[i]['id'] != message[a]['id']:
                    b = b + 1
                    message_pro[i].update({"cou" + str(b) + "id": message[a]['cou_id']})
                    message_pro[i].update({"cou" + str(b) + "sco": message[a]['cou_sco']})
    for i in range(0, len(message_pro)):
        a = message_pro[i]['cou_sco'] + message_pro[i]['cou1sco'] + message_pro[i]['cou2sco']
        message_pro[i].update({"sum": a})
    message_pro.sort(key=lambda k: (k.get('sum', 0)), reverse=True)
    for i in range(0, len(message_pro)):
        message_pro[i].update({"ranking": i + 1})
    fields = ['学生序号', '语文', '数学', '英语', '总分', '名次']  # 设置自己需要的Excel表头

    book = xlwt.Workbook(encoding='utf-8')  # 获取excel对象

    sheet = book.add_sheet('成绩表')  # 设置excel的sheet名称

    for col, field in enumerate(fields):  # 写入excel表头
        sheet.write(0, col, field)

    row = 1
    for data in message_pro:  # 根据数据写入excel，col-单元格行标，field-单元格列标
        for col, field in enumerate(data):
            sheet.write(row, col, field)
        row += 1
    sio = BytesIO()
    book.save(sio)  # 将数据存储为bytes
    sio.seek(0)
    response = make_response(sio.getvalue())
    response.headers['Content-type'] = 'application/vnd.ms-excel'  # 响应头告诉浏览器发送的文件类型为excel
    response.headers['Content-Disposition'] = 'attachment; filename=data.xlsx'  # 浏览器打开/保存的对话框，data.xlsx-设定的文件名
    return response
    # # 将字典列表转换为DataFrame
    # pf = pd.DataFrame(list(message_pro))
    # # 指定字段顺序
    # order = ['stu', 'cou_sco', 'cou1sco', 'cou2sco', 'sum', 'ranking']
    # pf = pf[order]
    # # 将列名替换为中文
    # columns_map = {
    #     'stu': '学生序号',
    #     'cou_sco': '语文',
    #     'cou1sco': '数学',
    #     'cou2sco': '英语',
    #     'sum': '总分',
    #     'ranking': '名次'
    # }
    # pf.rename(columns=columns_map, inplace=True)
    # 指定生成的Excel表格名称
    # file_path = pd.ExcelWriter('成绩单.xlsx')
    # # 替换空单元格
    # pf.fillna(' ', inplace=True)
    # # 输出
    # pf.to_excel(file_path, encoding='utf-8', index=False)
    # # 保存表格
    # # file_path.save()
    #
    # return jsonify(message_pro)


if __name__ == '__main__':
    app.run()
