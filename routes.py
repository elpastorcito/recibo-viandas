from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, Usuario

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    if 'user_id' in session:
        return render_template('dashboard.html')
    return redirect(url_for('routes.login'))

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('routes.index'))
    return render_template('login.html')

@routes.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('routes.login'))

@routes.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        nuevo_usuario = Usuario(username=username, password=password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('routes.login'))
    return render_template('registro.html')
