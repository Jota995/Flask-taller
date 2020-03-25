from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, ValidationError

class ModBajoStockForm(FlaskForm):
    bajo_stock = IntegerField(validators=[DataRequired()])
    submit = SubmitField('Ingresa')
    
    def validate_bajo_stock(self, bajo_stock):
        if bajo_stock.data <= 0:
            raise ValidationError('Ingresa una cantidad mayor a 0')
 
