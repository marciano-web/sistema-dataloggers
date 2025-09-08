from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models.user import db
from src.models.alocacao import Alocacao
from src.models.datalogger import Datalogger
from src.models.demanda import Demanda

alocacao_bp = Blueprint('alocacao', __name__)

@alocacao_bp.route('/alocacoes', methods=['GET'])
def get_alocacoes():
    try:
        status_filter = request.args.get('status')
        demanda_filter = request.args.get('demanda_id')
        datalogger_filter = request.args.get('datalogger_id')
        
        query = Alocacao.query
        
        if status_filter:
            query = query.filter(Alocacao.status == status_filter)
        if demanda_filter:
            query = query.filter(Alocacao.demanda_id == demanda_filter)
        if datalogger_filter:
            query = query.filter(Alocacao.datalogger_id == datalogger_filter)
            
        alocacoes = query.all()
        return jsonify([alocacao.to_dict() for alocacao in alocacoes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alocacao_bp.route('/alocacoes', methods=['POST'])
def create_alocacao():
    try:
        data = request.get_json()
        
        # Verificar se datalogger existe e está disponível
        datalogger = Datalogger.query.get(data['datalogger_id'])
        if not datalogger:
            return jsonify({'error': 'Datalogger não encontrado'}), 404
        if datalogger.status != 'Estoque':
            return jsonify({'error': 'Datalogger não está disponível para alocação'}), 400
        
        # Verificar se demanda existe e está ativa
        demanda = Demanda.query.get(data['demanda_id'])
        if not demanda:
            return jsonify({'error': 'Demanda não encontrada'}), 404
        if demanda.status != 'Ativa':
            return jsonify({'error': 'Demanda não está ativa'}), 400
        
        alocacao = Alocacao(
            datalogger_id=data['datalogger_id'],
            demanda_id=data['demanda_id'],
            data_saida=datetime.strptime(data['data_saida'], '%Y-%m-%d').date(),
            data_retorno_prevista=datetime.strptime(data['data_retorno_prevista'], '%Y-%m-%d').date(),
            status='Em campo',
            observacoes=data.get('observacoes')
        )
        
        # Atualizar status do datalogger
        datalogger.status = 'Alocado'
        datalogger.updated_at = datetime.utcnow()
        
        db.session.add(alocacao)
        db.session.commit()
        
        return jsonify(alocacao.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alocacao_bp.route('/alocacoes/<int:id>', methods=['GET'])
def get_alocacao(id):
    try:
        alocacao = Alocacao.query.get_or_404(id)
        return jsonify(alocacao.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alocacao_bp.route('/alocacoes/<int:id>', methods=['PUT'])
def update_alocacao(id):
    try:
        alocacao = Alocacao.query.get_or_404(id)
        data = request.get_json()
        
        # Atualizar campos básicos
        for field in ['observacoes']:
            if field in data:
                setattr(alocacao, field, data[field])
        
        # Converter datas se fornecidas
        if 'data_saida' in data and data['data_saida']:
            alocacao.data_saida = datetime.strptime(data['data_saida'], '%Y-%m-%d').date()
        if 'data_retorno_prevista' in data and data['data_retorno_prevista']:
            alocacao.data_retorno_prevista = datetime.strptime(data['data_retorno_prevista'], '%Y-%m-%d').date()
        if 'data_retorno_real' in data and data['data_retorno_real']:
            alocacao.data_retorno_real = datetime.strptime(data['data_retorno_real'], '%Y-%m-%d').date()
        
        alocacao.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(alocacao.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alocacao_bp.route('/alocacoes/<int:id>/retorno', methods=['POST'])
def registrar_retorno(id):
    try:
        alocacao = Alocacao.query.get_or_404(id)
        data = request.get_json()
        
        if alocacao.status == 'Retornado':
            return jsonify({'error': 'Alocação já foi finalizada'}), 400
        
        # Registrar retorno
        alocacao.status = 'Retornado'
        alocacao.data_retorno_real = datetime.strptime(data['data_retorno_real'], '%Y-%m-%d').date() if data.get('data_retorno_real') else date.today()
        alocacao.updated_at = datetime.utcnow()
        
        if data.get('observacoes'):
            alocacao.observacoes = data['observacoes']
        
        # Atualizar status do datalogger
        datalogger = Datalogger.query.get(alocacao.datalogger_id)
        if datalogger:
            # Verificar se precisa ir para calibração
            if data.get('enviar_calibracao'):
                datalogger.status = 'Calibração'
            else:
                datalogger.status = 'Estoque'
            datalogger.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(alocacao.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alocacao_bp.route('/alocacoes/<int:id>', methods=['DELETE'])
def delete_alocacao(id):
    try:
        alocacao = Alocacao.query.get_or_404(id)
        
        # Se a alocação está em campo, retornar datalogger ao estoque
        if alocacao.status == 'Em campo':
            datalogger = Datalogger.query.get(alocacao.datalogger_id)
            if datalogger:
                datalogger.status = 'Estoque'
                datalogger.updated_at = datetime.utcnow()
        
        db.session.delete(alocacao)
        db.session.commit()
        
        return jsonify({'message': 'Alocação excluída com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alocacao_bp.route('/alocacoes/em-campo', methods=['GET'])
def get_alocacoes_em_campo():
    try:
        alocacoes = Alocacao.query.filter_by(status='Em campo').all()
        return jsonify([alocacao.to_dict() for alocacao in alocacoes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alocacao_bp.route('/alocacoes/retornos-previstos', methods=['GET'])
def get_retornos_previstos():
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = Alocacao.query.filter_by(status='Em campo')
        
        if data_inicio:
            query = query.filter(Alocacao.data_retorno_prevista >= datetime.strptime(data_inicio, '%Y-%m-%d').date())
        if data_fim:
            query = query.filter(Alocacao.data_retorno_prevista <= datetime.strptime(data_fim, '%Y-%m-%d').date())
        
        alocacoes = query.order_by(Alocacao.data_retorno_prevista).all()
        return jsonify([alocacao.to_dict() for alocacao in alocacoes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

