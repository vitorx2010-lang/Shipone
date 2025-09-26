# ShipOne API Documentation

## Visão Geral

A API ShipOne fornece endpoints RESTful para gerenciar operações logísticas, incluindo autenticação, gestão de envios, analytics preditivos e notificações.

**Base URL**: `http://localhost:5000/api`

## Autenticação

A API usa autenticação JWT (JSON Web Tokens). Inclua o token no header Authorization:

```
Authorization: Bearer <seu_token_jwt>
```

### Endpoints de Autenticação

#### POST /auth/register
Registra um novo usuário.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string",
  "company": "string",
  "department": "string",
  "phone": "string",
  "role": "user|admin|manager"
}
```

**Response:**
```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "username": "usuario",
    "email": "usuario@email.com",
    "full_name": "Nome Completo",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "company": "Empresa",
    "department": "Departamento",
    "phone": "+55 11 99999-9999"
  }
}
```

#### POST /auth/login
Autentica um usuário e retorna um token JWT.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "usuario",
    "email": "usuario@email.com",
    "role": "user"
  }
}
```

#### GET /auth/profile
Retorna o perfil do usuário autenticado.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "usuario",
    "email": "usuario@email.com",
    "full_name": "Nome Completo",
    "role": "user",
    "company": "Empresa"
  }
}
```

## Logística

### Endpoints de Envios

#### POST /logistics/shipments
Cria um novo envio.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "recipient_name": "string",
  "recipient_email": "string",
  "recipient_phone": "string",
  "origin_address": "string",
  "destination_address": "string",
  "origin_city": "string",
  "destination_city": "string",
  "origin_country": "string",
  "destination_country": "string",
  "weight": 10.5,
  "dimensions": "30x20x10",
  "package_type": "box|envelope|pallet",
  "service_type": "standard|express|overnight",
  "cost": 150.00,
  "currency": "BRL"
}
```

**Response:**
```json
{
  "message": "Shipment created successfully",
  "shipment": {
    "id": 1,
    "tracking_number": "SHP12345678",
    "sender_id": 1,
    "recipient_name": "João Silva",
    "status": "pending",
    "estimated_delivery": "2024-01-08T00:00:00",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

#### GET /logistics/shipments
Lista envios do usuário autenticado.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "shipments": [
    {
      "id": 1,
      "tracking_number": "SHP12345678",
      "recipient_name": "João Silva",
      "origin_city": "São Paulo",
      "destination_city": "Rio de Janeiro",
      "status": "in_transit",
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

#### GET /logistics/shipments/{tracking_number}
Rastreia um envio pelo número de rastreamento (endpoint público).

**Response:**
```json
{
  "shipment": {
    "id": 1,
    "tracking_number": "SHP12345678",
    "recipient_name": "João Silva",
    "status": "in_transit",
    "tracking_events": [
      {
        "id": 1,
        "event_type": "created",
        "description": "Envio criado",
        "location": "São Paulo",
        "timestamp": "2024-01-01T10:00:00"
      },
      {
        "id": 2,
        "event_type": "in_transit",
        "description": "Pacote em trânsito",
        "location": "Centro de distribuição - SP",
        "timestamp": "2024-01-01T14:00:00"
      }
    ]
  }
}
```

#### GET /logistics/analytics/dashboard
Retorna dados analíticos para o dashboard.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "analytics": {
    "total_shipments": 25,
    "pending_shipments": 5,
    "in_transit_shipments": 8,
    "delivered_shipments": 12,
    "service_type_distribution": {
      "standard": 15,
      "express": 8,
      "overnight": 2
    },
    "destination_country_distribution": {
      "Brasil": 20,
      "Estados Unidos": 3,
      "Reino Unido": 2
    }
  }
}
```

## Analytics Avançados

### Predições de Entrega

#### POST /analytics/predictions/delivery/{shipment_id}
Cria uma predição de entrega para um envio.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Delivery prediction created successfully",
  "prediction": {
    "id": 1,
    "shipment_id": 1,
    "predicted_delivery_date": "2024-01-08T15:30:00",
    "confidence_score": 0.87,
    "factors": {
      "service_type": "express",
      "weight": 5.2,
      "weather_factor": 1.05,
      "traffic_factor": 0.98
    }
  }
}
```

#### GET /analytics/predictions/delivery/{shipment_id}
Obtém a predição de entrega para um envio.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "prediction": {
    "id": 1,
    "shipment_id": 1,
    "predicted_delivery_date": "2024-01-08T15:30:00",
    "confidence_score": 0.87,
    "actual_delivery_date": null,
    "accuracy_score": null
  }
}
```

### Otimização de Rotas

#### GET /analytics/route-optimization
Lista otimizações de rota disponíveis.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "optimizations": [
    {
      "id": 1,
      "name": "Rota Otimizada SP-RJ",
      "origin_city": "São Paulo",
      "destination_city": "Rio de Janeiro",
      "estimated_time_hours": 5.5,
      "estimated_cost": 850.00,
      "optimized_route": [
        {"city": "São Paulo", "lat": -23.5505, "lng": -46.6333, "order": 0},
        {"city": "Taubaté", "lat": -23.0205, "lng": -45.5555, "order": 1},
        {"city": "Rio de Janeiro", "lat": -22.9068, "lng": -43.1729, "order": 2}
      ]
    }
  ]
}
```

#### POST /analytics/route-optimization
Cria uma nova otimização de rota (apenas admin).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "string",
  "origin_city": "string",
  "destination_city": "string",
  "waypoints": [
    {"city": "string", "lat": 0, "lng": 0}
  ]
}
```

### Métricas de Performance

#### GET /analytics/performance-metrics
Obtém métricas de performance.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `category` (opcional): delivery, cost, efficiency, customer_satisfaction
- `days` (opcional): número de dias (padrão: 30)

**Response:**
```json
{
  "metrics": [
    {
      "id": 1,
      "metric_name": "Taxa de Entrega no Prazo",
      "metric_value": 87.5,
      "metric_unit": "%",
      "category": "delivery",
      "period_start": "2023-12-01T00:00:00",
      "period_end": "2024-01-01T00:00:00",
      "additional_data": {
        "target": 90.0,
        "improvement_needed": 2.5
      }
    }
  ]
}
```

#### GET /analytics/advanced-dashboard
Obtém dados avançados para dashboard.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "advanced_analytics": {
    "total_shipments": 25,
    "recent_shipments_30d": 15,
    "delivery_performance": {
      "on_time_percentage": 87.5,
      "average_delay_days": 1.2,
      "total_delivered": 20
    },
    "financial_metrics": {
      "total_revenue": 3750.00,
      "average_cost_per_shipment": 150.00,
      "shipments_with_cost": 25
    },
    "top_routes": [
      {"route": "São Paulo → Rio de Janeiro", "count": 8},
      {"route": "São Paulo → Belo Horizonte", "count": 5}
    ],
    "predictive_analytics": {
      "active_predictions": 12,
      "recent_optimizations": 3
    }
  }
}
```

## Notificações

### Endpoints de Notificações

#### GET /notifications/notifications
Lista notificações do usuário.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `unread_only` (opcional): true/false
- `limit` (opcional): número máximo de notificações (padrão: 50)

**Response:**
```json
{
  "notifications": [
    {
      "id": "notif_1234567890",
      "title": "Envio Entregue",
      "message": "Seu envio SHP12345678 foi entregue",
      "type": "success",
      "read": false,
      "created_at": "2024-01-01T10:00:00",
      "metadata": {
        "shipment_id": 1,
        "tracking_number": "SHP12345678"
      }
    }
  ],
  "total_count": 10,
  "unread_count": 3
}
```

#### POST /notifications/notifications/{notification_id}/read
Marca uma notificação como lida.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Notification marked as read"
}
```

#### POST /notifications/notifications/read-all
Marca todas as notificações como lidas.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "All notifications marked as read"
}
```

#### POST /notifications/test
Envia uma notificação de teste.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Test notification sent successfully",
  "notification": {
    "id": "notif_test_123",
    "title": "Notificação de Teste",
    "message": "Esta é uma notificação de teste do sistema ShipOne.",
    "type": "info"
  }
}
```

## Códigos de Status HTTP

- `200 OK` - Requisição bem-sucedida
- `201 Created` - Recurso criado com sucesso
- `400 Bad Request` - Dados inválidos na requisição
- `401 Unauthorized` - Token de autenticação inválido ou ausente
- `403 Forbidden` - Acesso negado (permissões insuficientes)
- `404 Not Found` - Recurso não encontrado
- `500 Internal Server Error` - Erro interno do servidor

## Tratamento de Erros

Todas as respostas de erro seguem o formato:

```json
{
  "message": "Descrição do erro"
}
```

## Rate Limiting

Atualmente não há rate limiting implementado, mas é recomendado para produção.

## Versionamento

A API está na versão 2.0.0. Futuras versões manterão compatibilidade com versões anteriores quando possível.

