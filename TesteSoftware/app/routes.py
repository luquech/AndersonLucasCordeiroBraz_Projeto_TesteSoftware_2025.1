from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from . import db
from .models import Paciente, Atendimento
from .forms import PacienteForm
from datetime import datetime
from .forms import AtendimentoForm

main_routes = Blueprint('main', __name__)


@main_routes.route('/')
@login_required
def index():
    return render_template('index.html')


@main_routes.route('/pacientes/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar_paciente():
    form = PacienteForm()

    if form.validate_on_submit():
        try:

            cpf_limpo = ''.join(filter(str.isdigit, form.cpf.data))
            # Verifica se CPF já existe
            if Paciente.query.filter_by(cpf=cpf_limpo).first():
                flash('CPF já cadastrado no sistema', 'danger')
                return render_template('pacientes/cadastrar.html', form=form)

            paciente = Paciente(
                nome=form.nome.data,
                cpf=cpf_limpo,
                telefone=form.telefone.data,
                email=form.email.data.lower().strip()
            )

            db.session.add(paciente)
            db.session.commit()
            flash('Paciente cadastrado com sucesso!', 'success')
            return redirect(url_for('main.listar_pacientes'))

        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed: paciente.cpf' in str(e):
                flash('CPF já cadastrado no sistema', 'danger')
            else:
                flash(f'Erro ao cadastrar paciente: {str(e)}', 'danger')

    return render_template('pacientes/cadastrar.html', form=form)


# Rota para listar os pacientes
@main_routes.route('/pacientes')
@login_required
def listar_pacientes():
    pacientes = Paciente.query.all()
    return render_template('pacientes/lista.html', pacientes=pacientes)


# Rota para buscar paciente
@main_routes.route('/pacientes/buscar', methods=['GET', 'POST'])
@login_required
def buscar_paciente():
    if request.method == 'POST':
        termo = request.form.get('termo')
        pacientes = Paciente.query.filter(
            (Paciente.nome.contains(termo)) |
            (Paciente.cpf.contains(termo)) |
            (Paciente.email.contains(termo))
        ).all()
        return render_template('pacientes/buscar.html', pacientes=pacientes, termo=termo)

    return render_template('pacientes/buscar.html')


# Rota para editar paciente
@main_routes.route('/pacientes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    form = PacienteForm(obj=paciente)
    form.obj = paciente

    if form.validate_on_submit():
        try:
            paciente.nome = form.nome.data
            paciente.telefone = form.telefone.data
            paciente.email = form.email.data.lower().strip()

            db.session.commit()
            flash('Paciente atualizado com sucesso!', 'success')
            return redirect(url_for('main.listar_pacientes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar paciente: {str(e)}', 'danger')

    return render_template('pacientes/editar.html', form=form, paciente=paciente)


# Rota para excluir paciente
@main_routes.route('/pacientes/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    try:
        db.session.delete(paciente)
        db.session.commit()
        flash('Paciente excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir paciente: {str(e)}', 'danger')

    return redirect(url_for('main.listar_pacientes'))


# Rota para visualizar detalhes do paciente
@main_routes.route('/pacientes/<int:id>')
@login_required
def detalhes_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    atendimentos = Atendimento.query.filter_by(paciente_id=id).order_by(Atendimento.data.desc()).all()
    return render_template('pacientes/detalhes.html', paciente=paciente, atendimentos=atendimentos)


@main_routes.route('/atendimentos/agendar', methods=['GET', 'POST'])
@login_required
def agendar_atendimento():
    form = AtendimentoForm()
    form.paciente.choices = [(p.id, p.nome) for p in Paciente.query.order_by('nome')]

    if form.validate_on_submit():
        atendimento = Atendimento(
            paciente_id=form.paciente.data,
            data=form.data.data,
            descricao=form.descricao.data
        )
        db.session.add(atendimento)
        db.session.commit()
        flash('Atendimento agendado com sucesso!', 'success')
        return redirect(url_for('main.listar_atendimentos'))

    return render_template('atendimentos/agendar.html', form=form)


@main_routes.route('/atendimentos')
@login_required
def listar_atendimentos():
    atendimentos = Atendimento.query.order_by(Atendimento.data.desc()).all()
    return render_template('atendimentos/lista.html', atendimentos=atendimentos)


@main_routes.route('/atendimentos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_atendimento(id):
    atendimento = Atendimento.query.get_or_404(id)
    form = AtendimentoForm(obj=atendimento)

    form.paciente.choices = [(p.id, p.nome) for p in Paciente.query.order_by('nome')]

    if form.validate_on_submit():
        try:
            atendimento.data = form.data.data
            atendimento.descricao = form.descricao.data

            # Atualiza o paciente através do ID
            paciente = Paciente.query.get(form.paciente.data)
            if paciente:
                atendimento.paciente = paciente

            db.session.commit()
            flash('Atendimento atualizado com sucesso!', 'success')
            return redirect(url_for('main.listar_atendimentos'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar atendimento: {str(e)}', 'danger')

    return render_template('atendimentos/editar.html', form=form, atendimento=atendimento)


@main_routes.route('/atendimentos/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_atendimento(id):
    atendimento = Atendimento.query.get_or_404(id)
    db.session.delete(atendimento)
    db.session.commit()
    flash('Atendimento excluído com sucesso!', 'success')
    return redirect(url_for('main.listar_atendimentos'))


