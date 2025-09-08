from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models.user import db
from src.models.datalogger import Datalogger

datalogger_bp = Blueprint('datalogger', __name__)

@datalogger_bp.route('/dataloggers', methods=['GET'])
def get_dataloggers():
    try:
        status_filter = request.args.get('status')
        query = Datalogger.query
        
        if status_filter:
            query = query.filter(Datalogger.status == status_filter)
            
        dataloggers = query.all()
        return jsonify([dl.to_dict() for dl in dataloggers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@datalogger_bp.route('/dataloggers', methods=['POST'])
def create_datalogger():
    try:
        data = request.get_json()
        
        # Verificar se número de série já existe
        existing = Datalogger.query.filter_by(numero_serie=data['numero_serie']).first()
        if existing:
            return jsonify({'error': 'Número de série já existe'}), 400
        
        datalogger = Datalogger(
            numero_serie=data['numero_serie'],
            modelo=data['modelo'],
            status=data.get('status', 'Estoque'),
            observacoes=data.get('observacoes')
        )
        
        # Converter datas se fornecidas
        if data.get('data_aquisicao'):
            datalogger.data_aquisicao = datetime.strptime(data['data_aquisicao'], '%Y-%m-%d').date()
        if data.get('ultima_calibracao'):
            datalogger.ultima_calibracao = datetime.strptime(data['ultima_calibracao'], '%Y-%m-%d').date()
        if data.get('proxima_calibracao'):
            datalogger.proxima_calibracao = datetime.strptime(data['proxima_calibracao'], '%Y-%m-%d').date()
        
        db.session.add(datalogger)
        db.session.commit()
        
        return jsonify(datalogger.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@datalogger_bp.route('/dataloggers/<int:id>', methods=['GET'])
def get_datalogger(id):
    try:
        datalogger = Datalogger.query.get_or_404(id)
        return jsonify(datalogger.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@datalogger_bp.route('/dataloggers/<int:id>', methods=['PUT'])
def update_datalogger(id):
    try:
        datalogger = Datalogger.query.get_or_404(id)
        data = request.get_json()
        
        # Verificar se número de série já existe em outro datalogger
        if 'numero_serie' in data and data['numero_serie'] != datalogger.numero_serie:
            existing = Datalogger.query.filter_by(numero_serie=data['numero_serie']).first()
            if existing:
                return jsonify({'error': 'Número de série já existe'}), 400
        
        # Atualizar campos
        for field in ['numero_serie', 'modelo', 'status', 'observacoes']:
            if field in data:
                setattr(datalogger, field, data[field])
        
        # Converter datas se fornecidas
        if 'data_aquisicao' in data and data['data_aquisicao']:
            datalogger.data_aquisicao = datetime.strptime(data['data_aquisicao'], '%Y-%m-%d').date()
        if 'ultima_calibracao' in data and data['ultima_calibracao']:
            datalogger.ultima_calibracao = datetime.strptime(data['ultima_calibracao'], '%Y-%m-%d').date()
        if 'proxima_calibracao' in data and data['proxima_calibracao']:
            datalogger.proxima_calibracao = datetime.strptime(data['proxima_calibracao'], '%Y-%m-%d').date()
        
        datalogger.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(datalogger.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@datalogger_bp.route('/dataloggers/<int:id>', methods=['DELETE'])
def delete_datalogger(id):
    try:
        datalogger = Datalogger.query.get_or_404(id)
        
        # Verificar se há alocações ativas
        from src.models.alocacao import Alocacao
        alocacoes_ativas = Alocacao.query.filter_by(datalogger_id=id, status='Em campo').count()
        if alocacoes_ativas > 0:
            return jsonify({'error': 'Não é possível excluir datalogger com alocações ativas'}), 400
        
        db.session.delete(datalogger)
        db.session.commit()
        
        return jsonify({'message': 'Datalogger excluído com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@datalogger_bp.route('/dataloggers/disponveis', methods=['GET'])
def get_dataloggers_disponveis():
    try:
        dataloggers = Datalogger.query.filter_by(status='Estoque').all()
        return jsonify([dl.to_dict() for dl in dataloggers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@datalogger_bp.route('/dataloggers/calibracao-vencida', methods=['GET'])
def get_dataloggers_calibracao_vencida():
    try:
        hoje = date.today()
        dataloggers = Datalogger.query.filter(
            Datalogger.proxima_calibracao <= hoje,
            Datalogger.proxima_calibracao.isnot(None)
        ).all()
        return jsonify([dl.to_dict() for dl in dataloggers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

