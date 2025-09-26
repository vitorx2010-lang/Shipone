# ShipOne - Plataforma Logística Futurista e Preditiva

Uma plataforma completa de gestão logística com recursos avançados de análise preditiva, otimização de rotas e rastreamento em tempo real.

## 🚀 Funcionalidades

### Core Features
- **Autenticação e Autorização**: Sistema completo de login/registro com JWT
- **Gestão de Usuários**: Perfis de usuário com diferentes níveis de acesso
- **Gestão de Envios**: Criação, rastreamento e gerenciamento de envios
- **Rastreamento em Tempo Real**: Acompanhamento detalhado com histórico de eventos

### Features Avançadas
- **Análise Preditiva**: Predição de tempo de entrega usando machine learning
- **Otimização de Rotas**: Algoritmos para otimizar rotas de entrega
- **Sistema de Notificações**: Notificações em tempo real sobre status dos envios
- **Dashboard Analytics**: Métricas avançadas e visualizações de dados
- **Performance Metrics**: Monitoramento de KPIs operacionais

## 🏗️ Arquitetura

### Backend (Flask)
- **API RESTful** com Flask
- **Banco de Dados** SQLite com SQLAlchemy ORM
- **Autenticação** JWT com decorators de segurança
- **CORS** habilitado para integração frontend
- **Modelos de Dados** estruturados para logística

### Frontend (React)
- **Interface Moderna** com React e Tailwind CSS
- **Componentes UI** com shadcn/ui
- **Gráficos Interativos** com Recharts
- **Design Responsivo** para desktop e mobile
- **Navegação SPA** com hash routing

## 📦 Estrutura do Projeto

```
ShipOne/
├── apps/
│   ├── backend/
│   │   └── shipone-backend/
│   │       ├── src/
│   │       │   ├── models/          # Modelos de dados
│   │       │   ├── routes/          # Endpoints da API
│   │       │   ├── utils/           # Utilitários e seeders
│   │       │   └── main.py          # Aplicação principal
│   │       ├── requirements.txt     # Dependências Python
│   │       └── Dockerfile          # Container do backend
│   └── frontend/
│       └── shipone-frontend/
│           ├── src/
│           │   ├── components/      # Componentes React
│           │   └── App.jsx         # Aplicação principal
│           ├── package.json        # Dependências Node.js
│           └── Dockerfile          # Container do frontend
├── infra/
│   └── helm/                       # Charts Helm para deploy
├── docs/                           # Documentação
├── docker-compose.yml              # Orquestração local
└── README.md                       # Este arquivo
```

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- pnpm

### Backend
```bash
cd apps/backend/shipone-backend
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### Frontend
```bash
cd apps/frontend/shipone-frontend
pnpm install
pnpm run dev --host
```

### Docker Compose
```bash
docker-compose up --build
```

## 🔑 Credenciais de Demonstração

### Usuário Admin
- **Usuário**: `admin`
- **Senha**: `admin123`
- **Acesso**: Todas as funcionalidades

### Usuário Demo
- **Usuário**: `demo`
- **Senha**: `demo123`
- **Acesso**: Funcionalidades básicas

## 📊 Dados de Demonstração

O sistema inclui dados pré-populados para demonstração:
- **20 envios** com diferentes status e destinos
- **4 rotas** otimizadas entre principais cidades
- **Eventos de rastreamento** completos
- **Métricas de performance** dos últimos 30 dias

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask** - Framework web Python
- **SQLAlchemy** - ORM para banco de dados
- **Flask-CORS** - Suporte a CORS
- **PyJWT** - Autenticação JWT
- **Werkzeug** - Utilitários web

### Frontend
- **React** - Biblioteca de interface
- **Tailwind CSS** - Framework de estilos
- **shadcn/ui** - Componentes de interface
- **Recharts** - Gráficos e visualizações
- **Lucide React** - Ícones
- **Vite** - Build tool

### DevOps
- **Docker** - Containerização
- **Docker Compose** - Orquestração local

## 📈 Métricas e Analytics

### Dashboard Principal
- Total de envios e status
- Distribuição por tipo de serviço
- Principais destinos
- Envios recentes

### Analytics Avançados
- Taxa de entrega no prazo
- Custo médio por envio
- Satisfação do cliente
- Eficiência de combustível

### Predições
- Tempo estimado de entrega
- Otimização de rotas
- Análise de performance

## 🔄 API Endpoints

### Autenticação
- `POST /api/auth/register` - Registro de usuário
- `POST /api/auth/login` - Login
- `GET /api/auth/profile` - Perfil do usuário

### Logística
- `GET /api/logistics/shipments` - Listar envios
- `POST /api/logistics/shipments` - Criar envio
- `GET /api/logistics/shipments/{tracking}` - Rastrear envio
- `GET /api/logistics/analytics/dashboard` - Dashboard analytics

### Analytics Avançados
- `POST /api/analytics/predictions/delivery/{id}` - Criar predição
- `GET /api/analytics/route-optimization` - Otimizações de rota
- `GET /api/analytics/performance-metrics` - Métricas de performance
- `GET /api/analytics/advanced-dashboard` - Dashboard avançado

### Notificações
- `GET /api/notifications/notifications` - Listar notificações
- `POST /api/notifications/notifications/read-all` - Marcar como lidas
- `POST /api/notifications/test` - Enviar notificação teste

## 🧪 Testes

### Testes de Integração
- Backend Flask inicia corretamente
- Frontend React compila e executa
- Endpoints da API respondem adequadamente

### Dados de Teste
Execute o seeder para popular dados de demonstração:
```bash
cd apps/backend/shipone-backend
PYTHONPATH=/home/ubuntu/Shipone/apps/backend/shipone-backend python src/utils/data_seeder.py
```

## 🚀 Deploy

### Desenvolvimento Local
1. Clone o repositório
2. Execute o backend e frontend separadamente
3. Acesse `http://localhost:5173` para o frontend
4. API disponível em `http://localhost:5000`

### Produção
- Use Docker Compose para deploy completo
- Configure variáveis de ambiente adequadas
- Considere usar banco de dados PostgreSQL em produção

## 📝 Licença

Este projeto é desenvolvido como demonstração de uma plataforma logística moderna e completa.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

**ShipOne** - Transformando o futuro da logística com tecnologia preditiva e inteligência artificial.

