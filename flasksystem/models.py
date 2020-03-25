import enum
from datetime import datetime
from flasksystem import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Area(db.Document):
    Lab = db.StringField()
    Bod = db.StringField
    Lab_Bod = ds.StringField()


class Medida(db.Document):
    Gramos = db.StringField()
    Kilogramos = db.StringField()
    Ml = db.StringField()
    Unidad = db.StringField()
    Litros = db.StringField()


class Quimico(db.Document):
    tipo = db.StringField()
    reactivo_id = db.StringField()
    materia_id = db.StringField()
    area = db.Column(db.Enum(Area), nullable=False)

class BodCorr(db.Document):
    nro =db.IntField()

class LabCorr(db.Model):
    nro = db.IntField()
# Cambiar BODCORR Y LABCORR A UN SOLO CORRELATIVO (QUIZAS ELEJIR UN MEJOR NOMBRE)
# class Correlativo(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     nro = db.Column(db.Integer, nullable=False, default=1)


class Materia(db.Document):
    nombre = db.StringField()
    codigo = db.StringField()
    medida = db.StringField()
    historial = db.DocumentField(HistorialMaterias)
    quimico = db.DocumentField(Quimico)
    cantidad = db.IntField()
    bajo_stock = db.IntField()
    tipo = db.StringField()
    formulas = db.DocumentField(Ingrediente) #Acceso a los datos de la tabla Ingredientes
    area = db.StringField()

class HistorialMaterias(db.Document):
    observacion = db.StringField()
    cantidad = db.IntField()
    fecha_registro = db.IntField()
    materia_id = db.StringField()
    user_id = db.StringField()
    tipo = db.StringField()
    historial_quimico = db.DocumentField(Ingrediente)
    area = db.StringField()


class Formula(db.Document):
    reactivo_id = db.IntField()
    reactivo = db.DocumentField(Reactivo) # Accso a los datos de la tabla Reactivo
    materias = db.DocumentField(Ingrediente) # Acceso a los datos de la tabla Ingrediente    


class HistorialQuimicos(db.Document):
    tipo = db.StringField()
    reactivo_id = db.StringField()
    materia_id = db.StringField()
    fecha_registro = db.IntField()
    area = db.StringField()

class HistorialReactivos(db.Document):
    observacion = db.StringField()
    cantidad = db.IntField()
    fecha_registro = db.IntField()
    reactivo_id = db.StringField()
    user_id = db.StringField()
    tipo = db.StringField()
    historial_quimico = db.DocumentField(HistorialQuimicos)
    lote = db.StringField()
    area = db.StringField()

class Reactivo(db.Document):
    nombre = db.StringField()
    codigo =db.StringField()
    medida = db.StringField()
    historial = db.DocumentField(HistorialReactivos)
    quimico = db.DocumentField(Quimico)
    cantidad = db.IntField()
    bajo_stock = db.IntField()
    tipo = db.StringField()
    formula = db.DocumentField(formula)
    area = db.StringField()
    tiene_formula = db.BoolField()

class Ingrediente(db.Document):
    materia_id = db.StringField()
    formula_id = db.StringField()
    ratio = db.StringField()
    materia = db.DocumentField(Materia)
    formula = db.DocumentField(formula)

class User(db.Document):
    username = db.StringField()
    email = db.StringField()
    password = db.StringField()
    reactivos = db.DocumentField(HistorialReactivos)
    materias = db.DocumentField(HistorialMaterias)
    area = db.StringField()