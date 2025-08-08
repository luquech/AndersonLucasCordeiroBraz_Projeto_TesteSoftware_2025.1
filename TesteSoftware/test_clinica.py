import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Usuario, Paciente, Atendimento
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()

        # Cria usuário admin apenas se não existir
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth(client, app):
    with app.app_context():
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()

    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    return client

def test_cadastrar_paciente(auth, app):
    with app.app_context():
        response = auth.post('/pacientes/cadastrar', data={
            'nome': 'Novo Paciente',
            'cpf': '98765432109',
            'telefone': '11988888888',
            'email': 'novo@teste.com'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Paciente cadastrado com sucesso' in response.data
        assert Paciente.query.filter_by(cpf='98765432109').first() is not None


def test_cpf_duplicado(auth, app):
    with app.app_context():
        # Cria um paciente
        paciente = Paciente(
            nome='Paciente Existente',
            cpf='12345678901',
            telefone='11999999999',
            email='existente@teste.com'
        )
        db.session.add(paciente)
        db.session.commit()

        # Tenta criar com mesmo CPF
        response = auth.post('/pacientes/cadastrar', data={
            'nome': 'Paciente Duplicado',
            'cpf': '12345678901',
            'telefone': '11977777777',
            'email': 'duplicado@teste.com'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'CPF j' in response.data  # "CPF já cadastrado"


def test_cpf_invalido(auth, app):
    with app.app_context():
        response = auth.post('/pacientes/cadastrar', data={
            'nome': 'Paciente Invalido',
            'cpf': '111',  # CPF inválido
            'telefone': '11966666666',
            'email': 'invalido@teste.com'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'CPF inv' in response.data  # "CPF inválido"


def test_editar_paciente(auth, app):
    with app.app_context():
        # Cria paciente para editar
        paciente = Paciente(
            nome='Paciente Original',
            cpf='11122233344',
            telefone='11955555555',
            email='original@teste.com'
        )
        db.session.add(paciente)
        db.session.commit()

        response = auth.post(f'/pacientes/editar/{paciente.id}', data={
            'nome': 'Paciente Editado',
            'cpf': '11122233344',  # Mesmo CPF
            'telefone': '11944444444',
            'email': 'editado@teste.com'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Paciente atualizado com sucesso' in response.data
        paciente = Paciente.query.get(paciente.id)
        assert paciente.nome == 'Paciente Editado'


def test_excluir_paciente(auth, app):
    with app.app_context():
        # Cria paciente para excluir
        paciente = Paciente(
            nome='Paciente para Excluir',
            cpf='99999999999',
            telefone='11933333333',
            email='excluir@teste.com'
        )
        db.session.add(paciente)
        db.session.commit()

        response = auth.post(f'/pacientes/excluir/{paciente.id}',
                             follow_redirects=True)

        assert response.status_code == 200
        assert b'Paciente exclu' in response.data  # "Paciente excluído"
        assert Paciente.query.get(paciente.id) is None