from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from flasksystem import db
from flasksystem.models import (Reactivo, HistorialReactivos, HistorialMaterias, Quimico, 
                                Formula, Ingrediente, HistorialQuimicos, Area, BodCorr)
from flasksystem.reactivos.forms import (AddReactivoForm, ReduceReactivoForm, ReactivoForm, 
                                        NewFormulaForm, NewIngrediente, ConsultaForm, 
                                        LabNewFormulaForm, BodNewFormulaForm, ProdReactivoForm)
from flasksystem.main.forms import ModBajoStockForm
from flasksystem.main.utils import check_bod, check_lab, check_only_bod, check_only_lab
from flasksystem.reactivos.utils import is_number

reactivos = Blueprint('reactivos', __name__)

# --------------------------------SECTOR DE ROUTES LABORATORIO----------------------------------------------

@reactivos.route("/lab/reactivo/create", methods=['GET', 'POST'])
@login_required
def lab_new_reactivo():
    check_only_lab()
    form = ReactivoForm()
    if form.validate_on_submit():
        reactivo = Reactivo(nombre=form.nombre.data, codigo=form.codigo.data, 
                            medida=form.medida.data, bajo_stock=form.bajo_stock.data, area=Area.Lab)
        db.session.add(reactivo)
        db.session.commit()
        quimico = Quimico(tipo='Reactivo', reactivo=reactivo, area=Area.Lab)
        db.session.add(quimico)
        db.session.commit()
        flash('El reactivo se ha creado exitosamente!', 'success')
        return redirect(url_for('main.lab_home'))
    return render_template('crear_reactivo.html', title='Nuevo Reactivo', 
                            form=form, legend='Nuevo Reactivo', area='Lab')

@reactivos.route("/lab/reactivo/<int:reactivo_id>")
@login_required
def lab_reactivo(reactivo_id):
    check_lab()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Lab:
        return abort(403)
    return render_template('reactivo.html', title=reactivo.nombre, reactivo=reactivo, area='Lab', user=current_user)

@reactivos.route("/lab/reactivo/<int:reactivo_id>/alerta", methods=['GET', 'POST'])
@login_required
def lab_alerta_reactivo(reactivo_id):
    check_only_lab()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Lab:
        return abort(403)
    form = ModBajoStockForm()
    if form.validate_on_submit():
        reactivo.bajo_stock = form.bajo_stock.data
        db.session.commit()
        flash('Actualizada la cantidad para la alerta de bajo stock', 'success')
        return redirect(url_for('reactivos.lab_reactivo', reactivo_id=reactivo.id))
    # return render template alerta_reactivo.html
    return render_template('alerta_reactivo.html', form=form, legend='Modifica Alerta', area='Lab', reactivo=reactivo)

@reactivos.route("/lab/home/reactivo")
@login_required
def lab_home_reactivo():
    check_lab()
    # reactivos = Reactivo.query.filter_by(area=Area.Lab).all() # Esta forma no tiene order_by
    reactivos = db.session.query(Reactivo).filter(Reactivo.area == Area.Lab).order_by(Reactivo.id).all()
    return render_template('ver_reactivos.html', reactivos=reactivos, area='Lab', user=current_user)

@reactivos.route("/lab/reactivo/<int:reactivo_id>/add", methods=['GET', 'POST'])
@login_required
def lab_add_reactivo(reactivo_id):
    check_only_lab()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Lab:
        return abort(403)
    form = AddReactivoForm()
    if form.validate_on_submit():
        reactivo.cantidad += form.cantidad.data
        historial = HistorialReactivos(observacion=form.observacion.data, cantidad=form.cantidad.data, 
                                        reactivo=reactivo, user = current_user, tipo='Entrada', area=Area.Lab)
        db.session.add(historial)
        db.session.commit()
        historial_quimico = HistorialQuimicos(tipo='Reactivo', historial_reactivo=historial, fecha_registro=historial.fecha_registro, area=Area.Lab)
        db.session.add(historial_quimico)
        db.session.commit()
        flash('Se ha añadido la entrada de reactivo', 'success')
        return redirect(url_for('reactivos.lab_reactivo', reactivo_id=reactivo.id))
    return render_template('añadir_reactivo.html', title='Menu Reactivo', 
                            form=form, legend='Menu Reactivo', reactivo=reactivo, area='Lab')

@reactivos.route("/lab/reactivo/<int:reactivo_id>/historial", methods=['GET', 'POST'])
@login_required
def lab_historial_reactivo_especifico(reactivo_id):
    check_lab()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Lab:
        return abort(403)
    historiales = HistorialReactivos.query.filter_by(reactivo=reactivo).order_by(HistorialReactivos.fecha_registro.desc()).all()
    return render_template('historial_reactivo.html', title='Menu Historial Reactivos', legend='Menu Historial Reactivo', 
                            historiales=historiales, reactivo=reactivo, area='Lab')

@reactivos.route("/lab/reactivo/historial")
@login_required
def lab_historial_reactivos():
    check_lab()
    historiales = HistorialReactivos.query.filter_by(area=Area.Lab).order_by(HistorialReactivos.fecha_registro.desc()).all()
    return render_template('historial_total_reactivos.html', historiales=historiales, title='Historial Reactivos', area='Lab')

@reactivos.route("/lab/reactivo/<int:reactivo_id>/reduce", methods=['GET', 'POST'])
@login_required
def lab_reduce_reactivo(reactivo_id):
    check_only_lab()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Lab:
        return abort(403)
    form = ReduceReactivoForm()
    if form.validate_on_submit():
        if reactivo.cantidad - form.cantidad.data < 0:
            flash('No se puede dejar la cantidad en numeros negativos', 'danger')
            return redirect(url_for('reactivos.lab_reduce_reactivo', reactivo_id=reactivo.id))
        reactivo.cantidad -= form.cantidad.data
        historial = HistorialReactivos(observacion=form.observacion.data, cantidad=form.cantidad.data, lote=form.lote.data, 
                                        reactivo=reactivo, user = current_user, tipo='Salida', area=Area.Lab)
        db.session.add(historial)
        db.session.commit()
        historial_quimico = HistorialQuimicos(tipo='Reactivo', historial_reactivo=historial, fecha_registro=historial.fecha_registro, area=Area.Lab)
        db.session.add(historial_quimico)
        db.session.commit()
        flash('Se ha añadido la entrada de reactivo', 'success')
        return redirect(url_for('reactivos.lab_reactivo', reactivo_id=reactivo.id))
    return render_template('salida_reactivo.html', title='Menu Reactivo', 
                            form=form, legend='Menu Reactivo', reactivo=reactivo, area='Lab')

@reactivos.route("/lab/reactivo/<int:reactivo_id>/delete", methods=['POST'])
@login_required
def lab_delete_reactivo(reactivo_id):
    check_only_lab()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Lab:
        return abort(403)
    historiales = HistorialReactivos.query.filter_by(reactivo_id=reactivo_id).all()
    quimicos = Quimico.query.filter_by(reactivo_id=reactivo_id).all()
    formulas = Formula.query.filter_by(reactivo_id=reactivo_id).all()
    # Eliminar Tablas dependientes de reactivo
    for historial in historiales:
        q_historiales = HistorialQuimicos.query.filter_by(reactivo_id=historial.id).all()
        for q_historial in q_historiales:
            db.session.delete(q_historial)
        db.session.delete(historial)
    for quimico in quimicos:
        db.session.delete(quimico)
    for formula in formulas:
        Ingrediente.query.filter_by(formula_id = formula.id).delete()
        db.session.delete(formula)
    db.session.delete(reactivo)
    db.session.commit()
    flash('El reactivo se ha eliminado', 'success')
    return redirect(url_for('main.lab_home'))

@reactivos.route("/lab/reactivo/<int:reactivo_id>/formula", methods=['GET', 'POST'])
@login_required
def lab_formula(reactivo_id):
    check_only_lab()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Lab:
        return abort(403)
    if reactivo.tiene_formula:
        flash('Este reactivo ya tiene una formula asociada', 'info')
        return redirect(url_for('reactivos.lab_reactivo', reactivo_id=reactivo.id))
    form = LabNewFormulaForm()
    if form.validate_on_submit():
        formula = Formula(reactivo=reactivo)
        for materia in form.materias.data:
            ing = Ingrediente(ratio=0, materia=materia)
            formula.materias.append(ing)
        db.session.add(formula)
        db.session.commit()
        flash('Ingrese los ratios de las materias seleccionadas', 'info')
        return redirect(url_for('reactivos.lab_ingrediente', reactivo_id=reactivo.id))
    return render_template('formula.html', form=form, legend='Menu Formulas', area='Lab')

@reactivos.route("/lab/reactivo/<int:reactivo_id>/formula/add", methods=['GET', 'POST'])
@login_required
def lab_ingrediente(reactivo_id):
    check_only_lab()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Lab:
        return abort(403)

    if reactivo.tiene_formula:
        flash('El reactivo ya tiene una formula ingresada', 'danger')
        return redirect(url_for('reactivos.lab_reactivo', reactivo_id = reactivo.id))

    formula = reactivo.formula
    ingredientes = Ingrediente.query.filter_by(formula_id=formula.id).all()
    form = NewIngrediente()

    if request.method == 'POST':
        form = request.form
        i = 0

        for i in (0, len(ingredientes)-1):
            if not is_number(form['ratio_'+str(i)]):
                flash('Por favor ingrese un numero valido para los ratios', 'warning')
                return render_template('ingredientes.html', form = form, legend = 'Ingrese Ratio', 
                                        ingredientes = ingredientes, len = len(ingredientes), area='Lab')
            else:
                if float(form['ratio_'+str(i)]) <= 0:
                    flash('Por favor ingrese numeros positivos mayores a 0 para los ratios', 'warning')
                    return render_template('ingredientes.html', form = form, legend = 'Ingrese Ratio', 
                                            ingredientes = ingredientes, len = len(ingredientes), area='Lab')

        i = 0
        for ingrediente in ingredientes:
            ingrediente.ratio = form['ratio_'+str(i)]  
            i += 1
        reactivo.tiene_formula = True
        db.session.commit()

        flash('Formula Creada', 'success')     
        return redirect(url_for('reactivos.lab_reactivo', reactivo_id=reactivo.id))

    return render_template('ingredientes.html', form=form, legend='Ingresa Ratio', ingredientes = ingredientes, len = len(ingredientes), area='Lab')

@reactivos.route("/lab/reactivo/<int:reactivo_id>/producir", methods=['GET', 'POST'])
@login_required
def lab_entrada_reactivo(reactivo_id):
    check_only_lab()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Lab:
        return abort(403)
    # print(reactivo.formula)
    if not reactivo.tiene_formula:
        flash('El reactivo no tiene una formula asociada, crea una para poder realizar produccion de reactivo', 'info')
        return redirect(url_for('reactivos.lab_formula', reactivo_id=reactivo.id))
    
    formula = reactivo.formula
    ingredientes = Ingrediente.query.filter_by(formula_id = formula.id).all() 
    for ingrediente in ingredientes:
        if ingrediente.ratio == 0:
            Ingrediente.query.filter_by(formula_id=formula.id).delete()
            db.session.delete(formula)
            db.session.commit()
            flash('El proceso de asignarle formula al reactivo fue detenido antes de finalizar. Para asignarle una formula por favor complete el proceso', 'warning')
            return redirect(url_for('reactivos.lab_formula', reactivo_id = reactivo.id))

    form = ProdReactivoForm()
    if form.validate_on_submit():
        ingredientes = Ingrediente.query.filter_by(formula_id=formula.id)
        flag = True
        for assoc in ingredientes:
            if (assoc.materia.cantidad - form.cantidad.data * assoc.ratio) < 0:
                flag = False
                break
        if flag:
            
            correlativo = BodCorr.query.first()
            if correlativo:
                correlativo.nro += 1 
                db.session.commit()
            else:
                new_correlativo = BodCorr()
                db.session.add(new_correlativo)
                db.session.commit()

            last = db.session.query(HistorialReactivos).filter(HistorialReactivos.area == Area.Lab).order_by(HistorialReactivos.id.desc()).first()
            año_actual = datetime.utcnow().strftime("%y")
            if last:
                print("EXISTE LAST")
                año_anterior = last.fecha_registro.strftime("%y")
                if año_anterior != año_actual:
                    correlativo = BodCorr.query.first()
                    print("LOS AÑOS SON DIFERENTES")
                    if correlativo:
                        correlativo.nro = 1
                        db.session.commit()
                    else:
                        new_correlativo = BodCorr()
                        db.session.add(new_correlativo)
                        db.session.commit()

            correlativo = BodCorr.query.first()
            nro_correlativo = f'{correlativo.nro:04}'
            nro_analisis = f'{form.nro_analisis.data:04}'
            lote = 'Q'+año_actual+nro_correlativo+nro_analisis
                       
            for assoc in ingredientes:
                # print(assoc.materia.cantidad)
                # print("-")
                # print(assoc.ratio)
                # print(assoc.materia.cantidad - assoc.ratio)
                assoc.materia.cantidad -= (form.cantidad.data * assoc.ratio)
                historial = HistorialMaterias(observacion=f"Produccion de reactivo [{reactivo.id}, {reactivo.nombre}]", 
                                                cantidad=form.cantidad.data*assoc.ratio, materia=assoc.materia, 
                                                user=current_user, tipo='Producción', area='Lab') # Quizas cambiar el tipo
                db.session.add(historial)
                db.session.commit()
                historial_quimico = HistorialQuimicos(tipo='Materia', historial_materia = historial, 
                                                        fecha_registro = historial.fecha_registro, area='Lab')
                db.session.add(historial_quimico)
                db.session.commit()
            reactivo.cantidad += form.cantidad.data
            historial = HistorialReactivos(observacion=form.observacion.data, cantidad=form.cantidad.data, 
                                            reactivo=reactivo, user=current_user, tipo='Produccion', area='Lab', lote=lote) # Quizas cambiar el tipo
            db.session.add(historial)
            db.session.commit() 
            historial_quimico = HistorialQuimicos(tipo='Reactivo', historial_reactivo = historial, 
                                                    fecha_registro = historial.fecha_registro, area='Lab')
            db.session.add(historial_quimico)
            db.session.commit()
            flash('Se ha producido con exito el reactivo', 'success')
            return redirect(url_for('reactivos.lab_reactivo', reactivo_id=reactivo.id))
        else:
            flash('La cantidad ingresada supera al stock de las materias', 'danger')
            return redirect(url_for('reactivos.lab_entrada_reactivo', reactivo_id=reactivo.id))

    return render_template('producir_reactivo.html', legend='Menu Produccion', form=form, reactivo=reactivo, area='Lab')

@reactivos.route("/lab/reactivo/<int:reactivo_id>/consulta", methods=['GET','POST'])
@login_required
def lab_consulta(reactivo_id):
    check_lab()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Lab:
        return abort(403)

    if not reactivo.tiene_formula:
        flash('El reactivo no tiene una formula asociada, crea una para poder consultar la produccion de reactivo', 'info')
        return redirect(url_for('reactivos.lab_formula', reactivo_id=reactivo.id))

    formula = reactivo.formula
    ingredientes = Ingrediente.query.filter_by(formula_id = formula.id).all() 
    for ingrediente in ingredientes:
        if ingrediente.ratio == 0:
            Ingrediente.query.filter_by(formula_id = formula.id).delete()
            db.session.delete(formula)
            db.session.commit()
            flash('El proceso de asignarle formula al reactivo fue detenido antes de finalizar. Para asignarle una formula por favor complete el proceso', 'warning')
            return redirect(url_for('reactivos.lab_formula', reactivo_id = reactivo.id))

    form = ConsultaForm()
    if form.validate_on_submit():
        flag = True
        for assoc in ingredientes:
            if (assoc.materia.cantidad - form.cantidad.data * assoc.ratio) < 0:
                flag = False
                break
        if flag:
            flash(f"Es posible crear {form.cantidad.data} {reactivo.medida.value} de reactivo", 'info')
        else:
            flash(f'No es posible crear {form.cantidad.data} {reactivo.medida.value} de reactivo', 'warning')
        return redirect(url_for('reactivos.lab_consulta', reactivo_id = reactivo.id))
    return render_template('consulta.html', form=form, legend='Consulta', reactivo = reactivo, area='Lab')

# ----------------------------------------------------------------------------------------------------------    


# --------------------------------SECTOR DE ROUTES BODEGA---------------------------------------------------

@reactivos.route("/bod/reactivo/create", methods=['GET', 'POST'])
@login_required
def bod_new_reactivo():
    check_only_bod()
    form = ReactivoForm()
    if form.validate_on_submit():
        reactivo = Reactivo(nombre=form.nombre.data, codigo=form.codigo.data, 
                            medida=form.medida.data, bajo_stock=form.bajo_stock.data, area=Area.Bod)
        db.session.add(reactivo)
        db.session.commit()
        quimico = Quimico(tipo='Reactivo', reactivo=reactivo, area=Area.Bod)
        db.session.add(quimico)
        db.session.commit()
        flash('El reactivo se ha creado exitosamente!', 'success')
        return redirect(url_for('main.bod_home'))
    return render_template('crear_reactivo.html', title='Nuevo Reactivo', 
                            form=form, legend='Nuevo Reactivo', area='Bod')

@reactivos.route("/bod/reactivo/<int:reactivo_id>")
@login_required
def bod_reactivo(reactivo_id):
    check_bod()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Bod:
        return abort(403)
    return render_template('reactivo.html', title=reactivo.nombre, reactivo=reactivo, area='Bod', user=current_user)

@reactivos.route("/bod/reactivo/<int:reactivo_id>/alerta", methods=['GET', 'POST'])
@login_required
def bod_alerta_reactivo(reactivo_id):
    check_only_bod()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Bod:
        return abort(403)
    form = ModBajoStockForm()
    if form.validate_on_submit():
        reactivo.bajo_stock = form.bajo_stock.data
        db.session.commit()
        flash('Actualizada la cantidad para la alerta de bajo stock', 'success')
        return redirect(url_for('reactivos.bod_reactivo', reactivo_id=reactivo.id))
    return render_template('alerta_reactivo.html', form=form, legend='Modifica Alerta', area='Bod', reactivo=reactivo)

@reactivos.route("/bod/home/reactivo")
@login_required
def bod_home_reactivo():
    check_bod()
    # reactivos = Reactivo.query.filter_by(area=Area.Bod).all() # Por alguna razon no ordena del primer id a ultimo
    reactivos = db.session.query(Reactivo).filter(Reactivo.area == Area.Bod).order_by(Reactivo.id).all()
    return render_template('ver_reactivos.html', reactivos=reactivos, area='Bod', user=current_user)

@reactivos.route("/bod/reactivo/<int:reactivo_id>/add", methods=['GET', 'POST'])
@login_required
def bod_add_reactivo(reactivo_id):
    check_only_bod()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Bod:
        return abort(403)
    form = AddReactivoForm()
    if form.validate_on_submit():
        reactivo.cantidad += form.cantidad.data
        historial = HistorialReactivos(observacion=form.observacion.data, cantidad=form.cantidad.data, 
                                        reactivo=reactivo, user = current_user, tipo='Entrada', area=Area.Bod)
        db.session.add(historial)
        db.session.commit()
        historial_quimico = HistorialQuimicos(tipo='Reactivo',historial_reactivo=historial, fecha_registro=historial.fecha_registro, area=Area.Bod)
        db.session.add(historial_quimico)
        db.session.commit()
        flash('Se ha añadido la entrada de reactivo', 'success')
        return redirect(url_for('reactivos.bod_reactivo', reactivo_id=reactivo.id))
    return render_template('añadir_reactivo.html', title='Menu Reactivo', 
                            form=form, legend='Menu Reactivo', reactivo=reactivo, area='Bod')

@reactivos.route("/bod/reactivo/<int:reactivo_id>/historial", methods=['GET', 'POST'])
@login_required
def bod_historial_reactivo_especifico(reactivo_id):
    check_bod()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Bod:
        return abort(403)
    historiales = HistorialReactivos.query.filter_by(reactivo=reactivo).order_by(HistorialReactivos.fecha_registro.desc()).all()
    return render_template('historial_reactivo.html', title='Menu Historial Reactivos', legend='Menu Historial Reactivo', 
                            historiales=historiales, reactivo=reactivo, area='Bod')

@reactivos.route("/bod/reactivo/historial")
@login_required
def bod_historial_reactivos():
    historiales = HistorialReactivos.query.filter_by(area=Area.Bod).order_by(HistorialReactivos.fecha_registro.desc()).all()
    return render_template('historial_total_reactivos.html', historiales=historiales, title='Historial Reactivos', area='Bod')

@reactivos.route("/bod/reactivo/<int:reactivo_id>/reduce", methods=['GET', 'POST'])
@login_required
def bod_reduce_reactivo(reactivo_id):
    check_only_bod()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Bod:
        return abort(403)
    form = ReduceReactivoForm()
    if form.validate_on_submit():
        if reactivo.cantidad - form.cantidad.data < 0:
            flash('No se puede dejar la cantidad en numeros negativos', 'danger')
            return redirect(url_for('reactivos.bod_reduce_reactivo', reactivo_id=reactivo.id))
        reactivo.cantidad -= form.cantidad.data
        historial = HistorialReactivos(observacion=form.observacion.data, cantidad=form.cantidad.data, lote=form.lote.data, 
                                        reactivo=reactivo, user = current_user, tipo='Salida', area=Area.Bod)
        db.session.add(historial)
        db.session.commit()
        historial_quimico = HistorialQuimicos(tipo='Reactivo',historial_reactivo=historial, fecha_registro=historial.fecha_registro, area=Area.Bod)
        db.session.add(historial_quimico)
        db.session.commit()
        flash('Se ha añadido la entrada de reactivo', 'success')
        return redirect(url_for('reactivos.bod_reactivo', reactivo_id=reactivo.id))
    return render_template('salida_reactivo.html', title='Menu Reactivo', 
                            form=form, legend='Menu Reactivo', reactivo=reactivo, area='Bod')

@reactivos.route("/bod/reactivo/<int:reactivo_id>/delete", methods=['POST'])
@login_required
def bod_delete_reactivo(reactivo_id):
    check_only_bod()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Bod:
        return abort(403)
    historiales = HistorialReactivos.query.filter_by(reactivo_id=reactivo_id).all()
    quimicos = Quimico.query.filter_by(reactivo_id=reactivo_id).all()
    formulas = Formula.query.filter_by(reactivo_id=reactivo_id).all()
    # Eliminar Tablas dependientes de reactivo
    for historial in historiales:
        q_historiales = HistorialQuimicos.query.filter_by(reactivo_id=historial.id).all()
        for q_historial in q_historiales:
            db.session.delete(q_historial)
        db.session.delete(historial)
    for quimico in quimicos:
        db.session.delete(quimico)
    for formula in formulas:
        Ingrediente.query.filter_by(formula_id = formula.id).delete()
        db.session.delete(formula)
    db.session.delete(reactivo)
    db.session.commit()
    flash('El reactivo se ha eliminado', 'success')
    return redirect(url_for('main.bod_home'))

@reactivos.route("/bod/reactivo/<int:reactivo_id>/formula", methods=['GET', 'POST'])
@login_required
def bod_formula(reactivo_id):
    check_only_bod()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Bod:
        return abort(403)

    if reactivo.tiene_formula:
            flash('Este reactivo ya tiene una formula asociada', 'info')
            return redirect(url_for('reactivos.bod_reactivo', reactivo_id=reactivo.id))

    form = BodNewFormulaForm()
    if form.validate_on_submit():
        formula = Formula(reactivo=reactivo)
        for materia in form.materias.data:
            ing = Ingrediente(ratio=0, materia=materia)
            formula.materias.append(ing)
        db.session.add(formula)
        db.session.commit()
        flash('Ingrese los ratios de las materias seleccionadas', 'info')
        return redirect(url_for('reactivos.bod_ingrediente', reactivo_id=reactivo.id))
    return render_template('formula.html', form=form, legend='Menu Formulas', area='Bod')

@reactivos.route("/bod/reactivo/<int:reactivo_id>/formula/add", methods=['GET', 'POST'])
@login_required
def bod_ingrediente(reactivo_id):
    check_only_bod()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Bod:
        return abort(403)
    
    if reactivo.tiene_formula:
        flash('El reactivo ya tiene una formula ingresada', 'danger')
        return redirect(url_for('reactivos.bod_reactivo', reactivo_id = reactivo.id))

    formula = reactivo.formula
    ingredientes = Ingrediente.query.filter_by(formula_id=formula.id).all()
    form = NewIngrediente()

    if request.method == 'POST':
        form = request.form
        i = 0
        for i in (0, len(ingredientes)-1):
            if not is_number(form['ratio_'+str(i)]):
                flash('Por favor ingrese un numero valido para los ratios', 'warning')
                return render_template('ingredientes.html', form = form, legend = 'Ingrese Ratio', 
                                        ingredientes = ingredientes, len = len(ingredientes), area='Bod')
            else:
                if float(form['ratio_'+str(i)]) <= 0:
                    flash('Por favor ingrese numeros positivos mayores a 0 para los ratios', 'warning')
                    return render_template('ingredientes.html', form = form, legend = 'Ingrese Ratio', 
                                            ingredientes = ingredientes, len = len(ingredientes), area='Bod')

        i = 0
        for ingrediente in ingredientes:
            ingrediente.ratio = form['ratio_'+str(i)]  
            i += 1
        reactivo.tiene_formula = True
        db.session.commit()

        flash('Formula Creada', 'success')     
        return redirect(url_for('reactivos.bod_reactivo', reactivo_id=reactivo.id))

    return render_template('ingredientes.html', form=form, legend='Ingresa Ratio', ingredientes = ingredientes, len = len(ingredientes), area='Bod')

@reactivos.route("/bod/reactivo/<int:reactivo_id>/producir", methods=['GET', 'POST'])
@login_required
def bod_entrada_reactivo(reactivo_id):
    check_only_bod()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Bod:
        return abort(403)
    # print(reactivo.formula)
    if not reactivo.tiene_formula:
        flash('El reactivo no tiene una formula asociada, crea una para poder realizar produccion de reactivo', 'info')
        return redirect(url_for('reactivos.bod_formula', reactivo_id=reactivo.id))
    
    formula = reactivo.formula
    ingredientes = Ingrediente.query.filter_by(formula_id = formula.id).all() 
    for ingrediente in ingredientes:
        if ingrediente.ratio == 0:
            Ingrediente.query.filter_by(formula_id=formula.id).delete()
            db.session.delete(formula)
            db.session.commit()
            flash('El proceso de asignarle formula al reactivo fue detenido antes de finalizar. Para asignarle una formula por favor complete el proceso', 'warning')
            return redirect(url_for('reactivos.bod_formula', reactivo_id = reactivo.id))

    form = ProdReactivoForm()
    if form.validate_on_submit():
        ingredientes = Ingrediente.query.filter_by(formula_id=formula.id)
        flag = True
        for assoc in ingredientes:
            if (assoc.materia.cantidad - form.cantidad.data * assoc.ratio) < 0:
                flag = False
                break
        if flag:
            correlativo = BodCorr.query.first()
            if correlativo:
                correlativo.nro += 1 
                db.session.commit()
            else:
                new_correlativo = BodCorr()
                db.session.add(new_correlativo)
                db.session.commit()

            last = db.session.query(HistorialReactivos).filter(HistorialReactivos.area == Area.Bod).order_by(HistorialReactivos.id.desc()).first()
            año_actual = datetime.utcnow().strftime("%y")
            if last:
                print("EXISTE LAST")
                año_anterior = last.fecha_registro.strftime("%y")
                if año_anterior != año_actual:
                    correlativo = BodCorr.query.first()
                    print("LOS AÑOS SON DIFERENTES")
                    if correlativo:
                        correlativo.nro = 1
                        db.session.commit()
                    else:
                        new_correlativo = BodCorr()
                        db.session.add(new_correlativo)
                        db.session.commit()

            correlativo = BodCorr.query.first()
            nro_correlativo = f'{correlativo.nro:04}'
            nro_analisis = f'{form.nro_analisis.data:04}'
            lote = 'Q'+año_actual+nro_correlativo+nro_analisis
            for assoc in ingredientes:
                # print(assoc.materia.cantidad)
                # print("-")
                # print(assoc.ratio)
                # print(assoc.materia.cantidad - assoc.ratio)
                assoc.materia.cantidad -= (form.cantidad.data * assoc.ratio)
                historial = HistorialMaterias(observacion=f"Produccion de reactivo [{reactivo.id}, {reactivo.nombre}]", 
                                                cantidad=form.cantidad.data*assoc.ratio, materia=assoc.materia, 
                                                user=current_user, tipo='Produccion', area='Bod') # Quizas cambiar el tipo
                db.session.add(historial)
                db.session.commit()
                historial_quimico = HistorialQuimicos(tipo='Materia', historial_materia = historial, 
                                                        fecha_registro = historial.fecha_registro, area='Bod')
                db.session.add(historial_quimico)
                db.session.commit()
            reactivo.cantidad += form.cantidad.data
            historial = HistorialReactivos(observacion=form.observacion.data, cantidad=form.cantidad.data, 
                                            reactivo=reactivo, user=current_user, tipo='Produccion', area='Bod', lote=lote) # Quizas cambiar el tipo
            db.session.add(historial)
            db.session.commit() 
            historial_quimico = HistorialQuimicos(tipo='Reactivo', historial_reactivo = historial, 
                                                    fecha_registro = historial.fecha_registro, area='Bod')
            db.session.add(historial_quimico)
            db.session.commit()
            flash('Se ha producido con exito el reactivo', 'success')
            return redirect(url_for('reactivos.bod_reactivo', reactivo_id=reactivo.id))
        else:
            flash('La cantidad ingresada supera al stock de las materias', 'danger')
            return redirect(url_for('reactivos.bod_entrada_reactivo', reactivo_id=reactivo.id))

    return render_template('producir_reactivo.html', legend='Menu Produccion', form=form, reactivo=reactivo, area='Bod')

@reactivos.route("/bod/reactivo/<int:reactivo_id>/consulta", methods=['GET','POST'])
@login_required
def bod_consulta(reactivo_id):
    check_bod()
    reactivo = Reactivo.query.get_or_404(reactivo_id)
    if reactivo.area != Area.Bod:
        return abort(403)

    if not reactivo.tiene_formula:
        flash('El reactivo no tiene una formula asociada, crea una para poder consultar la produccion de reactivo', 'info')
        return redirect(url_for('reactivos.bod_formula', reactivo_id=reactivo.id))

    formula = reactivo.formula
    ingredientes = Ingrediente.query.filter_by(formula_id = formula.id).all() 
    for ingrediente in ingredientes:
        if ingrediente.ratio == 0:
            Ingrediente.query.filter_by(formula_id = formula.id).delete()
            db.session.delete(formula)
            db.session.commit()
            flash('El proceso de asignarle formula al reactivo fue detenido antes de finalizar. Para asignarle una formula por favor complete el proceso', 'warning')
            return redirect(url_for('reactivos.bod_formula', reactivo_id = reactivo.id))

    form = ConsultaForm()
    if form.validate_on_submit():
        flag = True
        for assoc in ingredientes:
            if (assoc.materia.cantidad - form.cantidad.data * assoc.ratio) < 0:
                flag = False
                break
        if flag:
            flash(f"Es posible crear {form.cantidad.data} {reactivo.medida.value} de reactivo", 'info')
        else:
            flash(f'No es posible crear {form.cantidad.data} {reactivo.medida.value} de reactivo', 'warning')
        return redirect(url_for('reactivos.bod_consulta', reactivo_id = reactivo.id))
    return render_template('consulta.html', form=form, legend='Consulta', reactivo = reactivo, area='Bod')

# ----------------------------------------------------------------------------------------------------------    