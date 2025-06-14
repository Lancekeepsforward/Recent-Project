# 导入必要的库和模块
from flask import Flask, render_template, request, redirect, url_for, flash  # Flask核心功能及模板渲染等工具
# Flask-SQLAlchemy 是 Flask 的一个扩展，主要用于简化在 Flask 应用中与数据库的交互操作。
# 它提供了一个高级的 ORM（对象关系映射）接口，允许开发者使用 Python 类和对象来表示数据库表和记录，
# 而无需编写复杂的 SQL 语句。通过它可以方便地进行数据库的创建、查询、插入、更新和删除等操作。
from flask_sqlalchemy import SQLAlchemy  

# Flask-Login 是 Flask 的一个用户认证扩展，用于处理用户的登录、登出和会话管理。
# LoginManager 是该扩展的核心类，负责管理整个应用的用户认证流程；
# UserMixin 是一个帮助类，为用户模型提供了一些默认的实现方法，如 is_authenticated、is_active 等；
# login_user 函数用于将用户登录到应用中；
# login_required 装饰器用于保护某些路由，只有登录用户才能访问；
# logout_user 函数用于将用户从应用中登出；
# current_user 是一个代理对象，在视图函数中可以方便地获取当前登录的用户。
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash  # 密码哈希处理工具
from datetime import datetime, timezone, timedelta  # 时间处理模块
import os  # 操作系统相关功能
# 导入dotenv库中的load_dotenv函数，该函数用于从.env文件中加载环境变量。
# 在开发和部署过程中，我们常常需要将敏感信息（如数据库密码、API密钥等）存储在环境变量中，
# 而不是直接写在代码里，这样可以提高代码的安全性。使用load_dotenv函数，
# 我们可以方便地从项目根目录下的.env文件中读取这些环境变量，
# 并将它们添加到Python的os.environ字典中，以便后续代码可以通过os.getenv()方法获取这些变量的值。
from dotenv import load_dotenv  # 加载环境变量的工具
import pymysql  # 添加PyMySQL导入
import pytz

# 这段代码的作用是将PyMySQL注册为MySQLdb的替代。在一些旧的Python库或框架中，可能会使用MySQLdb来连接MySQL数据库，
# 但MySQLdb对Python 3的支持有限，而PyMySQL是一个纯Python实现的MySQL客户端，兼容MySQLdb的API。
# 通过调用pymysql.install_as_MySQLdb()，可以让这些旧的库或框架在使用MySQLdb时，实际上使用PyMySQL来完成数据库连接操作。
pymysql.install_as_MySQLdb()

# 是的，调用 load_dotenv() 函数后，.env 文件里的变量和值会被加载到 Python 的环境变量中，
# 后续可以通过 os.getenv() 方法获取这些变量的值。
load_dotenv()

# 初始化Flask应用
app = Flask(__name__)

# 应用配置
# app.config['SECRET_KEY'] 通常是一个字符串类型的数据。
# 它在 Flask 应用中主要用于会话签名，确保会话数据在客户端和服务器之间传输时的完整性和安全性。
# 会话数据会被加密存储在客户端的 cookie 中，SECRET_KEY 就是用于加密和解密这些数据的密钥。
# 如果密钥泄露，攻击者可能会篡改会话数据，造成安全风险。
# os.getenv('SECRET_KEY', 'P@ssw0rd!Tr@v3lH^b789') 会尝试从环境变量中获取名为 'SECRET_KEY' 的值。
# 如果环境变量中存在 'SECRET_KEY'，则返回该环境变量的值，类型为字符串；
# 如果环境变量中不存在 'SECRET_KEY'，则返回默认值 'P@ssw0rd!Tr@v3lH^b789'，这也是一个字符串。
# 它不会进行变量拼接，只是简单地返回环境变量值或默认值。
# os.getenv() 函数用于从环境变量中获取指定名称的值。
# 第一个参数 'SECRET_KEY' 是要查找的环境变量名。
# 第二个参数 'P@ssw0rd!Tr@v3lH^b789' 是当环境变量中不存在该名称时返回的默认值。
# 这里将获取到的值赋给 Flask 应用配置中的 'SECRET_KEY'，用于会话签名。
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # 用于会话签名的密钥，优先从环境变量获取

# 数据库配置
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD') 
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

# 构建数据库URI
# 'SQLALCHEMY_DATABASE_URI' 名字不建议更改，格式有讲究，它遵循数据库连接 URI 的通用格式：
# dialect+driver://username:password@host:port/database
# 这里的 dialect 是数据库类型（如 mysql），driver 是使用的驱动（如 pymysql），
# 后面依次是用户名、密码、主机地址、端口（默认可省略）和数据库名。
# 该配置不是固定的，可根据使用的数据库类型和驱动进行修改。
# 例如，如果使用 PostgreSQL 数据库，可改为 'postgresql+psycopg2://...'。

# 构建数据库 URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
# 关闭 SQLAlchemy 的修改跟踪（减少内存消耗）
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库实例
db = SQLAlchemy(app)

# 初始化登录管理器（用于用户会话管理）
# 第一步：创建 LoginManager 实例
# LoginManager 是 Flask-Login 扩展中的核心类，用于管理整个应用的用户认证流程。
# 通过创建这个实例，我们可以使用 Flask-Login 提供的各种功能，如用户登录、登出、会话管理等。
login_manager = LoginManager()

# 第二步：将 LoginManager 实例与 Flask 应用进行绑定
# init_app 方法是 LoginManager 类提供的一个方法，用于将 LoginManager 实例与指定的 Flask 应用关联起来。
# 这样，Flask-Login 就能在该应用中正常工作，处理用户的认证相关事务。
login_manager.init_app(app)

# 第三步：设置未登录用户重定向的登录路由
# login_view 属性用于指定当一个未登录的用户尝试访问需要登录才能访问的路由时，
# 系统应该将其重定向到哪个路由。这里将其设置为 'login'，意味着未登录用户会被重定向到名为 'login' 的路由。
login_manager.login_view = 'login'  # 指定未登录用户重定向的登录路由

eastern = pytz.timezone('US/Eastern')
# 数据库模型定义
class User(UserMixin, db.Model):  # 用户模型，继承UserMixin（提供登录所需的默认方法）和db.Model（数据库模型基类）
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键（自动递增）
    username = db.Column(db.String(80), unique=True, nullable=False)  # 用户名（唯一且非空）
    nickname = db.Column(db.String(80), nullable=False)  # 昵称（非空)
    password_hash = db.Column(db.String(128))  # 密码哈希值（存储加密后的密码）
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(eastern))  # 用户创建时间（默认美东时间）
    # 定义了一个名为 resorts 的关系属性，用于表示用户和度假村评价之间的一对多关系
    # db.relationship() 是 SQLAlchemy 提供的关系映射函数，用于定义表之间的关联
    # 第一个参数 'UserResort' 指定了关联的目标模型类名
    # backref='user' 会在 UserResort 模型中自动创建一个 user 属性，可以通过 user_resort.user 反向访问对应的用户
    # lazy=True 表示采用延迟加载策略，只有在实际访问 resorts 属性时才会从数据库加载数据，可以提高性能
    # 
    # 这种关系映射相当于在原始 SQL 中的:
    # SELECT * FROM user_resort WHERE user_id = <当前用户id>
    # 但使用 SQLAlchemy 的方式更加面向对象，例如:
    # user.resorts 可以获取该用户的所有度假村评价
    # 或者 user_resort.user 可以获取某个评价对应的用户
    resorts = db.relationship('UserResort', backref='user', lazy=True)

class Resort(db.Model):  # 度假村模型
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键
    country = db.Column(db.String(100), nullable=False)  # 国家（非空）
    state = db.Column(db.String(100))  # 州/省（可选）
    city = db.Column(db.String(100))  # 城市（可选）
    county = db.Column(db.String(100))  # 县（可选）
    resort_name = db.Column(db.String(200), nullable=False)  # 度假村名称（非空）
    picture_local_address = db.Column(db.String(500))  # 图片本地存储路径（可选）
    # 度假村类型（枚举类型，限制可选值）
    resort_type = db.Column(db.Enum('Beach', 'Mountain', 'Spa', 'Adventure', 'Cultural', 'Urban', 'Rural', 'Luxury', 'Budget', 'Family',
                                    'Desert', 'Forest', 'Island', 'Lake', 'River', 'Valley', 'Volcano', 'Waterfall', 'Cave', 'Coast',
                                    'Safari', 'Ski', 'Golf', 'Wine', 'Wellness', 'Yoga', 'Fishing', 'Hunting', 'Cycling', 'Hiking',
                                    'Surfing', 'Diving', 'Sailing', 'Kayaking', 'Camping', 'Glamping', 'Eco', 'Sustainable', 'Historic', 'Heritage',
                                    'Art', 'Music', 'Food', 'Shopping', 'Nightlife', 'Romantic', 'Solo', 'Group', 'Accessible', 'PetFriendly'), nullable=False)
    user_resorts = db.relationship('UserResort', backref='resort', lazy=True)  # 与UserResort的一对多关系（被收藏的记录）

class UserResort(db.Model):  # 用户-度假村关联模型（记录用户对度假村的评价）
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 用户ID（外键关联User表）
    resort_id = db.Column(db.Integer, db.ForeignKey('resort.id'), nullable=False)  # 度假村ID（外键关联Resort表）
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(eastern))  # 记录创建时间（默认美东时间））
    recommendation = db.Column(db.Integer)  # 推荐指数（可选数值）
    expenditure = db.Column(db.Float)  # 消费金额（可选浮点数）
    comment = db.Column(db.Text)  # 评论内容（可选长文本）

# 登录管理器的用户加载回调函数（用于从用户ID获取用户对象）
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # 通过ID查询用户（返回User对象或None）

# 路由定义
@app.route('/')
def home():
    # 查询逻辑：获取平均推荐分最高的度假村
    # 使用SQLAlchemy的聚合函数计算每个度假村的平均推荐分，并按降序排序
    resorts = db.session.query(
        Resort,
        db.func.avg(UserResort.recommendation).label('avg_score')  # 计算平均推荐分并别名
    ).join(UserResort).group_by(Resort.id).order_by(db.desc('avg_score')).all()
    return render_template('home.html', resorts=resorts)  # 渲染主页模板并传递度假村数据

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # 处理POST请求（表单提交）
        username = request.form.get('username')  # 获取表单中的用户名
        password = request.form.get('password')  # 获取表单中的密码
        user = User.query.filter_by(username=username).first()  # 根据用户名查询用户

        # 验证用户存在且密码正确
        if user and check_password_hash(user.password_hash, password):
            login_user(user)  # 登录用户（设置会话）
            return redirect(url_for('home'))  # 重定向到主页
        flash('Invalid username or password')  # 验证失败时显示错误提示
    return render_template('login.html')  # 渲染登录页面（GET请求或验证失败时）

@app.route('/logout')
@login_required  # 需要登录才能访问的路由
def logout():
    logout_user()  # 登出用户（清除会话）
    return redirect(url_for('home'))  # 重定向到主页

@app.route('/profile')
@login_required  # 需要登录才能访问的路由
def profile():
    return render_template('profile.html')  # 渲染个人资料页面

# 启动应用（仅当直接运行此脚本时执行）
# 在数据库配置后添加以下代码
from sqlalchemy import exc

# 新增数据库配置模块
class DatabaseConfig:
    @staticmethod
    def initialize():
        # 合并原app.py和setup_db.py的初始化逻辑
        def initialize_database():
            try:
                with app.app_context():
                    db.create_all()
                    # 添加示例数据
                    if not User.query.first():
                        admin = User(username='admin', password_hash=generate_password_hash('admin123'))
                        db.session.add(admin)
                        db.session.commit()
            except exc.OperationalError as e:
                print(f"数据库连接失败: {str(e)}")
            except Exception as e:
                print(f"初始化错误: {str(e)}")

# 在if __name__ == '__main__':块中调用
if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)