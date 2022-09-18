HOSTNAME = '127.0.0.1'  # 域名
PORT = '3306'  # 端口号
DATABASE = 'CourseChoose'  # 数据库名称
USERNAME = 'root'  # 用户名
PASSWORD = '123456'  # 密码
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
SQLALCHEMY_DATABASE_URI = DB_URI  # 配置数据库连接
SQLALCHEMY_TRACK_MODIFICATIONS = True
