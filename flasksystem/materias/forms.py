from flasksystem import db
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, ValidationError
from flasksystem.models import Medida, Materia

class MateriaForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    codigo = StringField('Codigo', validators=[DataRequired(), Length(max=30)])
    medida = SelectField("Medidas", choices=Medida.choices(), coerce=Medida.coerce)
    bajo_stock = IntegerField('Bajo Stock', validators=[DataRequired()])
    # foo = SelectField('Foo', coerce=int, choices=[(1, 'Foo 1'), (2, 'Foo 2')])
    submit = SubmitField('Ingresar')
    
    def validate_bajo_stock(self, bajo_stock):
        if bajo_stock.data <= 0:
            raise ValidationError('Ingresa una cantidad mayor a 0')

class AddMateriaForm(FlaskForm):
    cantidad = IntegerField(validators=[DataRequired()])
    observacion = StringField('Observacion', validators=[Length(max=100)])
    submit = SubmitField('Ingresar')

    def validate_cantidad(self, cantidad):
        if cantidad.data <= 0:
            raise ValidationError('Ingresa una cantidad mayor a 0')

class ReduceMateriaForm(FlaskForm):
    cantidad = IntegerField(validators=[DataRequired()])
    observacion = StringField('Observacion', validators=[Length(max=100)])
    submit = SubmitField('Ingresar')

    def validate_cantidad(self, cantidad):
        if cantidad.data <= 0:
            raise ValidationError('Ingresa una cantidad mayor a 0')
