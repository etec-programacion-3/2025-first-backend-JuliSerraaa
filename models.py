from app import db

class Libro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    autor = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(50), default='disponible') # disponible, prestado, etc.
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Libro {self.titulo}>'