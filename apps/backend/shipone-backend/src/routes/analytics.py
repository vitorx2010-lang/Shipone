from flask import Blueprint, request, jsonify
from src.models.analytics import PredictiveModel, DeliveryPrediction, RouteOptimization, PerformanceMetric, db
from src.models.logistics import Shipment
from src.routes.auth import token_required, admin_required
from datetime import datetime, timedelta
import random
import math

analytics_bp = Blueprint('analytics', __name__)

def simulate_delivery_prediction(shipment):
    """Simula uma predição de entrega usando fatores básicos"""
    base_days = {
        'standard': 7,
        'express': 3,
        'overnight': 1
    }
    
    # Fatores que afetam a entrega
    factors = {
        'service_type': shipment.service_type,
        'weight': shipment.weight,
        'distance_factor': 1.0,  # Simulado
        'weather_factor': random.uniform(0.9, 1.1),
        'traffic_factor': random.uniform(0.95, 1.05)
    }
    
    # Calcular dias estimados
    base = base_days.get(shipment.service_type, 7)
    
    # Ajustar por peso (pacotes mais pesados podem demorar mais)
    if shipment.weight > 10:
        base += 1
    elif shipment.weight > 50:
        base += 2
    
    # Aplicar fatores
    adjusted_days = base * factors['weather_factor'] * factors['traffic_factor']
    
    # Adicionar variação aleatória
    adjusted_days += random.uniform(-0.5, 0.5)
    
    # Garantir que seja pelo menos 1 dia
    adjusted_days = max(1, adjusted_days)
    
    predicted_date = datetime.utcnow() + timedelta(days=adjusted_days)
    confidence = random.uniform(0.75, 0.95)
    
    return predicted_date, confidence, factors

@analytics_bp.route('/predictions/delivery/<int:shipment_id>', methods=['POST'])
@token_required
def create_delivery_prediction(current_user, shipment_id):
    """Criar predição de entrega para um envio"""
    try:
        shipment = Shipment.query.get(shipment_id)
        if not shipment:
            return jsonify({'message': 'Shipment not found'}), 404
        
        # Verificar se o usuário tem acesso ao envio
        if current_user.role != 'admin' and shipment.sender_id != current_user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Verificar se já existe uma predição
        existing_prediction = DeliveryPrediction.query.filter_by(shipment_id=shipment_id).first()
        if existing_prediction:
            return jsonify({'message': 'Prediction already exists for this shipment'}), 400
        
        # Buscar ou criar modelo padrão
        model = PredictiveModel.query.filter_by(
            model_type='delivery_time', 
            is_active=True
        ).first()
        
        if not model:
            # Criar modelo padrão
            model = PredictiveModel(
                name='Default Delivery Time Model',
                model_type='delivery_time',
                version='1.0',
                accuracy=0.85,
                parameters={
                    'algorithm': 'weighted_factors',
                    'factors': ['service_type', 'weight', 'distance', 'weather', 'traffic']
                }
            )
            db.session.add(model)
            db.session.commit()
        
        # Gerar predição
        predicted_date, confidence, factors = simulate_delivery_prediction(shipment)
        
        prediction = DeliveryPrediction(
            shipment_id=shipment_id,
            model_id=model.id,
            predicted_delivery_date=predicted_date,
            confidence_score=confidence,
            factors=factors
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        return jsonify({
            'message': 'Delivery prediction created successfully',
            'prediction': prediction.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating prediction: {str(e)}'}), 500

@analytics_bp.route('/predictions/delivery/<int:shipment_id>', methods=['GET'])
@token_required
def get_delivery_prediction(current_user, shipment_id):
    """Obter predição de entrega para um envio"""
    try:
        shipment = Shipment.query.get(shipment_id)
        if not shipment:
            return jsonify({'message': 'Shipment not found'}), 404
        
        # Verificar se o usuário tem acesso ao envio
        if current_user.role != 'admin' and shipment.sender_id != current_user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        prediction = DeliveryPrediction.query.filter_by(shipment_id=shipment_id).first()
        if not prediction:
            return jsonify({'message': 'No prediction found for this shipment'}), 404
        
        return jsonify({
            'prediction': prediction.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error getting prediction: {str(e)}'}), 500

@analytics_bp.route('/route-optimization', methods=['POST'])
@token_required
@admin_required
def create_route_optimization(current_user):
    """Criar otimização de rota"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'origin_city', 'destination_city']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'{field} is required'}), 400
        
        # Simular otimização de rota
        waypoints = [
            {'city': data['origin_city'], 'lat': 0, 'lng': 0, 'order': 0},
            {'city': data['destination_city'], 'lat': 0, 'lng': 0, 'order': 1}
        ]
        
        # Adicionar waypoints intermediários se fornecidos
        if 'waypoints' in data:
            for i, waypoint in enumerate(data['waypoints']):
                waypoints.insert(-1, {
                    'city': waypoint.get('city', f'Waypoint {i+1}'),
                    'lat': waypoint.get('lat', 0),
                    'lng': waypoint.get('lng', 0),
                    'order': i + 1
                })
        
        # Simular cálculos
        estimated_time = random.uniform(8, 48)  # 8-48 horas
        estimated_cost = random.uniform(500, 2000)  # $500-2000
        
        optimization = RouteOptimization(
            name=data['name'],
            origin_city=data['origin_city'],
            destination_city=data['destination_city'],
            optimized_route=waypoints,
            estimated_time_hours=estimated_time,
            estimated_cost=estimated_cost
        )
        
        # Campos opcionais
        if 'fuel_efficiency' in data:
            optimization.fuel_efficiency = data['fuel_efficiency']
        if 'carbon_footprint' in data:
            optimization.carbon_footprint = data['carbon_footprint']
        
        db.session.add(optimization)
        db.session.commit()
        
        return jsonify({
            'message': 'Route optimization created successfully',
            'optimization': optimization.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating route optimization: {str(e)}'}), 500

@analytics_bp.route('/route-optimization', methods=['GET'])
@token_required
def list_route_optimizations(current_user):
    """Listar otimizações de rota"""
    try:
        optimizations = RouteOptimization.query.order_by(RouteOptimization.created_at.desc()).all()
        
        return jsonify({
            'optimizations': [opt.to_dict() for opt in optimizations]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error listing route optimizations: {str(e)}'}), 500

@analytics_bp.route('/performance-metrics', methods=['POST'])
@token_required
@admin_required
def create_performance_metric(current_user):
    """Criar métrica de performance"""
    try:
        data = request.get_json()
        
        required_fields = ['metric_name', 'metric_value', 'category', 'period_start', 'period_end']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'{field} is required'}), 400
        
        period_start = datetime.fromisoformat(data['period_start'].replace('Z', '+00:00'))
        period_end = datetime.fromisoformat(data['period_end'].replace('Z', '+00:00'))
        
        metric = PerformanceMetric(
            metric_name=data['metric_name'],
            metric_value=float(data['metric_value']),
            category=data['category'],
            period_start=period_start,
            period_end=period_end,
            metric_unit=data.get('metric_unit'),
            additional_data=data.get('additional_data')
        )
        
        db.session.add(metric)
        db.session.commit()
        
        return jsonify({
            'message': 'Performance metric created successfully',
            'metric': metric.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating performance metric: {str(e)}'}), 500

@analytics_bp.route('/performance-metrics', methods=['GET'])
@token_required
def get_performance_metrics(current_user):
    """Obter métricas de performance"""
    try:
        category = request.args.get('category')
        days = int(request.args.get('days', 30))
        
        query = PerformanceMetric.query
        
        if category:
            query = query.filter_by(category=category)
        
        # Filtrar por período
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(PerformanceMetric.period_start >= start_date)
        
        metrics = query.order_by(PerformanceMetric.created_at.desc()).all()
        
        return jsonify({
            'metrics': [metric.to_dict() for metric in metrics]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error getting performance metrics: {str(e)}'}), 500

@analytics_bp.route('/advanced-dashboard', methods=['GET'])
@token_required
def get_advanced_dashboard(current_user):
    """Obter dados avançados para dashboard"""
    try:
        # Filtrar por usuário se não for admin
        if current_user.role == 'admin':
            shipments = Shipment.query.all()
        else:
            shipments = Shipment.query.filter_by(sender_id=current_user.id).all()
        
        # Métricas básicas
        total_shipments = len(shipments)
        
        # Análise de tendências (últimos 30 dias)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_shipments = [s for s in shipments if s.created_at >= thirty_days_ago]
        
        # Análise de performance de entrega
        delivered_shipments = [s for s in shipments if s.status == 'delivered' and s.actual_delivery and s.estimated_delivery]
        
        on_time_deliveries = 0
        total_delay_days = 0
        
        for shipment in delivered_shipments:
            estimated = shipment.estimated_delivery.date()
            actual = shipment.actual_delivery.date()
            
            if actual <= estimated:
                on_time_deliveries += 1
            else:
                delay = (actual - estimated).days
                total_delay_days += delay
        
        on_time_percentage = (on_time_deliveries / len(delivered_shipments) * 100) if delivered_shipments else 0
        avg_delay_days = (total_delay_days / (len(delivered_shipments) - on_time_deliveries)) if (len(delivered_shipments) - on_time_deliveries) > 0 else 0
        
        # Análise de custos
        shipments_with_cost = [s for s in shipments if s.cost]
        total_revenue = sum(s.cost for s in shipments_with_cost)
        avg_cost_per_shipment = total_revenue / len(shipments_with_cost) if shipments_with_cost else 0
        
        # Análise de rotas mais utilizadas
        route_usage = {}
        for shipment in shipments:
            route_key = f"{shipment.origin_city} → {shipment.destination_city}"
            route_usage[route_key] = route_usage.get(route_key, 0) + 1
        
        top_routes = sorted(route_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Predições ativas
        active_predictions = DeliveryPrediction.query.join(Shipment).filter(
            Shipment.status.in_(['pending', 'in_transit'])
        ).count()
        
        # Otimizações de rota recentes
        recent_optimizations = RouteOptimization.query.filter(
            RouteOptimization.created_at >= thirty_days_ago
        ).count()
        
        return jsonify({
            'advanced_analytics': {
                'total_shipments': total_shipments,
                'recent_shipments_30d': len(recent_shipments),
                'delivery_performance': {
                    'on_time_percentage': round(on_time_percentage, 2),
                    'average_delay_days': round(avg_delay_days, 2),
                    'total_delivered': len(delivered_shipments)
                },
                'financial_metrics': {
                    'total_revenue': round(total_revenue, 2),
                    'average_cost_per_shipment': round(avg_cost_per_shipment, 2),
                    'shipments_with_cost': len(shipments_with_cost)
                },
                'top_routes': [{'route': route, 'count': count} for route, count in top_routes],
                'predictive_analytics': {
                    'active_predictions': active_predictions,
                    'recent_optimizations': recent_optimizations
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error getting advanced dashboard: {str(e)}'}), 500

@analytics_bp.route('/models', methods=['GET'])
@token_required
@admin_required
def list_predictive_models(current_user):
    """Listar modelos preditivos"""
    try:
        models = PredictiveModel.query.all()
        
        return jsonify({
            'models': [model.to_dict() for model in models]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error listing models: {str(e)}'}), 500

@analytics_bp.route('/models', methods=['POST'])
@token_required
@admin_required
def create_predictive_model(current_user):
    """Criar novo modelo preditivo"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'model_type', 'version']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'{field} is required'}), 400
        
        model = PredictiveModel(
            name=data['name'],
            model_type=data['model_type'],
            version=data['version'],
            accuracy=data.get('accuracy'),
            parameters=data.get('parameters')
        )
        
        db.session.add(model)
        db.session.commit()
        
        return jsonify({
            'message': 'Predictive model created successfully',
            'model': model.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating model: {str(e)}'}), 500

