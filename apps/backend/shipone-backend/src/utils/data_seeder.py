from src.models.user import User, db
from src.models.logistics import Shipment, TrackingEvent, Route
from src.models.analytics import PredictiveModel, DeliveryPrediction, RouteOptimization, PerformanceMetric
from datetime import datetime, timedelta
import random
import string

def generate_tracking_number():
    """Gera um número de rastreamento único"""
    prefix = "SHP"
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}{suffix}"

def seed_demo_data():
    """Popula o banco com dados de demonstração"""
    try:
        # Criar usuário admin se não existir
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@shipone.com',
                full_name='Administrador ShipOne',
                role='admin',
                company='ShipOne Corp',
                department='Administração',
                phone='+55 11 99999-9999'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
        
        # Criar usuário demo se não existir
        demo_user = User.query.filter_by(username='demo').first()
        if not demo_user:
            demo_user = User(
                username='demo',
                email='demo@shipone.com',
                full_name='Usuário Demonstração',
                role='user',
                company='Demo Logistics',
                department='Operações',
                phone='+55 11 88888-8888'
            )
            demo_user.set_password('demo123')
            db.session.add(demo_user)
        
        db.session.commit()
        
        # Criar rotas de exemplo
        routes_data = [
            {
                'name': 'São Paulo - Rio de Janeiro',
                'origin_city': 'São Paulo',
                'destination_city': 'Rio de Janeiro',
                'distance_km': 430,
                'estimated_duration_hours': 6,
                'transport_mode': 'truck'
            },
            {
                'name': 'São Paulo - Belo Horizonte',
                'origin_city': 'São Paulo',
                'destination_city': 'Belo Horizonte',
                'distance_km': 586,
                'estimated_duration_hours': 8,
                'transport_mode': 'truck'
            },
            {
                'name': 'Rio de Janeiro - Salvador',
                'origin_city': 'Rio de Janeiro',
                'destination_city': 'Salvador',
                'distance_km': 1649,
                'estimated_duration_hours': 20,
                'transport_mode': 'truck'
            },
            {
                'name': 'São Paulo - Miami',
                'origin_city': 'São Paulo',
                'destination_city': 'Miami',
                'distance_km': 6500,
                'estimated_duration_hours': 12,
                'transport_mode': 'plane'
            }
        ]
        
        for route_data in routes_data:
            existing_route = Route.query.filter_by(
                origin_city=route_data['origin_city'],
                destination_city=route_data['destination_city']
            ).first()
            
            if not existing_route:
                route = Route(**route_data)
                db.session.add(route)
        
        # Criar envios de exemplo
        cities = [
            ('São Paulo', 'Brasil'),
            ('Rio de Janeiro', 'Brasil'),
            ('Belo Horizonte', 'Brasil'),
            ('Salvador', 'Brasil'),
            ('Brasília', 'Brasil'),
            ('Miami', 'Estados Unidos'),
            ('New York', 'Estados Unidos'),
            ('Londres', 'Reino Unido'),
            ('Paris', 'França'),
            ('Tóquio', 'Japão')
        ]
        
        recipients = [
            'João Silva',
            'Maria Santos',
            'Pedro Oliveira',
            'Ana Costa',
            'Carlos Ferreira',
            'Lucia Rodrigues',
            'Roberto Lima',
            'Fernanda Alves',
            'Marcos Pereira',
            'Juliana Souza'
        ]
        
        service_types = ['standard', 'express', 'overnight']
        package_types = ['box', 'envelope', 'pallet']
        statuses = ['pending', 'in_transit', 'out_for_delivery', 'delivered']
        
        # Criar 20 envios de exemplo
        for i in range(20):
            origin_city, origin_country = random.choice(cities)
            destination_city, destination_country = random.choice(cities)
            
            # Evitar origem e destino iguais
            while destination_city == origin_city:
                destination_city, destination_country = random.choice(cities)
            
            tracking_number = generate_tracking_number()
            
            # Verificar se já existe
            existing_shipment = Shipment.query.filter_by(tracking_number=tracking_number).first()
            if existing_shipment:
                continue
            
            service_type = random.choice(service_types)
            created_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            
            # Calcular data estimada de entrega
            if service_type == 'overnight':
                estimated_delivery = created_date + timedelta(days=1)
            elif service_type == 'express':
                estimated_delivery = created_date + timedelta(days=3)
            else:
                estimated_delivery = created_date + timedelta(days=7)
            
            shipment = Shipment(
                tracking_number=tracking_number,
                sender_id=demo_user.id,
                recipient_name=random.choice(recipients),
                origin_address=f'Rua Exemplo, 123 - {origin_city}',
                destination_address=f'Avenida Destino, 456 - {destination_city}',
                origin_city=origin_city,
                destination_city=destination_city,
                origin_country=origin_country,
                destination_country=destination_country,
                weight=round(random.uniform(0.5, 50.0), 2),
                package_type=random.choice(package_types),
                service_type=service_type
            )
            
            shipment.recipient_email = f'{recipients[i % len(recipients)].lower().replace(" ", ".")}@email.com'
            shipment.recipient_phone = f'+55 11 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}'
            shipment.dimensions = f'{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 30)}'
            shipment.cost = round(random.uniform(50, 500), 2)
            shipment.currency = 'BRL'
            shipment.estimated_delivery = estimated_delivery
            shipment.created_at = created_date
            shipment.status = random.choice(statuses)
            
            # Se foi entregue, definir data de entrega
            if shipment.status == 'delivered':
                delivery_variance = random.randint(-2, 3)  # Pode ser entregue até 2 dias antes ou 3 dias depois
                shipment.actual_delivery = estimated_delivery + timedelta(days=delivery_variance)
            
            db.session.add(shipment)
            db.session.commit()
            
            # Criar eventos de rastreamento
            events = [
                ('created', 'Envio criado e aguardando coleta', origin_city),
            ]
            
            if shipment.status in ['in_transit', 'out_for_delivery', 'delivered']:
                events.append(('pickup', 'Pacote coletado', origin_city))
                events.append(('in_transit', 'Pacote em trânsito', f'Centro de distribuição - {origin_city}'))
            
            if shipment.status in ['out_for_delivery', 'delivered']:
                events.append(('in_transit', 'Pacote chegou ao destino', f'Centro de distribuição - {destination_city}'))
                events.append(('out_for_delivery', 'Saiu para entrega', destination_city))
            
            if shipment.status == 'delivered':
                events.append(('delivered', 'Pacote entregue', destination_city))
            
            for j, (event_type, description, location) in enumerate(events):
                event_time = created_date + timedelta(hours=j * 6 + random.randint(1, 5))
                
                tracking_event = TrackingEvent(
                    shipment_id=shipment.id,
                    event_type=event_type,
                    description=description,
                    location=location
                )
                tracking_event.timestamp = event_time
                db.session.add(tracking_event)
        
        # Criar modelo preditivo padrão
        existing_model = PredictiveModel.query.filter_by(model_type='delivery_time').first()
        if not existing_model:
            model = PredictiveModel(
                name='Modelo de Predição de Entrega v1.0',
                model_type='delivery_time',
                version='1.0',
                accuracy=0.87,
                parameters={
                    'algorithm': 'weighted_factors',
                    'factors': ['service_type', 'weight', 'distance', 'weather', 'traffic'],
                    'weights': {
                        'service_type': 0.4,
                        'weight': 0.2,
                        'distance': 0.3,
                        'weather': 0.05,
                        'traffic': 0.05
                    }
                }
            )
            db.session.add(model)
        
        # Criar otimizações de rota de exemplo
        optimization_data = [
            {
                'name': 'Rota Otimizada SP-RJ',
                'origin_city': 'São Paulo',
                'destination_city': 'Rio de Janeiro',
                'optimized_route': [
                    {'city': 'São Paulo', 'lat': -23.5505, 'lng': -46.6333, 'order': 0},
                    {'city': 'Taubaté', 'lat': -23.0205, 'lng': -45.5555, 'order': 1},
                    {'city': 'Rio de Janeiro', 'lat': -22.9068, 'lng': -43.1729, 'order': 2}
                ],
                'estimated_time_hours': 5.5,
                'estimated_cost': 850.00,
                'fuel_efficiency': 8.5,
                'carbon_footprint': 120.5
            },
            {
                'name': 'Rota Otimizada SP-BH',
                'origin_city': 'São Paulo',
                'destination_city': 'Belo Horizonte',
                'optimized_route': [
                    {'city': 'São Paulo', 'lat': -23.5505, 'lng': -46.6333, 'order': 0},
                    {'city': 'Campinas', 'lat': -22.9099, 'lng': -47.0626, 'order': 1},
                    {'city': 'Belo Horizonte', 'lat': -19.9167, 'lng': -43.9345, 'order': 2}
                ],
                'estimated_time_hours': 7.2,
                'estimated_cost': 1200.00,
                'fuel_efficiency': 8.2,
                'carbon_footprint': 165.8
            }
        ]
        
        for opt_data in optimization_data:
            existing_opt = RouteOptimization.query.filter_by(
                origin_city=opt_data['origin_city'],
                destination_city=opt_data['destination_city']
            ).first()
            
            if not existing_opt:
                optimization = RouteOptimization(
                    name=opt_data['name'],
                    origin_city=opt_data['origin_city'],
                    destination_city=opt_data['destination_city'],
                    optimized_route=opt_data['optimized_route'],
                    estimated_time_hours=opt_data['estimated_time_hours'],
                    estimated_cost=opt_data['estimated_cost']
                )
                optimization.fuel_efficiency = opt_data.get('fuel_efficiency')
                optimization.carbon_footprint = opt_data.get('carbon_footprint')
                db.session.add(optimization)
        
        # Criar métricas de performance de exemplo
        metrics_data = [
            {
                'metric_name': 'Taxa de Entrega no Prazo',
                'metric_value': 87.5,
                'metric_unit': '%',
                'category': 'delivery',
                'period_start': datetime.utcnow() - timedelta(days=30),
                'period_end': datetime.utcnow(),
                'additional_data': {'target': 90.0, 'improvement_needed': 2.5}
            },
            {
                'metric_name': 'Custo Médio por Envio',
                'metric_value': 125.50,
                'metric_unit': 'BRL',
                'category': 'cost',
                'period_start': datetime.utcnow() - timedelta(days=30),
                'period_end': datetime.utcnow(),
                'additional_data': {'target': 120.0, 'variance': 5.5}
            },
            {
                'metric_name': 'Satisfação do Cliente',
                'metric_value': 4.2,
                'metric_unit': 'estrelas',
                'category': 'customer_satisfaction',
                'period_start': datetime.utcnow() - timedelta(days=30),
                'period_end': datetime.utcnow(),
                'additional_data': {'reviews_count': 156, 'target': 4.5}
            },
            {
                'metric_name': 'Eficiência de Combustível',
                'metric_value': 8.7,
                'metric_unit': 'km/l',
                'category': 'efficiency',
                'period_start': datetime.utcnow() - timedelta(days=30),
                'period_end': datetime.utcnow(),
                'additional_data': {'target': 9.0, 'improvement_potential': 0.3}
            }
        ]
        
        for metric_data in metrics_data:
            existing_metric = PerformanceMetric.query.filter_by(
                metric_name=metric_data['metric_name'],
                period_start=metric_data['period_start']
            ).first()
            
            if not existing_metric:
                metric = PerformanceMetric(**metric_data)
                db.session.add(metric)
        
        db.session.commit()
        
        print("✅ Dados de demonstração criados com sucesso!")
        print(f"👤 Usuários criados: admin (admin123), demo (demo123)")
        print(f"📦 Envios criados: {Shipment.query.count()}")
        print(f"🛣️ Rotas criadas: {Route.query.count()}")
        print(f"📊 Métricas criadas: {PerformanceMetric.query.count()}")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao criar dados de demonstração: {str(e)}")
        return False

if __name__ == '__main__':
    from src.main import app
    with app.app_context():
        seed_demo_data()

