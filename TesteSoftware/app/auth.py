from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required 
from werkzeug.security import check_password_hash
from .models import Usuario
from .forms import LoginForm

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Usuario.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))

        flash('Usuário ou senha inválidos')

    return render_template('auth/login.html', form=form)

@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso.')

    return redirect(url_for('auth.login'))
