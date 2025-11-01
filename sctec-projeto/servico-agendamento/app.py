from flask import Flask, jsonify, request
from models import db, Agendamento, Cientista
from datetime import datetime
import logging, json, os

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
    return jsonify({"message": "Serviço de Agendamento ativo!"})

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

@app.route('/cientistas/<int:id>', methods=['PUT'])
def atualizar_cientista(id):
    cientista = Cientista.query.get_or_404(id)
    data = request.get_json()
    cientista.nome = data.get('nome', cientista.nome)
    cientista.instituicao = data.get('instituicao', cientista.instituicao)
    db.session.commit()
    logger.info(f"Cientista {id} atualizado")
    return jsonify(cientista.to_dict())

@app.route('/cientistas/<int:id>', methods=['DELETE'])
def deletar_cientista(id):
    cientista = Cientista.query.get_or_404(id)
    db.session.delete(cientista)
    db.session.commit()
    logger.info(f"Cientista {id} deletado")
    return '', 204

# === CRUD de Agendamentos ===

@app.route('/agendamentos', methods=['POST'])
def criar_agendamento():
    logger.info("Requisição recebida para POST /agendamentos")
    data = request.get_json()
    cientista_id = data['cientista_id']
    horario_inicio = data['horario_inicio_utc']

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

@app.route('/agendamentos', methods=['GET'])
def listar_agendamentos():
    ags = Agendamento.query.all()
    return jsonify([a.to_dict() for a in ags])

@app.route('/agendamentos/<int:id>', methods=['GET'])
def obter_agendamento(id):
    ag = Agendamento.query.get_or_404(id)
    return jsonify(ag.to_dict())

@app.route('/agendamentos/<int:id>', methods=['PUT'])
def atualizar_agendamento(id):
    ag = Agendamento.query.get_or_404(id)
    data = request.get_json()
    ag.status = data.get('status', ag.status)
    db.session.commit()
    logger.info(f"Agendamento {id} atualizado")
    return jsonify(ag.to_dict())

@app.route('/agendamentos/<int:id>', methods=['DELETE'])
def deletar_agendamento(id):
    ag = Agendamento.query.get_or_404(id)
    db.session.delete(ag)
    db.session.commit()
    logger.info(f"Agendamento {id} deletado")
    return '', 204

@app.route('/agendamentos/<int:id>/cancelar', methods=['POST'])
def cancelar_agendamento(id):
    ag = Agendamento.query.get_or_404(id)
    ag.status = "CANCELADO"
    db.session.commit()
    logger.info(f"Agendamento {id} cancelado")

    log_auditoria("AGENDAMENTO_CANCELADO", {
        "agendamento_id": ag.id,
        "cientista_id": ag.cientista_id
    })

    return jsonify(ag.to_dict())

# === ENDPOINT DE TEMPO ===
@app.route('/time', methods=['GET'])
def get_time():
    now = datetime.utcnow().isoformat() + "Z"
    logger.info(f"GET /time chamado. Retornando {now}")
    return jsonify({"server_time_utc": now})

# === MAIN ===
if __name__ == '__main__':
    app.run(debug=True)
