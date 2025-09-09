import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.datalogger import datalogger_bp
from src.routes.cliente import cliente_bp
from src.routes.demanda import demanda_bp
from src.routes.alocacao import alocacao_bp
from src.routes.dashboard import dashboard_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Habilitar CORS para permitir requisições do frontend
CORS(app)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(datalogger_bp, url_prefix='/api')
app.register_blueprint(cliente_bp, url_prefix='/api')
app.register_blueprint(demanda_bp, url_prefix='/api')
app.register_blueprint(alocacao_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api')

# Configuração do banco de dados - PostgreSQL primeiro, SQLite como fallback
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # PostgreSQL (Railway) - corrigir URL se necessário
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"🐘 Usando PostgreSQL: {database_url[:50]}...")
else:
    # SQLite (desenvolvimento local)
    sqlite_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{sqlite_path}"
    print(f"📁 Usando SQLite: {sqlite_path}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Importar todos os modelos para garantir que as tabelas sejam criadas
from src.models.datalogger import Datalogger
from src.models.cliente import Cliente
from src.models.demanda import Demanda
from src.models.alocacao import Alocacao

db.init_app(app)

try:
    with app.app_context():
        # Criar diretório do banco se for SQLite
        if not database_url:
            os.makedirs(os.path.join(os.path.dirname(__file__), 'database'), exist_ok=True)
        
        print("🔄 Criando tabelas do banco de dados...")
        db.create_all()
        print("✅ Tabelas criadas com sucesso!")
        
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/health')
def health_check():
    return {"status": "ok", "database": "connected"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print(f"🚀 Iniciando aplicação na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
