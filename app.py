from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'troque_essa_chave_por_uma_segura_e_randomica'  # obrigatório para sessão

# Configurações de upload
UPLOAD_FOLDER = '/tmp/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_db_connection():
    conn = sqlite3.connect('/tmp/posts.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
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

# Usuário e senha fixos do admin (mude como quiser)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'senha123'

# Decorator para proteger rotas
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Faça login para acessar essa página.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Login realizado com sucesso!')
            return redirect(url_for('admin'))
        else:
            flash('Usuário ou senha incorretos.')
            return redirect(url_for('login'))
    return '''
    <h2>Login Admin</h2>
    <form method="POST">
      <input name="username" placeholder="Usuário" required><br><br>
      <input name="password" type="password" placeholder="Senha" required><br><br>
      <button type="submit">Entrar</button>
    </form>
    '''

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('Você saiu da sessão.')
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin():
    return '''
    <h1>Admin - Criar Post</h1>
    <p><a href="/logout">Sair</a></p>
    <form action="/admin/create-post" method="POST" enctype="multipart/form-data">
      <input name="title" placeholder="Título" required><br><br>
      <textarea name="description" placeholder="Descrição" required></textarea><br><br>
      <input type="file" name="image"><br><br>
      <button type="submit">Criar Post</button>
    </form>
    '''

@app.route('/admin/create-post', methods=['POST'])
@login_required
def create_post():
    title = request.form.get('title')
    description = request.form.get('description')
    file = request.files.get('image')

    filename = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    if not title or not description:
        return "Título e descrição são obrigatórios.", 400

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO posts (title, description, image_filename, created_at) VALUES (?, ?, ?, ?)",
        (title, description, filename, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

    return redirect(url_for('blog'))

# Rotas públicas

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
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT title, description FROM posts ORDER BY created_at DESC')
    posts = [{'title': row['title'], 'description': row['description']} for row in c.fetchall()]
    conn.close()
    return render_template('blog.html', posts=posts)

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
