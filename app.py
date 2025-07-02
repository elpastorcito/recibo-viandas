from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_cambia'  # Cambia esta clave
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = Usuario.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Acceso denegado')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_first_request
def create_tables():
    db.create_all()
    admin = Usuario.query.filter_by(username='admin').first()
    if not admin:
        admin = Usuario(username='admin', is_admin=True)
        admin.set_password('noli#0932')
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login exitoso')
            return redirect(url_for('dashboard'))
        flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if Usuario.query.filter_by(username=username).first():
            flash('Usuario ya existe')
            return redirect(url_for('register'))
        user = Usuario(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registro exitoso, logueate')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = Usuario.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/admin')
@admin_required
def admin_panel():
    usuarios = Usuario.query.all()
    return render_template('admin.html', usuarios=usuarios)

@app.route('/admin/create', methods=['GET', 'POST'])
@admin_required
def admin_create():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = 'is_admin' in request.form

        if Usuario.query.filter_by(username=username).first():
            flash('El usuario ya existe')
            return redirect(url_for('admin_create'))

        nuevo_usuario = Usuario(username=username, is_admin=is_admin)
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Usuario creado')
        return redirect(url_for('admin_panel'))
    return render_template('admin_create.html')

@app.route('/admin/delete/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete(user_id):
    if user_id == session['user_id']:
        flash('No podés eliminar tu propia cuenta')
        return redirect(url_for('admin_panel'))
    usuario = Usuario.query.get(user_id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuario eliminado')
    return redirect(url_for('admin_panel'))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        user = Usuario.query.get(session['user_id'])
        if not user.check_password(current_password):
            flash('Contraseña actual incorrecta')
            return redirect(url_for('reset_password'))
        user.set_password(new_password)
        db.session.commit()
        flash('Contraseña actualizada')
        return redirect(url_for('dashboard'))
    return render_template('reset_password.html')

if __name__ == '__main__':
    app.run(debug=True)
