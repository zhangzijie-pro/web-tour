from flask import Flask,Blueprint,render_template

location = Blueprint('recommend', __name__, static_folder='static', template_folder='templates')

@location.route('/place1', methods=['POST', 'GET'],endpoint='mountain')
def place1():
    return render_template('place1.html')
@location.route('/place2', methods=['POST', 'GET'],endpoint='culture')
def place1():
    return render_template('place2.html')
@location.route('/place3', methods=['POST', 'GET'],endpoint='history')
def place1():
    return render_template('place3.html')
@location.route('/place4', methods=['POST', 'GET'],endpoint='customs')
def place1():
    return render_template('place4.html')