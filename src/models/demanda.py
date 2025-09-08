from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Demanda(db.Model):
    __tablename__ = 'demandas'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim_prevista = db.Column(db.Date, nullable=False)
    data_fim_real = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Ativa')  # Ativa, Finalizada, Cancelada
    observacoes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    alocacoes = db.relationship('Alocacao', backref='demanda', lazy=True)

    def __repr__(self):
        return f'<Demanda {self.id} - {self.descricao[:50]}>'

    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'cliente_nome': self.cliente.nome if self.cliente else None,
            'descricao': self.descricao,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim_prevista': self.data_fim_prevista.isoformat() if self.data_fim_prevista else None,
            'data_fim_real': self.data_fim_real.isoformat() if self.data_fim_real else None,
            'status': self.status,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

