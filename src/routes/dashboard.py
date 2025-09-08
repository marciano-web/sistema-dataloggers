from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_
from src.models.user import db
from src.models.datalogger import Datalogger
from src.models.cliente import Cliente
from src.models.demanda import Demanda
from src.models.alocacao import Alocacao

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/resumo', methods=['GET'])
def get_resumo_estoque():
    try:
        # Contadores por status de datalogger
        total_dataloggers = Datalogger.query.count()
        em_estoque = Datalogger.query.filter_by(status='Estoque').count()
        alocados = Datalogger.query.filter_by(status='Alocado').count()
        em_calibracao = Datalogger.query.filter_by(status='Calibração').count()
        em_manutencao = Datalogger.query.filter_by(status='Manutenção').count()
        
        # Demandas ativas
        demandas_ativas = Demanda.query.filter_by(status='Ativa').count()
        
        # Alocações em campo
        alocacoes_em_campo = Alocacao.query.filter_by(status='Em campo').count()
        
        # Calibrações vencidas
        hoje = date.today()
        calibracoes_vencidas = Datalogger.query.filter(
            Datalogger.proxima_calibracao <= hoje,
            Datalogger.proxima_calibracao.isnot(None)
        ).count()
        
        # Retornos previstos próximos (próximos 7 dias)
        data_limite = hoje + timedelta(days=7)
        retornos_proximos = Alocacao.query.filter(
            and_(
                Alocacao.status == 'Em campo',
                Alocacao.data_retorno_prevista <= data_limite,
                Alocacao.data_retorno_prevista >= hoje
            )
        ).count()
        
        resumo = {
            'total_dataloggers': total_dataloggers,
            'em_estoque': em_estoque,
            'alocados': alocados,
            'em_calibracao': em_calibracao,
            'em_manutencao': em_manutencao,
            'demandas_ativas': demandas_ativas,
            'alocacoes_em_campo': alocacoes_em_campo,
            'calibracoes_vencidas': calibracoes_vencidas,
            'retornos_proximos': retornos_proximos,
            'taxa_ocupacao': round((alocados / total_dataloggers * 100), 2) if total_dataloggers > 0 else 0
        }
        
        return jsonify(resumo), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/dashboard/disponibilidade', methods=['GET'])
def get_projecao_disponibilidade():
    try:
        dias_projecao = int(request.args.get('dias', 30))
        data_inicio = date.today()
        data_fim = data_inicio + timedelta(days=dias_projecao)
        
        # Buscar todas as alocações em campo com retorno previsto no período
        alocacoes = Alocacao.query.filter(
            and_(
                Alocacao.status == 'Em campo',
                Alocacao.data_retorno_prevista >= data_inicio,
                Alocacao.data_retorno_prevista <= data_fim
            )
        ).order_by(Alocacao.data_retorno_prevista).all()
        
        # Agrupar por data de retorno
        retornos_por_data = {}
        for alocacao in alocacoes:
            data_str = alocacao.data_retorno_prevista.isoformat()
            if data_str not in retornos_por_data:
                retornos_por_data[data_str] = []
            retornos_por_data[data_str].append(alocacao.to_dict())
        
        # Calcular disponibilidade acumulada
        disponibilidade_atual = Datalogger.query.filter_by(status='Estoque').count()
        projecao = []
        
        for i in range(dias_projecao + 1):
            data_atual = data_inicio + timedelta(days=i)
            data_str = data_atual.isoformat()
            
            retornos_dia = len(retornos_por_data.get(data_str, []))
            disponibilidade_atual += retornos_dia
            
            projecao.append({
                'data': data_str,
                'disponibilidade': disponibilidade_atual,
                'retornos': retornos_dia,
                'detalhes_retornos': retornos_por_data.get(data_str, [])
            })
        
        return jsonify({
            'projecao': projecao,
            'disponibilidade_atual': Datalogger.query.filter_by(status='Estoque').count(),
            'total_dataloggers': Datalogger.query.count()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/dashboard/ocupacao-por-cliente', methods=['GET'])
def get_ocupacao_por_cliente():
    try:
        # Buscar alocações ativas agrupadas por cliente
        resultado = db.session.query(
            Cliente.nome,
            func.count(Alocacao.id).label('quantidade_alocacoes')
        ).join(
            Demanda, Cliente.id == Demanda.cliente_id
        ).join(
            Alocacao, Demanda.id == Alocacao.demanda_id
        ).filter(
            Alocacao.status == 'Em campo'
        ).group_by(Cliente.id, Cliente.nome).all()
        
        ocupacao = [
            {
                'cliente': nome,
                'quantidade': quantidade
            }
            for nome, quantidade in resultado
        ]
        
        return jsonify(ocupacao), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/dashboard/alertas', methods=['GET'])
def get_alertas():
    try:
        alertas = []
        hoje = date.today()
        
        # Calibrações vencidas
        calibracoes_vencidas = Datalogger.query.filter(
            Datalogger.proxima_calibracao <= hoje,
            Datalogger.proxima_calibracao.isnot(None)
        ).all()
        
        for dl in calibracoes_vencidas:
            dias_vencido = (hoje - dl.proxima_calibracao).days
            alertas.append({
                'tipo': 'calibracao_vencida',
                'prioridade': 'alta',
                'mensagem': f'Datalogger {dl.numero_serie} com calibração vencida há {dias_vencido} dias',
                'datalogger_id': dl.id,
                'data_vencimento': dl.proxima_calibracao.isoformat()
            })
        
        # Calibrações próximas (próximos 30 dias)
        data_limite = hoje + timedelta(days=30)
        calibracoes_proximas = Datalogger.query.filter(
            and_(
                Datalogger.proxima_calibracao > hoje,
                Datalogger.proxima_calibracao <= data_limite,
                Datalogger.proxima_calibracao.isnot(None)
            )
        ).all()
        
        for dl in calibracoes_proximas:
            dias_restantes = (dl.proxima_calibracao - hoje).days
            alertas.append({
                'tipo': 'calibracao_proxima',
                'prioridade': 'media',
                'mensagem': f'Datalogger {dl.numero_serie} precisa de calibração em {dias_restantes} dias',
                'datalogger_id': dl.id,
                'data_vencimento': dl.proxima_calibracao.isoformat()
            })
        
        # Retornos atrasados
        alocacoes_atrasadas = Alocacao.query.filter(
            and_(
                Alocacao.status == 'Em campo',
                Alocacao.data_retorno_prevista < hoje
            )
        ).all()
        
        for alocacao in alocacoes_atrasadas:
            dias_atraso = (hoje - alocacao.data_retorno_prevista).days
            alertas.append({
                'tipo': 'retorno_atrasado',
                'prioridade': 'alta',
                'mensagem': f'Datalogger {alocacao.datalogger.numero_serie} está {dias_atraso} dias em atraso',
                'alocacao_id': alocacao.id,
                'datalogger_id': alocacao.datalogger_id,
                'demanda_id': alocacao.demanda_id,
                'dias_atraso': dias_atraso
            })
        
        # Ordenar por prioridade
        ordem_prioridade = {'alta': 0, 'media': 1, 'baixa': 2}
        alertas.sort(key=lambda x: ordem_prioridade.get(x['prioridade'], 3))
        
        return jsonify(alertas), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/dashboard/historico-ocupacao', methods=['GET'])
def get_historico_ocupacao():
    try:
        dias_historico = int(request.args.get('dias', 30))
        data_fim = date.today()
        data_inicio = data_fim - timedelta(days=dias_historico)
        
        # Buscar alocações que estavam ativas no período
        alocacoes = Alocacao.query.filter(
            and_(
                Alocacao.data_saida <= data_fim,
                db.or_(
                    Alocacao.data_retorno_real.is_(None),
                    Alocacao.data_retorno_real >= data_inicio
                )
            )
        ).all()
        
        # Calcular ocupação por dia
        historico = []
        total_dataloggers = Datalogger.query.count()
        
        for i in range(dias_historico + 1):
            data_atual = data_inicio + timedelta(days=i)
            
            # Contar quantos dataloggers estavam alocados nesta data
            alocados_na_data = 0
            for alocacao in alocacoes:
                if (alocacao.data_saida <= data_atual and 
                    (alocacao.data_retorno_real is None or alocacao.data_retorno_real >= data_atual)):
                    alocados_na_data += 1
            
            taxa_ocupacao = (alocados_na_data / total_dataloggers * 100) if total_dataloggers > 0 else 0
            
            historico.append({
                'data': data_atual.isoformat(),
                'alocados': alocados_na_data,
                'disponivel': total_dataloggers - alocados_na_data,
                'taxa_ocupacao': round(taxa_ocupacao, 2)
            })
        
        return jsonify(historico), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

