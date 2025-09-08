from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Datalogger(db.Model):
    __tablename__ = 'dataloggers'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_serie = db.Column(db.String(100), unique=True, nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Estoque')  # Estoque, Alocado, Calibração, Manutenção
    data_aquisicao = db.Column(db.Date, nullable=True)
    ultima_calibracao = db.Column(db.Date, nullable=True)
    proxima_calibracao = db.Column(db.Date, nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    alocacoes = db.relationship('Alocacao', backref='datalogger', lazy=True)

    def __repr__(self):
        return f'<Datalogger {self.numero_serie}>'

    def to_dict(self):
        return {
            'id': self.id,
            'numero_serie': self.numero_serie,
            'modelo': self.modelo,
            'status': self.status,
            'data_aquisicao': self.data_aquisicao.isoformat() if self.data_aquisicao else None,
            'ultima_calibracao': self.ultima_calibracao.isoformat() if self.ultima_calibracao else None,
            'proxima_calibracao': self.proxima_calibracao.isoformat() if self.proxima_calibracao else None,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

