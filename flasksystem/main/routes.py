from flask import render_template, url_for, redirect, request, Blueprint
from flask_login import current_user, login_required
from flasksystem.models import HistorialQuimicos, Quimico, Area
from flasksystem.main.utils import check_lab, check_bod

main = Blueprint('main', __name__)

@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return render_template('index.html')

@main.route("/home")
@login_required
def home():
    if current_user.area == Area.Lab:
        return redirect(url_for('main.lab_home'))
    elif current_user.area == Area.Bod:
        return redirect(url_for('main.bod_home'))
    else:
        return render_template('home.html', title='Home')

@main.route("/about")
def about():
    return render_template('about.html', title='About')

@main.route("/home/historial")
@login_required
def home_historial():
    historiales = HistorialQuimicos.query.order_by(HistorialQuimicos.fecha_registro.desc()).all()
    return render_template('ver_historial.html', historiales=historiales)

@main.route("/lab")
@login_required
def lab_home():
    check_lab()
    quimicos = Quimico.query.filter_by(area=Area.Lab).all()
    return render_template('lab/home.html', title='Lab Home', quimicos=quimicos, area='Lab', user=current_user)

@main.route("/lab/historial")
@login_required
def lab_home_historial():
    check_lab()
    historiales = HistorialQuimicos.query.filter_by(area=Area.Lab).order_by(HistorialQuimicos.fecha_registro.desc()).all()
    return render_template('ver_historial.html', historiales=historiales, area='Lab')

@main.route("/bod")
@login_required
def bod_home():
    check_bod()
    quimicos = Quimico.query.filter_by(area=Area.Bod).all()
    return render_template('bod/home.html', title='Bod Home', quimicos=quimicos, area='Bod', user=current_user)

@main.route("/bod/historial")
@login_required
def bod_home_historial():
    check_bod()
    historiales = HistorialQuimicos.query.filter_by(area=Area.Bod).order_by(HistorialQuimicos.fecha_registro.desc()).all()
    return render_template('ver_historial.html', historiales=historiales, area='Bod')