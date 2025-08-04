from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configurações para upload (pode usar depois)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Inicializar banco SQLite (posts.db)
def init_db():
    conn = sqlite3.connect('posts.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            image_filename TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/blog')
def blog():
    conn = sqlite3.connect('posts.db')
    c = conn.cursor()
    c.execute('SELECT title, description FROM posts ORDER BY created_at DESC')
    posts = [{'title': row[0], 'description': row[1]} for row in c.fetchall()]
    conn.close()
    return render_template('blog.html', posts=posts)

@app.route('/contact')
def contact():
    return render_template('contact.html')




@app.route('/admin')
def admin():
    # Página admin simples para criar posts (não seguro, só exemplo)
    return '''
    <h1>Admin - Criar Post</h1>
    <form action="/admin/create-post" method="POST">
      <input name="title" placeholder="Título" required><br><br>
      <textarea name="description" placeholder="Descrição" required></textarea><br><br>
      <button type="submit">Criar Post</button>
    </form>
    '''

@app.route('/admin/create-post', methods=['POST'])
def create_post():
    title = request.form.get('title')
    description = request.form.get('description')

    if not title or not description:
        return "Título e descrição são obrigatórios.", 400

    conn = sqlite3.connect('posts.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO posts (title, description, created_at) VALUES (?, ?, ?)",
        (title, description, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

    return redirect(url_for('blog'))


