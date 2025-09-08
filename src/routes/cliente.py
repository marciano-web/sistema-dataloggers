from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.user import db
from src.models.cliente import Cliente

cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route('/clientes', methods=['GET'])
def get_clientes():
    try:
        clientes = Cliente.query.all()
        return jsonify([cliente.to_dict() for cliente in clientes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cliente_bp.route('/clientes', methods=['POST'])
def create_cliente():
    try:
        data = request.get_json()
        
        cliente = Cliente(
            nome=data['nome'],
            contato=data.get('contato'),
            telefone=data.get('telefone'),
            email=data.get('email'),
            endereco=data.get('endereco')
        )
        
        db.session.add(cliente)
        db.session.commit()
        
        return jsonify(cliente.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cliente_bp.route('/clientes/<int:id>', methods=['GET'])
def get_cliente(id):
    try:
        cliente = Cliente.query.get_or_404(id)
        return jsonify(cliente.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cliente_bp.route('/clientes/<int:id>', methods=['PUT'])
def update_cliente(id):
    try:
        cliente = Cliente.query.get_or_404(id)
        data = request.get_json()
        
        # Atualizar campos
        for field in ['nome', 'contato', 'telefone', 'email', 'endereco']:
            if field in data:
                setattr(cliente, field, data[field])
        
        cliente.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(cliente.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cliente_bp.route('/clientes/<int:id>', methods=['DELETE'])
def delete_cliente(id):
    try:
        cliente = Cliente.query.get_or_404(id)
        
        # Verificar se há demandas ativas
        from src.models.demanda import Demanda
        demandas_ativas = Demanda.query.filter_by(cliente_id=id, status='Ativa').count()
        if demandas_ativas > 0:
            return jsonify({'error': 'Não é possível excluir cliente com demandas ativas'}), 400
        
        db.session.delete(cliente)
        db.session.commit()
        
        return jsonify({'message': 'Cliente excluído com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cliente_bp.route('/clientes/<int:id>/demandas', methods=['GET'])
def get_cliente_demandas(id):
    try:
        cliente = Cliente.query.get_or_404(id)
        from src.models.demanda import Demanda
        demandas = Demanda.query.filter_by(cliente_id=id).all()
        return jsonify([demanda.to_dict() for demanda in demandas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

