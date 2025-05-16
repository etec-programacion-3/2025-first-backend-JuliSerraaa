from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

# PASO 1: Inicializa SQLAlchemy sin pasarle la app directamente todavía.
# En este punto, 'db' es una instancia de SQLAlchemy, pero aún no sabe
# con qué aplicación Flask está trabajando.

db = SQLAlchemy()

# Defino el modelo de datos, que antes estaba en models.py pero me daba errores
# Al colocarlo acá, elimino la importación circular.

class Libro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    autor = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(50), default='disponible') # disponible, prestado, etc.
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Libro {self.titulo}>'

    # Método para serializar el objeto a un diccionario, útil para JSON
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'autor': self.autor,
            'categoria': self.categoria,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

# PASO 2: Vincula la instancia 'db' con la aplicación Flask.
# Esto se hace después de que todos los modelos (en este caso, Libro)
# han sido definidos.

db.init_app(app)

# --- DEFINICIÓN DE RUTAS (ENDPOINTS) ---

@app.route('/')
def index():
    return "¡Bienvenido al Backend de la Biblioteca!"

# Endpoint para listar todos los libros con búsqueda y filtrado
@app.route('/libros', methods=['GET'])
def get_libros():
    query = Libro.query
    titulo = request.args.get('titulo')
    autor = request.args.get('autor')
    categoria = request.args.get('categoria')
    estado = request.args.get('estado')

    if titulo:
        query = query.filter(Libro.titulo.ilike(f'%{titulo}%'))
    if autor:
        query = query.filter(Libro.autor.ilike(f'%{autor}%'))
    if categoria:
        query = query.filter(Libro.categoria.ilike(f'%{categoria}%'))
    if estado:
        query = query.filter(Libro.estado.ilike(f'%{estado}%'))

    libros = query.all()
    return jsonify([libro.to_dict() for libro in libros])

# Endpoint para obtener un libro específico por su ID
@app.route('/libros/<int:id>', methods=['GET'])
def get_libro(id):
    libro = Libro.query.get(id)
    if libro is None:
        return jsonify({'message': 'Libro no encontrado'}), 404
    return jsonify(libro.to_dict())

# Endpoint para crear un nuevo libro
@app.route('/libros', methods=['POST'])
def create_libro():
    data = request.json
    if not data:
        return jsonify({'message': 'No se proporcionaron datos'}), 400

    # Validación de datos 
    required_fields = ['titulo', 'autor', 'categoria'] 
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'El campo "{field}" es requerido'}), 400

    if not isinstance(data['titulo'], str) or len(data['titulo']) < 1:
        return jsonify({'message': 'Título inválido'}), 400
    
    # Puedes añadir más validaciones para otros campos si lo deseas

    try:
        nuevo_libro = Libro(
            titulo=data['titulo'],
            autor=data['autor'],
            categoria=data['categoria'],
            estado=data.get('estado', 'disponible')
        )
        db.session.add(nuevo_libro)
        db.session.commit()
        return jsonify(nuevo_libro.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al crear el libro: {str(e)}'}), 500

# Endpoint para actualizar un libro existente por su ID
@app.route('/libros/<int:id>', methods=['PUT'])
def update_libro(id):
    libro = Libro.query.get(id)
    if libro is None:
        return jsonify({'message': 'Libro no encontrado'}), 404

    data = request.json
    if not data:
        return jsonify({'message': 'No se proporcionaron datos para actualizar'}), 400

    if 'titulo' in data:
        if not isinstance(data['titulo'], str) or len(data['titulo']) < 1:
            return jsonify({'message': 'Título inválido'}), 400
        libro.titulo = data['titulo']
    if 'autor' in data:
        if not isinstance(data['autor'], str) or len(data['autor']) < 1:
            return jsonify({'message': 'Autor inválido'}), 400
        libro.autor = data['autor']

    if 'categoria' in data:
        libro.categoria = data['categoria']
    if 'estado' in data:
        libro.estado = data['estado']

    try:
        db.session.commit()
        return jsonify(libro.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al actualizar el libro: {str(e)}'}), 500

# Endpoint para eliminar un libro por su ID
@app.route('/libros/<int:id>', methods=['DELETE'])
def delete_libro(id):
    libro = Libro.query.get(id)
    if libro is None:
        return jsonify({'message': 'Libro no encontrado'}), 404

    try:
        db.session.delete(libro)
        db.session.commit()
        return jsonify({'message': 'Libro eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al eliminar el libro: {str(e)}'}), 500

# --- INICIO DE LA APLICACIÓN ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Crea las tablas en la base de datos si no existen
    app.run(debug=True)