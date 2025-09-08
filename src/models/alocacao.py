from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Alocacao(db.Model):
    __tablename__ = 'alocacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    datalogger_id = db.Column(db.Integer, db.ForeignKey('dataloggers.id'), nullable=False)
    demanda_id = db.Column(db.Integer, db.ForeignKey('demandas.id'), nullable=False)
    data_saida = db.Column(db.Date, nullable=False)
    data_retorno_prevista = db.Column(db.Date, nullable=False)
    data_retorno_real = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Em campo')  # Em campo, Retornado
    observacoes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Alocacao {self.id} - DL:{self.datalogger_id} Demanda:{self.demanda_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'datalogger_id': self.datalogger_id,
            'datalogger_numero_serie': self.datalogger.numero_serie if self.datalogger else None,
            'demanda_id': self.demanda_id,
            'demanda_descricao': self.demanda.descricao if self.demanda else None,
            'cliente_nome': self.demanda.cliente.nome if self.demanda and self.demanda.cliente else None,
            'data_saida': self.data_saida.isoformat() if self.data_saida else None,
            'data_retorno_prevista': self.data_retorno_prevista.isoformat() if self.data_retorno_prevista else None,
            'data_retorno_real': self.data_retorno_real.isoformat() if self.data_retorno_real else None,
            'status': self.status,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

