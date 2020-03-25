from flasksystem import db
from flasksystem.models import Medida, Materia, Area
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField

class ReactivoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    codigo = StringField('Codigo', validators=[DataRequired(), Length(max=30)])
    medida = SelectField("Medidas", choices=Medida.choices(), coerce=Medida.coerce)
    bajo_stock = IntegerField('Bajo Stock', validators=[DataRequired()])
    submit = SubmitField('Ingresar')

    def validate_bajo_stock(self, bajo_stock):
        if bajo_stock.data <= 0:
            raise ValidationError('Ingresa una cantidad mayor a 0')

class AddReactivoForm(FlaskForm):
    cantidad = IntegerField(validators=[DataRequired()])
    observacion = StringField('Observacion', validators=[Length(max=100)])
    submit = SubmitField('Ingresar')
    
    def validate_cantidad(self, cantidad):
        if cantidad.data <= 0:
            raise ValidationError('Ingresa una cantidad mayor a 0')

class ProdReactivoForm(FlaskForm):
    cantidad = IntegerField(validators=[DataRequired()])
    nro_analisis = IntegerField(validators=[DataRequired()])
    observacion = StringField('Observacion', validators=[Length(max=100)])
    submit = SubmitField('Ingresar')
    
    def validate_cantidad(self, cantidad):
        if cantidad.data <= 0:
            raise ValidationError('Ingresa una cantidad mayor a 0')

class ReduceReactivoForm(FlaskForm):
    lote = StringField(validators=[DataRequired(), Length(min=3, max=15)])
    cantidad = IntegerField(validators=[DataRequired()])
    observacion = observacion = StringField('Observacion', validators=[Length(max=100)])
    submit = SubmitField('Ingresar')

    def validate_cantidad(self, cantidad):
        if cantidad.data <= 0:
            raise ValidationError('Ingresa una cantidad mayor a 0')

class NewFormulaForm(FlaskForm):
    materias = QuerySelectMultipleField('Elige Materias',query_factory=lambda: db.session.query(Materia), get_pk=lambda m: m.id, get_label=lambda m:'id: '+str(m.id) +' | nombre: '+m.nombre+' | codigo: '+m.codigo, validators=[DataRequired()]) #, widget=LazySelect()
    submit = SubmitField('Ingresa')

class LabNewFormulaForm(FlaskForm):
    materias = QuerySelectMultipleField('Elige Materias',query_factory=lambda: db.session.query(Materia).filter(Materia.area==Area.Lab), get_pk=lambda m: m.id, get_label=lambda m:'id: '+str(m.id) +' | nombre: '+m.nombre+' | codigo: '+m.codigo, validators=[DataRequired()]) #, widget=LazySelect()
    submit = SubmitField('Ingresa')

class BodNewFormulaForm(FlaskForm):
    materias = QuerySelectMultipleField('Elige Materias',query_factory=lambda: db.session.query(Materia).filter(Materia.area==Area.Bod), get_pk=lambda m: m.id, get_label=lambda m:'id: '+str(m.id) +' | nombre: '+m.nombre+' | codigo: '+m.codigo, validators=[DataRequired()]) #, widget=LazySelect()
    submit = SubmitField('Ingresa')

class NewIngrediente(FlaskForm):
    ratio = DecimalField(validators=[DataRequired()])
    sumbit = SubmitField('Ingresar')


class ConsultaForm(FlaskForm):
    cantidad = IntegerField(validators=[DataRequired()])
    submit = SubmitField('Ingresa')

    def validate_consulta(self, consulta):
        if consulta.data <= 0:
            raise ValidationError('Ingresa una cantidad mayor a 0')   