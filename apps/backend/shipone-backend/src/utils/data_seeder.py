import os
import sys
from datetime import datetime, timedelta
import random

# Adiciona o diretório raiz do projeto ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.main import app, db
from src.models.user import User
from src.models.logistics import Shipment, TrackingEvent, RouteOptimization
from src.models.analytics import PerformanceMetric, DeliveryPrediction

with app.app_context():
    db.create_all()

    # Limpar dados existentes
    db.session.query(User).delete()
    db.session.query(Shipment).delete()
    db.session.query(TrackingEvent).delete()
    db.session.query(RouteOptimization).delete()
    db.session.query(PerformanceMetric).delete()
    db.session.query(DeliveryPrediction).delete()
    db.session.commit()

    # Criar usuários
    admin_user = User(
        username="admin",
        email="admin@shipone.com",
        password="admin123",
        full_name="Admin User",
        company="ShipOne Inc.",
        department="Management",
        phone="+1234567890",
        role="admin"
    )
    demo_user = User(
        username="demo",
        email="demo@shipone.com",
        password="demo123",
        full_name="Demo User",
        company="Demo Corp.",
        department="Operations",
        phone="+0987654321",
        role="user"
    )
    db.session.add_all([admin_user, demo_user])
    db.session.commit()

    print("✅ Usuários criados: admin (admin123), demo (demo123)")

    # Criar envios
    shipments_data = []
    cities = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre", "Salvador"]
    statuses = ["pending", "in_transit", "delivered", "exception"]
    service_types = ["standard", "express", "overnight"]

    for i in range(20):
        origin_city = random.choice(cities)
        destination_city = random.choice(cities)
        while destination_city == origin_city:
            destination_city = random.choice(cities)

        shipment = Shipment(
            sender_id=random.choice([admin_user.id, demo_user.id]),
            recipient_name=f"Recipient {i+1}",
            recipient_email=f"recipient{i+1}@example.com",
            recipient_phone=f"(XX) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            origin_address=f"Rua Origem {i+1}, {origin_city}",
            destination_address=f"Rua Destino {i+1}, {destination_city}",
            origin_city=origin_city,
            destination_city=destination_city,
            origin_country="Brasil",
            destination_country="Brasil",
            weight=round(random.uniform(0.5, 100.0), 2),
            dimensions=f"{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(10, 100)}",
            package_type=random.choice(["box", "envelope", "pallet"]),
            service_type=random.choice(service_types),
            cost=round(random.uniform(50.0, 1000.0), 2),
            currency="BRL",
            status=random.choice(statuses),
            estimated_delivery=datetime.now() + timedelta(days=random.randint(1, 10))
        )
        shipments_data.append(shipment)

    db.session.add_all(shipments_data)
    db.session.commit()

    print(f"✅ Envios criados: {len(shipments_data)}")

    # Criar eventos de rastreamento
    for shipment in shipments_data:
        event_types = ["created", "in_transit", "out_for_delivery", "delivered", "exception"]
        locations = [shipment.origin_city, "Centro de Distribuição", shipment.destination_city]
        current_time = shipment.created_at

        for event_type in event_types:
            if event_type == "exception" and random.random() > 0.8:
                event = TrackingEvent(
                    shipment_id=shipment.id,
                    event_type="exception",
                    description=f"Exceção: {random.choice([\"Endereço incorreto\", \"Atraso na entrega\", \"Pacote danificado\"])}",
                    location=random.choice(locations),
                    timestamp=current_time + timedelta(hours=random.randint(1, 24))
                )
                db.session.add(event)
                break
            elif event_type == "delivered" and shipment.status != "delivered":
                continue # Não cria evento de entrega se o status final não for entregue
            elif event_type == "delivered" and shipment.status == "delivered":
                event = TrackingEvent(
                    shipment_id=shipment.id,
                    event_type=event_type,
                    description=f"Envio {event_type}",
                    location=shipment.destination_city,
                    timestamp=shipment.estimated_delivery + timedelta(hours=random.randint(-12, 12))
                )
                db.session.add(event)
                break
            else:
                event = TrackingEvent(
                    shipment_id=shipment.id,
                    event_type=event_type,
                    description=f"Envio {event_type}",
                    location=random.choice(locations),
                    timestamp=current_time + timedelta(hours=random.randint(1, 24))
                )
                db.session.add(event)
                current_time = event.timestamp

    db.session.commit()
    print("✅ Eventos de rastreamento criados.")

    # Criar otimizações de rota
    routes_data = [
        {
            "name": "Rota SP-RJ",
            "origin_city": "São Paulo",
            "destination_city": "Rio de Janeiro",
            "waypoints": [
                {"city": "São Paulo", "lat": -23.5505, "lng": -46.6333},
                {"city": "Taubaté", "lat": -23.0205, "lng": -45.5555},
                {"city": "Rio de Janeiro", "lat": -22.9068, "lng": -43.1729}
            ]
        },
        {
            "name": "Rota SP-BH",
            "origin_city": "São Paulo",
            "destination_city": "Belo Horizonte",
            "waypoints": [
                {"city": "São Paulo", "lat": -23.5505, "lng": -46.6333},
                {"city": "Campinas", "lat": -22.9099, "lng": -47.0626},
                {"city": "Belo Horizonte", "lat": -19.9167, "lng": -43.9345}
            ]
        },
        {
            "name": "Rota Sul",
            "origin_city": "Curitiba",
            "destination_city": "Porto Alegre",
            "waypoints": [
                {"city": "Curitiba", "lat": -25.4284, "lng": -49.2733},
                {"city": "Florianópolis", "lat": -27.5935, "lng": -48.5585},
                {"city": "Porto Alegre", "lat": -30.0346, "lng": -51.2177}
            ]
        },
        {
            "name": "Rota Nordeste",
            "origin_city": "Salvador",
            "destination_city": "Recife",
            "waypoints": [
                {"city": "Salvador", "lat": -12.9714, "lng": -38.5014},
                {"city": "Aracaju", "lat": -10.9472, "lng": -37.0731},
                {"city": "Maceió", "lat": -9.6659, "lng": -35.7359},
                {"city": "Recife", "lat": -8.0476, "lng": -34.8768}
            ]
        }
    ]

    for route_data in routes_data:
        route = RouteOptimization(
            name=route_data["name"],
            origin_city=route_data["origin_city"],
            destination_city=route_data["destination_city"],
            waypoints=route_data["waypoints"]
        )
        db.session.add(route)
    db.session.commit()
    print(f"✅ Rotas criadas: {len(routes_data)}")

    # Criar métricas de performance
    metrics_data = [
        {
            "metric_name": "Taxa de Entrega no Prazo",
            "metric_value": 87.5,
            "metric_unit": "%",
            "category": "delivery",
            "period_start": datetime.now() - timedelta(days=30),
            "period_end": datetime.now(),
            "additional_data": {"target": 90.0, "improvement_needed": 2.5}
        },
        {
            "metric_name": "Custo Médio por Envio",
            "metric_value": 150.00,
            "metric_unit": "BRL",
            "category": "cost",
            "period_start": datetime.now() - timedelta(days=30),
            "period_end": datetime.now(),
            "additional_data": {"target": 140.0, "variance": 10.0}
        },
        {
            "metric_name": "Eficiência de Combustível",
            "metric_value": 8.2,
            "metric_unit": "km/l",
            "category": "efficiency",
            "period_start": datetime.now() - timedelta(days=30),
            "period_end": datetime.now(),
            "additional_data": {"target": 8.5, "delta": -0.3}
        },
        {
            "metric_name": "Satisfação do Cliente",
            "metric_value": 4.7,
            "metric_unit": "estrelas",
            "category": "customer_satisfaction",
            "period_start": datetime.now() - timedelta(days=30),
            "period_end": datetime.now(),
            "additional_data": {"target": 4.8, "feedback_count": 120}
        }
    ]

    for metric_data in metrics_data:
        metric = PerformanceMetric(
            metric_name=metric_data["metric_name"],
            metric_value=metric_data["metric_value"],
            metric_unit=metric_data["metric_unit"],
            category=metric_data["category"],
            period_start=metric_data["period_start"],
            period_end=metric_data["period_end"],
            additional_data=metric_data["additional_data"]
        )
        db.session.add(metric)
    db.session.commit()
    print(f"✅ Métricas criadas: {len(metrics_data)}")

    # Criar predições de entrega
    for shipment in shipments_data:
        if shipment.status != "delivered":
            prediction = DeliveryPrediction(
                shipment_id=shipment.id,
                predicted_delivery_date=shipment.estimated_delivery + timedelta(hours=random.randint(-24, 24)),
                confidence_score=round(random.uniform(0.7, 0.99), 2),
                factors={
                    "service_type": shipment.service_type,
                    "weight": shipment.weight,
                    "weather_factor": round(random.uniform(0.9, 1.1), 2),
                    "traffic_factor": round(random.uniform(0.9, 1.1), 2)
                }
            )
            db.session.add(prediction)
    db.session.commit()
    print("✅ Predições de entrega criadas.")

    print("\n✅ Dados de demonstração criados com sucesso!")


