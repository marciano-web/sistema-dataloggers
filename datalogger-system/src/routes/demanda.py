from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models.user import db
from src.models.demanda import Demanda
from src.models.cliente import Cliente

demanda_bp = Blueprint('demanda', __name__)

@demanda_bp.route('/demandas', methods=['GET'])
def get_demandas():
    try:
        status_filter = request.args.get('status')
        cliente_filter = request.args.get('cliente_id')
        
        query = Demanda.query
        
        if status_filter:
            query = query.filter(Demanda.status == status_filter)
        if cliente_filter:
            query = query.filter(Demanda.cliente_id == cliente_filter)
            
        demandas = query.all()
        return jsonify([demanda.to_dict() for demanda in demandas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@demanda_bp.route('/demandas', methods=['POST'])
def create_demanda():
    try:
        data = request.get_json()
        
        # Verificar se cliente existe
        cliente = Cliente.query.get(data['cliente_id'])
        if not cliente:
            return jsonify({'error': 'Cliente não encontrado'}), 404
        
        demanda = Demanda(
            cliente_id=data['cliente_id'],
            descricao=data['descricao'],
            data_inicio=datetime.strptime(data['data_inicio'], '%Y-%m-%d').date(),
            data_fim_prevista=datetime.strptime(data['data_fim_prevista'], '%Y-%m-%d').date(),
            status=data.get('status', 'Ativa'),
            observacoes=data.get('observacoes')
        )
        
        if data.get('data_fim_real'):
            demanda.data_fim_real = datetime.strptime(data['data_fim_real'], '%Y-%m-%d').date()
        
        db.session.add(demanda)
        db.session.commit()
        
        return jsonify(demanda.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@demanda_bp.route('/demandas/<int:id>', methods=['GET'])
def get_demanda(id):
    try:
        demanda = Demanda.query.get_or_404(id)
        return jsonify(demanda.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@demanda_bp.route('/demandas/<int:id>', methods=['PUT'])
def update_demanda(id):
    try:
        demanda = Demanda.query.get_or_404(id)
        data = request.get_json()
        
        # Verificar se cliente existe (se fornecido)
        if 'cliente_id' in data:
            cliente = Cliente.query.get(data['cliente_id'])
            if not cliente:
                return jsonify({'error': 'Cliente não encontrado'}), 404
        
        # Atualizar campos básicos
        for field in ['cliente_id', 'descricao', 'status', 'observacoes']:
            if field in data:
                setattr(demanda, field, data[field])
        
        # Converter datas se fornecidas
        if 'data_inicio' in data and data['data_inicio']:
            demanda.data_inicio = datetime.strptime(data['data_inicio'], '%Y-%m-%d').date()
        if 'data_fim_prevista' in data and data['data_fim_prevista']:
            demanda.data_fim_prevista = datetime.strptime(data['data_fim_prevista'], '%Y-%m-%d').date()
        if 'data_fim_real' in data and data['data_fim_real']:
            demanda.data_fim_real = datetime.strptime(data['data_fim_real'], '%Y-%m-%d').date()
        
        demanda.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(demanda.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@demanda_bp.route('/demandas/<int:id>', methods=['DELETE'])
def delete_demanda(id):
    try:
        demanda = Demanda.query.get_or_404(id)
        
        # Verificar se há alocações ativas
        from src.models.alocacao import Alocacao
        alocacoes_ativas = Alocacao.query.filter_by(demanda_id=id, status='Em campo').count()
        if alocacoes_ativas > 0:
            return jsonify({'error': 'Não é possível excluir demanda com alocações ativas'}), 400
        
        db.session.delete(demanda)
        db.session.commit()
        
        return jsonify({'message': 'Demanda excluída com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@demanda_bp.route('/demandas/<int:id>/finalizar', methods=['POST'])
def finalizar_demanda(id):
    try:
        demanda = Demanda.query.get_or_404(id)
        data = request.get_json()
        
        demanda.status = 'Finalizada'
        demanda.data_fim_real = datetime.strptime(data['data_fim_real'], '%Y-%m-%d').date() if data.get('data_fim_real') else date.today()
        demanda.updated_at = datetime.utcnow()
        
        # Finalizar todas as alocações da demanda
        from src.models.alocacao import Alocacao
        from src.models.datalogger import Datalogger
        
        alocacoes = Alocacao.query.filter_by(demanda_id=id, status='Em campo').all()
        for alocacao in alocacoes:
            alocacao.status = 'Retornado'
            alocacao.data_retorno_real = demanda.data_fim_real
            alocacao.updated_at = datetime.utcnow()
            
            # Atualizar status do datalogger para estoque
            datalogger = Datalogger.query.get(alocacao.datalogger_id)
            if datalogger:
                datalogger.status = 'Estoque'
                datalogger.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(demanda.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@demanda_bp.route('/demandas/<int:id>/alocacoes', methods=['GET'])
def get_demanda_alocacoes(id):
    try:
        demanda = Demanda.query.get_or_404(id)
        from src.models.alocacao import Alocacao
        alocacoes = Alocacao.query.filter_by(demanda_id=id).all()
        return jsonify([alocacao.to_dict() for alocacao in alocacoes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

