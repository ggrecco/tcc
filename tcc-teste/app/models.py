from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from hashlib import md5


class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    resultados = db.relationship('Dados', backref='autor_usuario',
                                 lazy='dynamic')
    rel_servidor = db.relationship('Servidor', backref='rel_usuario',
                                   lazy='dynamic')

    def __repr__(self):
        return '<Usuario {}>'.format(self.nome)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


class Servidor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(140), unique=True)
    url = db.Column(db.String(255))
    ip = db.Column(db.String(25))
    scan = db.Column(db.String(10))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    resultados = db.relationship('Dados', backref='autor_servidor',
                                 lazy='dynamic')

    def __repr__(self):
        return '<Servidor {}>'.format(self.nome)


@login.user_loader
def load_user(id):
    return Usuario.query.get(int(id))


class Dados(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    servidor_id = db.Column(db.Integer, db.ForeignKey('servidor.id'))
    produto = db.Column(db.String(20))
    cveid = db.Column(db.String(25))
    tipo = db.Column(db.String(25))
    datacorrecao = db.Column(db.String(50))
    nota = db.Column(db.Float(50))
    acesso = db.Column(db.String(100))
    porta = db.Column(db.String(10))
    comentario = db.Column(db.String(5000))
    check = db.Column(db.String(5))

    def __repr__(self):
        return '<Dados {}>'.format(self.produto)
