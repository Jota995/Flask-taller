from flask import render_template, url_for, flash, redirect, abort, Blueprint
from flask_login import current_user, login_required
from flasksystem import db
from flasksystem.models import Materia, HistorialMaterias, Quimico, HistorialQuimicos, Area
from flasksystem.materias.forms import MateriaForm, AddMateriaForm, ReduceMateriaForm
from flasksystem.main.utils import check_bod, check_lab, check_only_bod, check_only_lab
from flasksystem.main.forms import ModBajoStockForm

materias = Blueprint('materias', __name__)

# --------------------------------SECTOR DE ROUTES LABORATORIO----------------------------------------------

@materias.route("/lab/materia/create", methods=['GET', 'POST'])
@login_required
def lab_new_materia():
    check_only_lab()
    form = MateriaForm()
    if form.validate_on_submit():
        materia = Materia(nombre=form.nombre.data, codigo=form.codigo.data, medida=form.medida.data, 
                            bajo_stock=form.bajo_stock.data, area=Area.Lab)
        db.session.add(materia)
        db.session.commit()
        quimico = Quimico(tipo='Materia', materia=materia, area=Area.Lab)
        db.session.add(quimico)
        db.session.commit()        
        flash('La materia se ha creado exitosamente!', 'success')
        return redirect(url_for('main.lab_home'))
    return render_template('crear_materia.html', title='Nueva Materia',
                            form=form, legend='Nueva Materia', area='Lab')

@materias.route("/lab/materia/<int:materia_id>")
@login_required
def lab_materia(materia_id):
    check_lab()
    materia = Materia.query.get_or_404(materia_id)
    if materia.area != Area.Lab:
        return abort(403)
    return render_template('materia.html', title=materia.nombre, materia=materia, area='Lab', user=current_user)

@materias.route("/lab/materia/<int:materia_id>/alerta", methods=['GET', 'POST'])
@login_required
def lab_alerta_materia(materia_id):
    check_only_lab()
    materia = Materia.query.get_or_404(materia_id)
    if materia.area != Area.Lab:
        return abort(403)
    form = ModBajoStockForm()
    if form.validate_on_submit():
        materia.bajo_stock = form.bajo_stock.data
        db.session.commit()
        flash('Actualizada la cantidad para la alerta de bajo stock', 'success')
        return redirect(url_for('materias.lab_materia', materia_id=materia.id))
    return render_template('modificar_alerta.html', form=form, legend='Modifica Alerta', area='Lab', materia=materia)

@materias.route("/lab/home/materia")
@login_required
def lab_home_materia():
    check_lab()
    # materias = Materia.query.filter_by(area=Area.Lab).all() # Esta forma no tiene order_by
    materias = db.session.query(Materia).filter(Materia.area == Area.Lab).order_by(Materia.id).all()
    return render_template('ver_materias.html', materias=materias, area='Lab', user=current_user)

@materias.route("/lab/materia/<int:materia_id>/add", methods=['GET', 'POST'])
@login_required
def lab_add_materia(materia_id):
    check_only_lab()
    materia = Materia.query.get_or_404(materia_id)
    if materia.area != Area.Lab:
        return abort(403)
    form = AddMateriaForm()
    if form.validate_on_submit():
        materia.cantidad += form.cantidad.data
        historial = HistorialMaterias(observacion=form.observacion.data, cantidad=form.cantidad.data,
                                         materia=materia, user = current_user, tipo='Entrada', area=Area.Lab)
        db.session.add(historial)
        db.session.commit()
        historial_quimico = HistorialQuimicos(tipo='Materia',historial_materia = historial, fecha_registro = historial.fecha_registro, area=Area.Lab)
        db.session.add(historial_quimico)
        db.session.commit()
        flash('Se ha añadido la entrada de materia', 'success')
        return redirect(url_for('materias.lab_materia', materia_id=materia.id))
    return render_template('añadir_materia.html', title='Menu Materia', 
                            form=form, legend='Menu Materia', materia=materia, area='Lab')

@materias.route("/lab/materia/<int:materia_id>/historial", methods=['GET', 'POST'])
@login_required
def lab_historial_materia_especifico(materia_id):
    check_lab()
    materia = Materia.query.get_or_404(materia_id)
    if materia.area != Area.Lab:
        return abort(403)
    historiales = HistorialMaterias.query.filter_by(materia=materia).order_by(HistorialMaterias.fecha_registro.desc()).all()
    return render_template('historial_materia.html', title='Menu Historial Materia', legend='Menu Historial Materia', 
                            historiales=historiales, materia=materia, area='Lab')

@materias.route("/lab/materia/historial")
@login_required
def lab_historial_materias():
    check_lab()
    historiales = HistorialMaterias.query.filter_by(area=Area.Lab).order_by(HistorialMaterias.fecha_registro.desc()).all()
    return render_template('historial_total_materias.html', historiales=historiales, title='Historial Materias', area='Lab')

@materias.route("/lab/materia/<int:materia_id>/reduce", methods=['GET', 'POST'])
@login_required
def lab_reduce_materia(materia_id):
    check_only_lab()
    materia = Materia.query.get_or_404(materia_id)
    if materia.area != Area.Lab:
        return abort(403)
    form = ReduceMateriaForm()
    if form.validate_on_submit():
        if materia.cantidad - form.cantidad.data < 0:
            flash('No se puede dejar la cantidad en numeros negativos', 'danger')
            return redirect(url_for('materias.lab_reduce_materia', materia_id=materia.id))        
        materia.cantidad -= form.cantidad.data
        historial = HistorialMaterias(observacion=form.observacion.data, cantidad=form.cantidad.data, 
                                        materia=materia, user = current_user, tipo='Salida', area=Area.Lab)
        db.session.add(historial)
        db.session.commit()
        historial_quimico = HistorialQuimicos(tipo='Materia',historial_materia = historial, fecha_registro = historial.fecha_registro, area=Area.Lab)
        db.session.add(historial_quimico)
        db.session.commit()        
        flash('Se ha añadido la salida de materia', 'success')
        return redirect(url_for('materias.lab_materia', materia_id=materia.id))
    return render_template('salida_materia.html', title='Menu Materia', 
                            form=form, legend='Menu Materia', materia=materia, area='Lab')

@materias.route("/lab/materia/<int:materia_id>/delete", methods=['POST'])
@login_required
def lab_delete_materia(materia_id):
    check_only_lab()
    materia = Materia.query.get_or_404(materia_id)
    if materia.area != Area.Lab:
        return abort(403)
    if materia.formulas != []:
        flash('Esta materia es parte de una o más formulas. Si desea eliminarla por favor elimine la(s) formula(s) de la(s) que es parte', 'danger')
        return redirect(url_for('materias.lab_materia', materia_id = materia.id))
    historiales = HistorialMaterias.query.filter_by(materia_id=materia_id).all()
    quimicos = Quimico.query.filter_by(materia_id=materia_id).all()
    # Eliminar Tablas dependientes de Materia
    for historial in historiales:
        q_historiales = HistorialQuimicos.query.filter_by(materia_id=historial.id).all()
        for q_historial in q_historiales:
            db.session.delete(q_historial)
        db.session.delete(historial)
    for quimico in quimicos:
        db.session.delete(quimico)
    db.session.delete(materia)
    db.session.commit()
    flash('La materia se ha eliminado', 'success')
    return redirect(url_for('main.lab_home'))

# ----------------------------------------------------------------------------------------------------------


# --------------------------------SECTOR DE ROUTES BODEGA---------------------------------------------------

@materias.route("/bod/materia/create", methods=['GET', 'POST'])
@login_required
def bod_new_materia():
    check_only_bod()
    form = MateriaForm()
    if form.validate_on_submit():
        materia = Materia(nombre=form.nombre.data, codigo=form.codigo.data, medida=form.medida.data, 
                            bajo_stock=form.bajo_stock.data, area=Area.Bod)
        db.session.add(materia)
        db.session.commit()
        quimico = Quimico(tipo='Materia', materia=materia, area=Area.Bod)
        db.session.add(quimico)
        db.session.commit()        
        flash('La materia se ha creado exitosamente!', 'success')
        return redirect(url_for('main.bod_home'))
    return render_template('crear_materia.html', title='Nueva Materia',
                            form=form, legend='Nueva Materia', area='Bod')

@materias.route("/bod/materia/<int:materia_id>")
@login_required
def bod_materia(materia_id):
    check_bod()
    materia = Materia.query.get_or_404(materia_id)
    if materia.area != Area.Bod:
        return abort(403)
    return render_template('materia.html', title=materia.nombre, materia=materia, area='Bod', user=current_user)

@materias.route("/bod/materia/<int:materia_id>/alerta", methods=['GET', 'POST'])
@login_required
def bod_alerta_materia(materia_id):
    check_only_bod()
    materia = Materia.query.get_or_404(materia_id)
    if materia.area != Area.Bod:
        return abort(403)
    form = ModBajoStockForm()
    if form.validate_on_submit():
        materia.bajo_stock = form.bajo_stock.data
        db.session.commit()
        flash('Actualizada la cantidad para la alerta de bajo stock', 'success')
        return redirect(url_for('materias.bod_materia', materia_id=materia.id))
    # return render template alerta_reactivo.html
    return render_template('alerta_materia.html', form=form, legend='Modifica Alerta', area='Bod', materia=materia)

@materias.route("/bod/home/materia")
@login_required
def bod_home_materia():
    check_bod()
    # materias = Materia.query.filter_by(area=Area.Bod).all() # Esta forma no tiene el order_by
    materias = db.session.query(Materia).filter(Materia.area == Area.Bod).order_by(Materia.id).all()
    return render_template('ver_materias.html', materias=materias, area='Bod', user=current_user)

@materias.route("/bod/materia/<int:materia_id>/add", methods=['GET', 'POST'])
@login_required
def bod_add_materia(materia_id):
    check_only_bod()
    materia = Materia.query.get_or_404(materia_id)
    if materia.area != Area.Bod:
        return abort(403)
    form = AddMateriaForm()
    if form.validate_on_submit():
        materia.cantidad += form.cantidad.data
        historial = HistorialMaterias(observacion=form.observacion.data, cantidad=form.cantidad.data, 
                                        materia=materia, user = current_user, tipo='Entrada', area=Area.Bod)
        db.session.add(historial)
        db.session.commit()
        historial_quimico = HistorialQuimicos(tipo='Materia',historial_materia = historial, fecha_registro = historial.fecha_registro, area=Area.Bod)
        db.session.add(historial_quimico)
        db.session.commit()
        flash('Se ha añadido la salida de materia', 'success')
        return redirect(url_for('materias.bod_materia', materia_id=materia.id))
    return render_template('añadir_materia.html', title='Menu Materia', 
                            form=form, legend='Menu Materia', materia=materia, area='Bod')

@materias.route("/bod/materia/<int:materia_id>/historial", methods=['GET', 'POST'])
@login_required
def bod_historial_materia_especifico(materia_id):
    check_bod()
    materia = Materia.query.get_or_404(materia_id)
    if materia.area != Area.Bod:
        return abort(403)
    historiales = HistorialMaterias.query.filter_by(materia=materia).order_by(HistorialMaterias.fecha_registro.desc()).all()
    return render_template('historial_materia.html', title='Menu Historial Materia', legend='Menu Historial Materia', 
                            historiales=historiales, materia=materia, area='Bod')

@materias.route("/bod/materia/historial")
@login_required
def bod_historial_materias():
    check_bod()
    historiales = HistorialMaterias.query.filter_by(area=Area.Bod).order_by(HistorialMaterias.fecha_registro.desc()).all()
    return render_template('historial_total_materias.html', historiales=historiales, title='Historial Materias', area='Bod')

@materias.route("/bod/materia/<int:materia_id>/reduce", methods=['GET', 'POST'])
@login_required
def bod_reduce_materia(materia_id):
    check_only_bod()
    materia = Materia.query.get_or_404(materia_id)
    if materia.area != Area.Bod:
        return abort(403)
    form = ReduceMateriaForm()
    if form.validate_on_submit():
        if materia.cantidad - form.cantidad.data < 0:
            flash('No se puede dejar la cantidad en numeros negativos', 'danger')
            return redirect(url_for('materias.bod_reduce_materia', materia_id=materia.id))        
        materia.cantidad -= form.cantidad.data
        historial = HistorialMaterias(observacion=form.observacion.data, cantidad=form.cantidad.data, materia=materia, 
                                        user = current_user, tipo='Salida', area=Area.Bod)
        db.session.add(historial)
        db.session.commit()
        historial_quimico = HistorialQuimicos(tipo='Materia',historial_materia = historial, fecha_registro = historial.fecha_registro, area=Area.Bod)
        db.session.add(historial_quimico)
        db.session.commit()        
        flash('Se ha añadido la entrada de materia', 'success')
        return redirect(url_for('materias.bod_materia', materia_id=materia.id))
    return render_template('salida_materia.html', title='Menu Materia', 
                            form=form, legend='Menu Materia', materia=materia, area='Bod')

@materias.route("/bod/materia/<int:materia_id>/delete", methods=['POST'])
@login_required
def bod_delete_materia(materia_id):
    check_only_bod()
    materia = Materia.query.get_or_404(materia_id)
    if materia.area != Area.Bod:
        return abort(403)
    if materia.formulas != []:
        flash('Esta materia es parte de una o más formulas. Si desea eliminarla por favor elimine la(s) formula(s) de la(s) que es parte', 'danger')
        return redirect(url_for('materias.bod_materia', materia_id = materia.id))
    historiales = HistorialMaterias.query.filter_by(materia_id=materia_id).all()
    quimicos = Quimico.query.filter_by(materia_id=materia_id).all()
    # Eliminar Tablas dependientes de Materia
    for historial in historiales:
        q_historiales = HistorialQuimicos.query.filter_by(materia_id=historial.id).all()
        for q_historial in q_historiales:
            db.session.delete(q_historial)
        db.session.delete(historial)
    for quimico in quimicos:
        db.session.delete(quimico)
    db.session.delete(materia)
    db.session.commit()
    flash('La materia se ha eliminado', 'success')
    return redirect(url_for('main.bod_home'))

# ----------------------------------------------------------------------------------------------------------


# --------------------------------SECTOR DE ROUTES GENERAL--------------------------------------------------


# ----------------------------------------------------------------------------------------------------------



# NOTAS:
#  1.- usando area='Lab' o 'Bod' puedo hacer que jinja2 haga el url_for correcto
