from flask import Blueprint,render_template,request
import sqlite3
import json
import requests

chat = Blueprint('chat',__name__,static_folder='static', template_folder='templates')

chat.route('/chat', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect('travel.db')
    c = conn.cursor()

    c.execute("SELECT * FROM travel_guide ORDER BY RANDOM() LIMIT 3")
    guides = c.fetchall()

    conn.close()

    return render_template('index.html', guides=guides)


chat.route('/submit',methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        render_template('chat.html')
    elif request.method == 'POST':
        title = request.form.get('title')
        location = request.form.get('location')
        description = request.form.get('description')
        image = request.form.get('image')

        coon = sqlite3.connect('travel.db')
        c = coon.cursor()
        c.execute("INSERT INTO travel_guide(title,location,description,image) VALUES(?,?,?,?)",(title,location,description,image))

        coon.commit()
        coon.close()
        messages = "发布成功！"
        return render_template('submit.html',message=message)
    return render_template('chat.html')