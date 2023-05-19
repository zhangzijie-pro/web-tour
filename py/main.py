from flask import Flask, render_template, request, jsonify
import requests
import json
import sqlite3
from place import location
from search import find
from user_db import user_bp
import os

app = Flask(__name__)
DATABASE='groups.db'

# 登录界面
app.secret_key = '00978b5aa04d735470d552dc-f5e1e1041b7a-55be3f598032d6d2a780b60e5f8b'
app.register_blueprint(user_bp)


app.config['DEBUG'] = True
app.config['SECRET_KEY'] = '00978b5aa04d735470d552dc-f5e1e1041b7a-55be3f598032d6d2a780b60e5f8b'

def get_db():
    db = sqlite3.connect('group.db')
    db.row_factory = sqlite3.Row
    return db
# 旅游联盟
@app.route('/group', methods=['GET'])
def index():
    return render_template('group.html')
# 添加群组路由：渲染添加群组页面
@app.route('/add', methods=['GET'])
def add():
    return render_template('add.html')
# 添加群组路由：处理添加群组请求
@app.route('/add', methods=['POST'])
def add_group():
    group = request.form['group']
    location = request.form['location']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO groups (location, groups) VALUES ('{location}', '{group}')")
    conn.commit()
    conn.close()
    message = 'Group added successfully!'
    return render_template('add.html', message=message)
# 搜索群组路由：根据地点搜索群组
@app.route('/search_group', methods=['GET'],endpoint='group_search')
def search():
    location = request.args.get('location')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM groups WHERE location LIKE '%{location}%'")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append({'group': row['groups'], 'location': row['location']})

    return jsonify(result)


# 搜索结果库
app.register_blueprint(find)

# 论坛
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    coon = sqlite3.connect('travel.db')
    c = coon.cursor()

    c.execute("SELECT * FROM travel_guide ORDER BY RANDOM() LIMIT 3")
    guides = c.fetchall()
    coon.close()
    if guides is None:
        guides = []
        return render_template('chat.html', guides=guides)
    else:
        return render_template('chat.html', guides=guides)
    # return render_template('chat.html', guides=guides)

@app.route('/submit_index')
def submit_index():
    return render_template('submit.html')

@app.route('/submit',methods=['GET', 'POST'])
def submit_article():
    if  request.method == 'GET':
        render_template('submit.html')
    elif request.method == 'POST':
        title = request.form.get('title')
        location = request.form.get('location')
        description = request.form.get('description')
        image = request.files['image'].read()

        coon = sqlite3.connect('travel.db')
        c = coon.cursor()
        c.execute("INSERT INTO travel_guide(title,location,description,image) VALUES(?,?,?,?)",(title,location,description,image))

        coon.commit()
        coon.close()
        messages = "发布成功！"
        return render_template('submit.html',message=messages)
    return render_template('chat.html')

@app.route('/search_chat')
def search():
    # 获取查询参数
    query = request.args.get('query')
    coon = sqlite3.connect('travel.db')
    c = coon.cursor()
    # 在数据库中执行搜索操作
    results = c.execute('SELECT * FROM travel_guide WHERE title LIKE ? OR location LIKE ? OR description LIKE ?', ('%' + query + '%','%' + query + '%','%' + query + '%',)).fetchall()

    # 返回搜索结果
    return render_template('search_chat.html', results=results)


# 高德地图
@app.route('/map', methods=['GET', 'POST'])
def map():
    # 获得用户的起始地址和终点
    user_ip = request.remote_addr
    user_location = user_ip
    # 得到用户所在地

    # 获取起始地址和终点地址
    start_location = request.form.get('start_location')
    end_location = request.form.get('end_location')

    # 将起始地址和终点地址转换为经纬度坐标
    start_url = 'https://restapi.amap.com/v3/geocode/geo?key=8ee1503576799d2b4adc775624cc390d&address={}'.format(start_location)
    end_url = 'https://restapi.amap.com/v3/geocode/geo?key=8ee1503576799d2b4adc775624cc390d&address={}'.format(end_location)
    start_res = requests.get(start_url)
    end_res = requests.get(end_url)
    if start_res.status_code !=200 and end_res.status_code !=200:
        error = '请求时发生错误'
        return render_template('home.html', error=error)
    else:
        start_data = json.loads(start_res.text)
        end_data = json.loads(end_res.text)
        start_location_ip = start_data['geocodes'][0]['location']
        end_location_ip = end_data['geocodes'][0]['location']     # 得到起始点和终点的坐标

    # 获取路径规划结果
    path_plan_url = "https://restapi.amap.com/v3/direction/driving?origin={}&destination={}&extensions=all&key=8ee1503576799d2b4adc775624cc390d".format(start_location_ip, end_location_ip)
    path_plan_res = requests.get(path_plan_url)
    path_plan_data = json.loads(path_plan_res.text)
    # 路径的详细方式
    path_points = path_plan_data['route']['paths'][0]['steps']
    path=[]
    for step in path_points:
        points = step['polyline'].split(';')
        for point in points:
            path.append([float(x) for x in point.split(',')])

    # 坐标
    result = [[start_location_ip.split(',')], [end_location_ip.split(',')]]
    result_load = {'route': path}
    # 返回路径规划结果
    return render_template('map.html', result=result, user_location=user_location, result_load=result_load)


# 旅游推荐
app.register_blueprint(location)

@app.route('/warning')
def warning():
    return render_template('warning.html')


if __name__ == '__main__':
    app.run(debug=True, port=80, threaded=True)
    
os.makedirs("templates", exist_ok=True)
with open("templates/main.html", "w") as f:
    f.write(render_template("main.html"))
