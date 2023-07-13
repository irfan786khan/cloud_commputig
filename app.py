from flask import Flask, render_template, request, jsonify, session, redirect
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


def create_tables():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()


def create_user(username, password):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()


def get_user(username):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user


def add_task(user_id, task_name):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (user_id, name) VALUES (?, ?)', (user_id, task_name))
    conn.commit()
    conn.close()


def fetch_tasks(user_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,))
    tasks = [{'id': row[0], 'name': row[2]} for row in cursor.fetchall()]
    conn.close()
    return tasks


def update_task(task_id, task_name):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET name = ? WHERE id = ?', (task_name, task_id))
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()


@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html')
    return redirect('/login')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if get_user(username):
            return jsonify({'message': 'Username already exists'})

        create_user(username, password)
        return redirect('/login')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)

        if not user or user[2] != password:
            return jsonify({'message': 'Invalid username or password'})

        session['username'] = username
        return redirect('/')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


@app.route('/api/tasks', methods=['POST'])
def create_task():
    if 'username' not in session:
        return jsonify({'message': 'User not logged in'})

    task_name = request.json['name']
    user = get_user(session['username'])
    add_task(user[0], task_name)
    return jsonify({'message': 'Task created successfully'})


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    if 'username' not in session:
        return jsonify({'message': 'User not logged in'})

    user = get_user(session['username'])
    tasks = fetch_tasks(user[0])
    return jsonify(tasks)


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task_route(task_id):
    if 'username' not in session:
        return jsonify({'message': 'User not logged in'})

    task_name = request.json['name']
    update_task(task_id, task_name)
    return jsonify({'message': 'Task updated successfully'})


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task_route(task_id):
    if 'username' not in session:
        return jsonify({'message': 'User not logged in'})

    delete_task(task_id)
    return jsonify({'message': 'Task deleted successfully'})


if __name__ == '__main__':
    create_tables()
    app.run()
