# ShipOne - Guia de Deploy

Este guia fornece instruções detalhadas para fazer deploy da plataforma ShipOne em diferentes ambientes.

## 📋 Pré-requisitos

### Para Deploy Local
- Docker 20.10+
- Docker Compose 2.0+
- Git

### Para Deploy em Produção
- Servidor Linux (Ubuntu 20.04+ recomendado)
- Docker e Docker Compose
- Nginx (para proxy reverso)
- Certificado SSL (Let\'s Encrypt recomendado)
- Domínio configurado

## 🚀 Deploy Local com Docker Compose

### 1. Clone o Repositório
```bash
git clone https://github.com/vitorx2010-lang/Shipone.git
cd Shipone
```

### 2. Configure Variáveis de Ambiente
```bash
# Backend
cp apps/backend/shipone-backend/.env.example apps/backend/shipone-backend/.env

# Frontend
cp apps/frontend/shipone-frontend/.env.example apps/frontend/shipone-frontend/.env
```

### 3. Execute com Docker Compose
```bash
docker-compose up --build
```

### 4. Acesse a Aplicação
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

### 5. Popule Dados de Demonstração
```bash
docker-compose exec backend python src/utils/data_seeder.py
```

## 🏭 Deploy em Produção

### 1. Preparação do Servidor

#### Instalar Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Instalar Nginx
```bash
sudo apt update
sudo apt install nginx
```

### 2. Configuração de Produção

#### Arquivo docker-compose.prod.yml
```yaml
version: \'3.8\'

services:
  backend:
    build: 
      context: ./apps/backend/shipone-backend
      dockerfile: Dockerfile
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    networks:
      - shipone-network

  frontend:
    build:
      context: ./apps/frontend/shipone-frontend
      dockerfile: Dockerfile
    environment:
      - REACT_APP_API_URL=${REACT_APP_API_URL}
    restart: unless-stopped
    networks:
      - shipone-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
    networks:
      - shipone-network

networks:
  shipone-network:
    driver: bridge

volumes:
  postgres_data:
```

#### Configuração do Nginx (nginx.conf)
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:5000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name seu-dominio.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name seu-dominio.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # API routes
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend routes
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 3. Variáveis de Ambiente de Produção

#### .env.prod
```bash
# Backend
SECRET_KEY=sua_chave_secreta_super_segura_aqui
DATABASE_URL=postgresql://user:password@postgres:5432/shipone
FLASK_ENV=production

# Frontend
REACT_APP_API_URL=https://seu-dominio.com/api

# Database
POSTGRES_DB=shipone
POSTGRES_USER=shipone_user
POSTGRES_PASSWORD=senha_super_segura
```

### 4. Deploy em Produção
```bash
# 1. Clone o repositório no servidor
git clone https://github.com/vitorx2010-lang/Shipone.git
cd Shipone

# 2. Configure variáveis de ambiente
cp .env.example .env.prod
# Edite .env.prod com suas configurações

# 3. Execute em produção
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# 4. Verifique os logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔒 Configuração SSL com Let\'s Encrypt

### 1. Instalar Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

### 2. Obter Certificado
```bash
sudo certbot --nginx -d seu-dominio.com
```

### 3. Renovação Automática
```bash
sudo crontab -e
# Adicione a linha:
0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoramento e Logs

### Visualizar Logs
```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Health Checks
```bash
# Backend
curl http://localhost:5000/api/health

# Frontend (verificar se está servindo)
curl http://localhost:3000
```

### Monitoramento de Recursos
```bash
# Status dos containers
docker-compose ps

# Uso de recursos
docker stats
```

## 🔄 Atualizações e Manutenção

### Atualizar a Aplicação
```bash
# 1. Fazer backup do banco de dados
docker-compose exec postgres pg_dump -U shipone_user shipone > backup.sql

# 2. Parar os serviços
docker-compose down

# 3. Atualizar código
git pull origin main

# 4. Rebuild e restart
docker-compose up --build -d

# 5. Verificar saúde
docker-compose logs -f
```

### Backup do Banco de Dados
```bash
# Backup
docker-compose exec postgres pg_dump -U shipone_user shipone > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
docker-compose exec -T postgres psql -U shipone_user shipone < backup.sql
```

## 🐛 Troubleshooting

### Problemas Comuns

#### Container não inicia
```bash
# Verificar logs
docker-compose logs backend

# Verificar configuração
docker-compose config
```

#### Erro de conexão com banco
```bash
# Verificar se o banco está rodando
docker-compose ps postgres

# Verificar logs do banco
docker-compose logs postgres
```

#### Frontend não carrega
```bash
# Verificar se o build foi bem-sucedido
docker-compose logs frontend

# Verificar configuração do Nginx
docker-compose exec nginx nginx -t
```

### Comandos Úteis

#### Limpar recursos Docker
```bash
# Remover containers parados
docker container prune

# Remover imagens não utilizadas
docker image prune

# Limpar tudo (cuidado!)
docker system prune -a
```

#### Acessar container
```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh

# Banco de dados
docker-compose exec postgres psql -U shipone_user shipone
```

## 📈 Otimizações de Performance

### 1. Configuração do Nginx
```nginx
# Adicionar ao nginx.conf
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

# Cache estático
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 2. Configuração do Backend
```python
# Adicionar ao main.py
from flask_compress import Compress

app = Flask(__name__)
Compress(app)
```

### 3. Configuração do Frontend
```javascript
// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: [\'react\', \'react-dom\'],
          ui: [\'@radix-ui/react-dialog\', \'@radix-ui/react-select\']
        }
      }
    }
  }
}
```

## 🔐 Segurança

### Checklist de Segurança
- [ ] Usar HTTPS em produção
- [ ] Configurar firewall (UFW)
- [ ] Usar senhas fortes
- [ ] Configurar rate limiting
- [ ] Manter Docker atualizado
- [ ] Fazer backups regulares
- [ ] Monitorar logs de segurança

### Configuração de Firewall
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
```

## 📞 Suporte

Para problemas de deploy ou configuração:
1. Verifique os logs dos containers
2. Consulte a documentação da API
3. Abra uma issue no repositório GitHub

---

**Nota**: Este guia assume conhecimento básico de Docker, Linux e administração de servidores. Para ambientes de produção críticos, considere consultar um especialista em DevOps.

