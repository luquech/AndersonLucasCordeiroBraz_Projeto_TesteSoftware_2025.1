from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from app.models import Paciente
from datetime import datetime
import re

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class PacienteForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[
        DataRequired(message="Campo obrigatório"),
        Length(min=3, max=100, message="Deve ter entre 3 e 100 caracteres")
    ])
    telefone = StringField('Telefone', validators=[
        DataRequired(message="Campo obrigatório")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Campo obrigatório"),
        Email(message="Email inválido")
    ])
    submit = SubmitField('Salvar')

    cpf = StringField('CPF', validators=[
        DataRequired(message="Campo obrigatório"),
        Length(min=11, max=14, message="CPF deve ter 11 dígitos")
    ])

    def validate_cpf(self, field):
        cpf = re.sub(r'[^0-9]', '', field.data)

        if len(cpf) != 11 or cpf == cpf[0] * 11:
            raise ValidationError('CPF inválido')

        if hasattr(self, 'obj') and self.obj:
            if cpf != self.obj.cpf:
                raise ValidationError('Não é permitido alterar o CPF')
        else:
            paciente = Paciente.query.filter_by(cpf=cpf).first()
            if paciente:
                raise ValidationError('CPF já cadastrado no sistema')

class AtendimentoForm(FlaskForm):
    paciente = SelectField('Paciente', coerce=int, validators=[DataRequired()])
    data = DateTimeLocalField('Data e Hora',
                            format='%Y-%m-%dT%H:%M',
                            validators=[DataRequired()])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    submit = SubmitField('Atualizar')

