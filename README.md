# Sistema de Controle de Dataloggers

Uma aplicação web completa para gerenciamento de estoque de dataloggers, controle de alocações e projeção de disponibilidade.

## 🚀 Funcionalidades

- **Dashboard Executivo**: Métricas em tempo real e alertas
- **Gestão de Dataloggers**: Cadastro, edição e controle de status
- **Controle de Demandas**: Gerenciamento de projetos e clientes
- **Alocações**: Rastreamento de equipamentos em campo
- **Projeção de Disponibilidade**: Planejamento futuro baseado em retornos

## 🛠 Tecnologias

- **Backend**: Flask + SQLite
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Deploy**: Railway (recomendado) ou qualquer plataforma compatível

## 📦 Deploy no Railway

### 1. Preparar o Repositório GitHub

1. Crie um novo repositório no GitHub
2. Clone este projeto ou faça upload dos arquivos
3. Certifique-se de que todos os arquivos estão commitados

### 2. Deploy no Railway

1. Acesse [railway.app](https://railway.app)
2. Faça login com sua conta GitHub
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Escolha o repositório do projeto
6. O Railway detectará automaticamente que é um projeto Python

### 3. Configuração Automática

O Railway irá:
- Detectar o `requirements.txt` e instalar dependências
- Usar o `Procfile` para iniciar a aplicação
- Configurar automaticamente a porta via variável `PORT`

### 4. Variáveis de Ambiente (Opcional)

Se necessário, configure no Railway:
- `FLASK_ENV=production` (para desabilitar debug)
- `SECRET_KEY=sua-chave-secreta-aqui` (para segurança)

## 🔧 Desenvolvimento Local

### Pré-requisitos
- Python 3.8+
- Node.js 16+ (para desenvolvimento do frontend)

### Backend
```bash
cd datalogger-system
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install -r requirements.txt
python src/main.py
```

### Frontend (Desenvolvimento)
```bash
cd datalogger-frontend
npm install
npm run dev
```

### Build de Produção
```bash
cd datalogger-frontend
npm run build
cp -r dist/* ../datalogger-system/src/static/
```

## 📁 Estrutura do Projeto

```
datalogger-system/
├── src/
│   ├── main.py              # Aplicação principal
│   ├── models/              # Modelos do banco de dados
│   ├── routes/              # Rotas da API
│   ├── static/              # Frontend buildado
│   └── database/            # Banco SQLite
├── requirements.txt         # Dependências Python
├── Procfile                # Configuração Railway
├── railway.json            # Configuração Railway
└── README.md               # Este arquivo
```

## 🌐 URLs da API

- `GET /api/dataloggers` - Listar dataloggers
- `POST /api/dataloggers` - Criar datalogger
- `PUT /api/dataloggers/{id}` - Atualizar datalogger
- `DELETE /api/dataloggers/{id}` - Deletar datalogger
- `GET /api/dashboard/resumo` - Métricas do dashboard
- `GET /api/dashboard/disponibilidade` - Projeção de disponibilidade

## 🔒 Segurança

- CORS configurado para permitir requisições do frontend
- Validação de dados nos formulários
- Sanitização de inputs
- Configuração de produção com debug desabilitado

## 📊 Status dos Dataloggers

- **Estoque**: Disponível para alocação
- **Alocado**: Em uso em campo
- **Calibração**: Enviado para calibração
- **Manutenção**: Em reparo

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique os logs no Railway Dashboard
2. Confirme se todas as dependências estão no `requirements.txt`
3. Verifique se o frontend foi buildado corretamente

## 📝 Licença

Este projeto foi desenvolvido para controle interno de dataloggers.

---

**Desenvolvido com ❤️ usando Flask + React**

