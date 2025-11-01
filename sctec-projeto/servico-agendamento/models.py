from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Cientista(db.Model):
    __tablename__ = 'cientistas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    instituicao = db.Column(db.String(120), nullable=False)

    def to_dict(self):
        return {
            "cientista_id": self.id,
            "nome": self.nome,
            "instituicao": self.instituicao,
            "_links": {
                "self": {"href": f"/cientistas/{self.id}", "method": "GET"},
                "agendamentos": {"href": f"/cientistas/{self.id}/agendamentos", "method": "GET"},
                "criar_agendamento": {"href": "/agendamentos", "method": "POST"},
            }
        }


class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    id = db.Column(db.Integer, primary_key=True)
    cientista_id = db.Column(db.Integer, db.ForeignKey('cientistas.id'), nullable=False)
    horario_inicio_utc = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='CONFIRMADO')

    cientista = db.relationship("Cientista", backref=db.backref("agendamentos", lazy=True))

    def to_dict(self):
        data = {
            "agendamento_id": self.id,
            "cientista_id": self.cientista_id,
            "horario_inicio_utc": self.horario_inicio_utc,
            "status": self.status,
            "_links": {
                "self": {"href": f"/agendamentos/{self.id}", "method": "GET"},
                "cientista": {"href": f"/cientistas/{self.cientista_id}", "method": "GET"}
            }
        }

        if self.status == "CONFIRMADO":
            data["_links"]["cancel"] = {"href": f"/agendamentos/{self.id}/cancelar", "method": "POST"}

        return data
