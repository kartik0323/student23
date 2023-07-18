from flask import Flask, render_template, request, redirect, session, jsonify
from pymongo import MongoClient

from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "kartik"  # Change this to a secure key
client = MongoClient('mongodb+srv://kartikpoojary8:kartik@kartik.p9a2qyy.mongodb.net/?retryWrites=true&w=majority')
db = client['student_management_system']
students = db['students']

# Rest of the code...
# Admin Login Page
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_username = request.form['admin_username']
        admin_password = request.form['admin_password']

        # Add your admin authentication logic here
        if admin_username == 'admin' and admin_password == 'password':
            session['admin_logged_in'] = True
            return redirect('/admin/dashboard')
        else:
            error = 'Invalid username or password. Please try again.'
            return render_template('admin_login.html', error=error)

    return render_template('admin_login.html')

# Admin Dashboard
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin_logged_in' in session:
        if request.method == 'POST':
            search_term = request.form['search']

            # Perform the search query to find students by name
            students = db.students.find({'name': {'$regex': search_term, '$options': 'i'}})
            return render_template('admin_dashboard.html', students=students)
        else:
            students = db.students.find()
            return render_template('admin_dashboard.html', students=students)
    else:
        return redirect('/admin/login')

# Admin Search
@app.route('/admin/search', methods=['POST'])
def admin_search():
    if 'admin_logged_in' in session:
        search_term = request.form['search']

        # Perform the search query to find students by name
        students = db.students.find({'name': {'$regex': search_term, '$options': 'i'}})
        return render_template('admin_dashboard.html', students=students)
    else:
        return redirect('/admin/login')



@app.route('/')
def index():
    if 'username' in session:
        return redirect('/dashboard')
    else:
        return render_template('index.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_student = students.find_one({'username': username})
        if existing_student:
            return render_template('register.html', error='Username already taken')

        existing_student = students.find_one({'email': request.form['email']})
        if existing_student:
            return render_template('register.html', error='Email already registered')

        student = {
            'username': username,
            'password': password,
            'email': request.form['email'],
            'marks': {},
            'activities': [],
            'attendance': {}
        }
        students.insert_one(student)
        session['username'] = username
        return redirect('/dashboard')
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        student = students.find_one({'username': username, 'password': password})
        if student:
            session['username'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid username or password')
    else:
        return render_template('login.html')

@app.route('/api/students', methods=['GET'])
def get_students():
    student_list = []
    for student in students.find():
        student_list.append({
            'username': student['username'],
            'email': student['email'],
            'marks': student['marks'],
            'activities': student['activities'],
            'attendance': student['attendance']
        })
    return jsonify(student_list)

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        student = students.find_one({'username': username})
        return render_template('dashboard.html', student=student)
    else:
        return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
