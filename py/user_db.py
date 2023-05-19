import sqlite3
import re
from flask import session, request, render_template, redirect, url_for, g, Blueprint, abort
from flask_bcrypt import generate_password_hash, Bcrypt

# 创建蓝图
user_bp = Blueprint('user', __name__, static_folder='static', template_folder='templates')

# 连接数据库
DATABASE = 'user.db'


# 创建用户表
create_table_sql = '''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(40) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL,
    nickname VARCHAR(40),
    avatar VARCHAR(255),
    birthdate DATE,
    travel_preference TEXT,
    dream_place TEXT,
    wish_place TEXT
);
'''

# 在应用上下文中初始化数据库连接
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


# 注册函数，用来添加用户
@user_bp.route('/register', methods=['GET', 'POST'], endpoint='register')
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        birthdate = request.form.get('birthdate')

        # 密码强度校验
        if not re.search(r'[a-z]', password) or not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password):
            return '密码必须包含大小写字母和数字'
        hashed_password = generate_password_hash(password, 12)
        # 添加用户数据
        db = get_db()
        try:
            insert_user_sql = '''
            INSERT INTO user (username, password, birthdate)
            VALUES (?, ?, ?);
            '''
            db.execute(insert_user_sql, (username, password, birthdate))
            db.commit()
            x = f'{username}注册成功'
        except:
            db.rollback()
            error = '注册失败，请检查用户是否已经存在'
            return  render_template('register.html',error=error)
        return render_template('login.html', x=x)
    else:
        return render_template('register.html')


# 登录函数，用来验证用户身份
@user_bp.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 查询用户数据
        query_user_sql = '''
        SELECT COUNT(*)
        FROM user
        WHERE username = ?
        AND password = ?
        '''
        db = get_db()
        result = db.execute(query_user_sql, (username, password)).fetchone()
        count = result[0]

        # 返回验证结果
        if count == 0:
            return redirect(url_for('user.register'))
        elif count == 1:
            session['username'] = username
            return render_template('home.html')
        else:
            return render_template('login.html', error='用户名或密码错误')
    else:
        return render_template('login.html')


# 修改个人信息函数，用来更新用户数据
@user_bp.route('/personal', methods=['GET', 'POST'], endpoint='personal')
def update_info():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nickname = request.form.get('nickname')
        avatar = request.form.get('avatar')
        birthdate = request.form.get('birthdate')
        travel_preference = request.form.get('travel_preference')
        dream_place = request.form.get('dream_place')
        wish_place = request.form.get('wish_place')

        # 更新用户数据
        update_user_sql = '''
        UPDATE user
        SET nickname = ?, avatar = ?, birthdate = ?, travel_preference = ?, dream_place = ?, wish_place = ?
        WHERE username = ?
        '''
        db = get_db()
        db.execute(update_user_sql, (nickname, avatar, birthdate, travel_preference, dream_place, wish_place, username))
        db.commit()
        message = "信息修改完毕！"
        # 返回更新结果
        return render_template('personal.html', username=username,message=message)
    else:
        query_user_sql = '''
        SELECT nickname, avatar, birthdate, travel_preference, dream_place, wish_place
        FROM user
        WHERE username = ?
        '''
        db = get_db()
        result = db.execute(query_user_sql, (username,)).fetchone()

        # 将查询结果封装成字典
        if result == '':
            info = {'nickname': '', 'avatar': '', 'birthdate': '', 'travel_preference': '',
                    'dream_place': '', 'wish_place': ''}
            messages = "您还未填写信息"
        else:
            info = {'nickname': result[0], 'avatar': result[1], 'birthdate': result[2], 'travel_preference': result[3],
                    'dream_place': result[4], 'wish_place': result[5]}

        # 返回个人信息
        return render_template('personal.html', info=info, username=username,message=messages)


# 首页
@user_bp.route('/', endpoint='home_page')
def home():
    # 获取当前登录用户的用户名
    username = session.get("username")

    if username:
        # 如果用户已登录，则渲染主页模板，并传递用户名参数
        return render_template("home.html", username=username)
    else:
        # 如果用户未登录，则重定向到登录页面
        return redirect("/login")


@user_bp.route("/logout", endpoint='logout')
def logout():
    # 删除 Session 中保存的用户名
    session.pop("username", None)

    # 重定向到登录页面
    return redirect("/login")

# 关闭数据库连接
@user_bp.teardown_request
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()