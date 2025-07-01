# Requisitos:
# pip install flask flask_sqlalchemy weasyprint

from flask import Flask, render_template, request, redirect, send_file, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from io import BytesIO
from weasyprint import HTML

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recibos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Recibo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(50))
    tipo_vianda = db.Column(db.String(50))
    precio = db.Column(db.Float)
    forma_pago = db.Column(db.String(50))
    fecha_pago = db.Column(db.Date)
    fecha_terminacion = db.Column(db.Date)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Usuario.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        if user:
            session['usuario_id'] = user.id
            return redirect('/formulario')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nuevo = Usuario(username=request.form['username'], password=request.form['password'])
        db.session.add(nuevo)
        db.session.commit()
        return redirect('/')
    return render_template('registro.html')

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if 'usuario_id' not in session:
        return redirect('/')
    if request.method == 'POST':
        fecha_pago = datetime.strptime(request.form['fecha_pago'], '%Y-%m-%d')
        dias_agregados = 0
        fecha_terminacion = fecha_pago
        while dias_agregados < 22:
            fecha_terminacion += timedelta(days=1)
            if fecha_terminacion.weekday() < 5:
                dias_agregados += 1
        recibo = Recibo(
            cliente=request.form['cliente'],
            telefono=request.form['telefono'],
            tipo_vianda=request.form['tipo_vianda'],
            precio=float(request.form['precio']),
            forma_pago=request.form['forma_pago'],
            fecha_pago=fecha_pago,
            fecha_terminacion=fecha_terminacion,
            usuario_id=session['usuario_id']
        )
        db.session.add(recibo)
        db.session.commit()
        return redirect(url_for('descargar_pdf', recibo_id=recibo.id))
    return render_template('formulario.html')

@app.route('/descargar/<int:recibo_id>')
def descargar_pdf(recibo_id):
    recibo = Recibo.query.get_or_404(recibo_id)
    html = render_template('recibo_pdf.html', recibo=recibo)
    pdf_file = BytesIO()
    HTML(string=html).write_pdf(pdf_file)
    pdf_file.seek(0)
    return send_file(pdf_file, download_name='recibo_vianda.pdf', as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
