# app.py
from flask import Flask, jsonify, request
from models import db, Agendamento, Cientista
from datetime import datetime
import logging, json, os, requests


COORDENADOR_URL = "http://127.0.0.1:3000"  # Porta do coordenador


# Configuração básica
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# Criar o banco na primeira execução
with app.app_context():
    db.create_all()


# === CONFIGURAÇÃO DE LOGGING ===
log_file = 'app.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(asctime)s:%(name)s:%(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('servico-agendamento')


def log_auditoria(event_type, details):
    registro = {
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "level": "AUDIT",
        "event_type": event_type,
        "service": "servico-agendamento",
        "details": details
    }
    logger.warning(json.dumps(registro))


# === ROTAS ===


@app.route('/')
def home():
    return jsonify({"message": "Serviço de Agendamento ativo e coordenado!"})


# === CRUD de Cientistas ===
@app.route('/cientistas', methods=['POST'])
def criar_cientista():
    data = request.get_json()
    novo = Cientista(nome=data['nome'], instituicao=data['instituicao'])
    db.session.add(novo)
    db.session.commit()
    logger.info("Cientista criado com sucesso")
    return jsonify(novo.to_dict()), 201


@app.route('/cientistas', methods=['GET'])
def listar_cientistas():
    cientistas = Cientista.query.all()
    return jsonify([c.to_dict() for c in cientistas])


@app.route('/cientistas/<int:id>', methods=['GET'])
def obter_cientista(id):
    cientista = Cientista.query.get_or_404(id)
    return jsonify(cientista.to_dict())


# === CRUD de Agendamentos com coordenação ===


@app.route('/agendamentos', methods=['POST'])
def criar_agendamento():
    data = request.get_json()
    cientista_id = data['cientista_id']
    horario_inicio = data['horario_inicio_utc']


    resource_id = f"agendamento_{cientista_id}_{horario_inicio}"
    logger.info(f"Tentando adquirir lock para o recurso {resource_id}")


    try:
        # === Solicita lock ao Coordenador ===
        resp = requests.post(f"{COORDENADOR_URL}/lock", json={"resource_id": resource_id}, timeout=5)
        if resp.status_code == 409:
            logger.info(f"Falha ao adquirir lock, recurso ocupado ({resource_id})")
            return jsonify({"status": "falha", "motivo": "recurso_ocupado"}), 409


        if resp.status_code != 200:
            logger.info(f"Erro inesperado ao tentar adquirir lock ({resp.status_code})")
            return jsonify({"status": "falha", "motivo": "erro_coordenador"}), 500


        logger.info(f"Lock adquirido com sucesso para o recurso {resource_id}")


        # === Cria o agendamento no BD ===
        novo = Agendamento(cientista_id=cientista_id, horario_inicio_utc=horario_inicio)
        db.session.add(novo)
        db.session.commit()
        logger.info("Salvando novo agendamento no BD")


        log_auditoria("AGENDAMENTO_CRIADO", {
            "agendamento_id": novo.id,
            "cientista_id": novo.cientista_id,
            "horario_inicio_utc": novo.horario_inicio_utc
        })


        return jsonify(novo.to_dict()), 201


    finally:
        # === Libera lock ===
        try:
            requests.post(f"{COORDENADOR_URL}/unlock", json={"resource_id": resource_id}, timeout=5)
            logger.info(f"Lock liberado para o recurso {resource_id}")
        except Exception as e:
            logger.info(f"Falha ao liberar lock ({resource_id}): {e}")


@app.route('/agendamentos', methods=['GET'])
def listar_agendamentos():
    ags = Agendamento.query.all()
    return jsonify([a.to_dict() for a in ags])


@app.route('/time', methods=['GET'])
def get_time():
    now = datetime.utcnow().isoformat() + "Z"
    logger.info(f"GET /time chamado. Retornando {now}")
    return jsonify({"server_time_utc": now})


if __name__ == '__main__':
    app.run(debug=True)