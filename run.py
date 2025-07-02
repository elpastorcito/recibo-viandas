from flask import Flask
from app.routes import routes
from app.models import db, Usuario
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = 'clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(routes)

with app.app_context():
    db.create_all()
    if not Usuario.query.filter_by(username='admin').first():
        admin = Usuario(username='admin', password=generate_password_hash('noli#0932'))
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
