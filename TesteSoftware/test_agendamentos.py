import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Usuario, Paciente, Atendimento
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='module')
def app():

    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()

        admin = Usuario(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)

        paciente = Paciente(
            nome='Paciente Agendamento',
            cpf='12312312312',
            telefone='11999999999',
            email='agendamento@teste.com'
        )
        db.session.add(paciente)
        db.session.commit()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture(scope='module')
def client(app):

    return app.test_client()


@pytest.fixture(scope='module')
def auth(client, app):

    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    return client


@pytest.fixture(scope='module')
def paciente_id(app):

    with app.app_context():
        paciente = Paciente.query.filter_by(cpf='12312312312').first()
        return paciente.id


def check_flash_message(response, message):
    return message.encode('utf-8') in response.data


def test_1_marcar_agendamento(auth, app, paciente_id):
    with app.app_context():
        data_futura = datetime.now() + timedelta(days=1)
        data_str = data_futura.strftime('%Y-%m-%dT%H:%M')

        response = auth.post('/atendimentos/agendar', data={
            'paciente': paciente_id,
            'data': data_str,
            'descricao': 'Sessão inicial'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert check_flash_message(response, 'Atendimento agendado com sucesso')
        assert Atendimento.query.count() == 1


def test_2_editar_agendamento(auth, app, paciente_id):
    with app.app_context():
        atendimento = Atendimento.query.first()
        nova_data = datetime.now() + timedelta(days=2)
        data_str = nova_data.strftime('%Y-%m-%dT%H:%M')

        response = auth.post(f'/atendimentos/editar/{atendimento.id}', data={
            'paciente': paciente_id,
            'data': data_str,
            'descricao': 'Sessão modificada'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert check_flash_message(response, 'Atendimento atualizado com sucesso')
        assert Atendimento.query.first().descricao == 'Sessão modificada'

def test_3_excluir_agendamento(auth, app):
    with app.app_context():
        atendimento = Atendimento.query.first()
        atendimento_id = atendimento.id

        response = auth.post(f'/atendimentos/excluir/{atendimento_id}',
                             follow_redirects=True)

        assert response.status_code == 200
        assert check_flash_message(response, 'Atendimento excluído com sucesso')
        assert Atendimento.query.get(atendimento_id) is None