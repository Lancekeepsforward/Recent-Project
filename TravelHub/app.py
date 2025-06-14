from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from dotenv import load_dotenv
from setup_db import db, User, Resort, UserResort, init_app
import uuid
from werkzeug.utils import secure_filename
import re

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initialize database and login manager
init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

UPLOAD_FOLDER = os.path.join('static', 'resort_pics')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    """
    主页路由处理函数
    查询所有度假村及其平均评分，按评分从高到低排序展示
    
    Returns:
        返回渲染后的home.html模板，传入度假村数据和对应的平均评分
    """
    # 只查询前20个 resort
    resorts = db.session.query(
        Resort,
        db.func.avg(UserResort.recommendation).label('avg_score')
    ).join(UserResort, isouter=True).group_by(Resort.id).order_by(db.desc('avg_score')).limit(20).all()
    return render_template('home.html', resorts=resorts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Login attempt - Username: {username}")
        
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User found: {user.username}")
            print(f"Password check result: {user.password == password}")
            if user.password == password:
                login_user(user)
                print("Login successful")
                # 登录成功后重定向到用户个人页面
                return redirect(url_for('profile'))
            else:
                print("Password check failed")
        else:
            print(f"No user found with username: {username}")
            
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            resort_name = request.form.get('resort_name')
            country = request.form.get('country')
            state = request.form.get('state')
            city = request.form.get('city')
            county = request.form.get('county')
            resort_type = request.form.get('resort_type')
            recommendation = request.form.get('recommendation')
            expenditure = request.form.get('expenditure')
            comment = request.form.get('comment')
            picture = request.files.get('picture')
            # 处理图片上传
            picture_path = None
            if picture and allowed_file(picture.filename):
                filename = secure_filename(str(uuid.uuid4()) + '_' + picture.filename)
                picture_save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                picture.save(picture_save_path)
                picture_path = os.path.join('resort_pics', filename)
            # 新建 Resort，指定创建者
            new_resort = Resort(
                country=country,
                state=state,
                city=city,
                county=county,
                resort_name=resort_name,
                resort_type=resort_type,
                picture_local_address=picture_path,
                creator_id=current_user.id
            )
            db.session.add(new_resort)
            db.session.commit()
            # 新建 UserResort 关联，写入评分、花销、评论
            user_resort = UserResort(
                user_id=current_user.id,
                resort_id=new_resort.id,
                recommendation=int(recommendation) if recommendation else None,
                expenditure=float(expenditure) if expenditure else None,
                comment=comment
            )
            db.session.add(user_resort)
            db.session.commit()
            flash('新度假村已提交！')
        except Exception as e:
            db.session.rollback()
            print(f"添加度假村失败: {e}")
            flash('添加度假村失败，请检查输入内容或稍后再试。')
        return redirect(url_for('profile'))
    # 只查找当前用户自己创建的度假村
    resorts = Resort.query.filter_by(creator_id=current_user.id).all()
    return render_template('profile.html', resorts=resorts)

@app.route('/debug/users')
def debug_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'is_admin': user.is_admin,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None
        })
    return {'users': result}

@app.route('/api/resorts')
def api_resorts():
    try:
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 20))
    except Exception:
        offset = 0
        limit = 20
    resorts = db.session.query(
        Resort,
        db.func.avg(UserResort.recommendation).label('avg_score')
    ).join(UserResort, isouter=True).group_by(Resort.id).order_by(db.desc('avg_score')).offset(offset).limit(limit).all()
    result = []
    for resort, avg_score in resorts:
        result.append({
            'id': resort.id,
            'resort_name': resort.resort_name,
            'country': resort.country,
            'city': resort.city,
            'picture': url_for('static', filename=resort.picture_local_address) if resort.picture_local_address else None,
            'avg_score': avg_score if avg_score is not None else '无',
            'resort_type': resort.resort_type
        })
    return jsonify(result)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        nickname = request.form.get('nickname')
        password = request.form.get('password')
        # 密码复杂度要求：8-13位，包含大写、小写、数字和特殊字符
        password_require = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,13}$'
        if not re.match(password_require, password):
            flash('密码必须为8-13位，且包含大写、小写、数字和特殊字符')
            return render_template('signup.html', username=username, nickname=nickname)
        # 检查用户名唯一
        if User.query.filter_by(username=username).first():
            flash('用户名已存在，请更换')
            return render_template('signup.html', username=username, nickname=nickname)
        # 创建新用户
        new_user = User(
            username=username,
            nickname=nickname,
            password=password,
            is_admin=False
        )
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('注册成功，请登录！')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请稍后再试')
            return render_template('signup.html', username=username, nickname=nickname)
    return render_template('signup.html')

@app.route('/resort/<int:resort_id>', methods=['GET', 'POST'])
def resort_detail(resort_id):
    resort = Resort.query.get_or_404(resort_id)
    # 查询所有与该resort相关的UserResort（评论/评分/开销），按时间倒序
    user_resorts = UserResort.query.filter_by(resort_id=resort_id).join(User).order_by(UserResort.created_at.desc()).all()
    # 计算平均分
    avg_score = None
    scores = [ur.recommendation for ur in user_resorts if ur.recommendation is not None]
    if scores:
        avg_score = round(sum(scores) / len(scores), 2)
    # 处理评论/评分/开销提交
    if request.method == 'POST' and current_user.is_authenticated:
        comment = request.form.get('comment')
        recommendation = request.form.get('recommendation')
        expenditure = request.form.get('expenditure')
        try:
            recommendation = int(recommendation) if recommendation else None
            expenditure = float(expenditure) if expenditure else None
        except Exception:
            flash('评分或开销格式不正确')
            return redirect(url_for('resort_detail', resort_id=resort_id))
        # 每次都新建一条评论记录
        user_resort = UserResort(
            user_id=current_user.id,
            resort_id=resort_id,
            comment=comment,
            recommendation=recommendation,
            expenditure=expenditure
        )
        db.session.add(user_resort)
        db.session.commit()
        flash('评论/评分已提交！')
        return redirect(url_for('resort_detail', resort_id=resort_id))
    return render_template('resort_detail.html', resort=resort, user_resorts=user_resorts, avg_score=avg_score)

if __name__ == '__main__':
    app.run(debug=True)