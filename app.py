from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from models import Libro # Importa el modelo aquí

if __name__ == '__main__':
    with app.app_context(): # Añade este bloque
        db.create_all() # Crea las tablas en la base de datos
    app.run(debug=True)