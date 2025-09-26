from flask import Blueprint, request, jsonify
from src.models.logistics import Shipment, TrackingEvent, Route, db
from src.routes.auth import token_required
from datetime import datetime, timedelta
import random
import string

logistics_bp = Blueprint('logistics', __name__)

def generate_tracking_number():
    """Gera um número de rastreamento único"""
    prefix = "SHP"
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}{suffix}"

@logistics_bp.route('/shipments', methods=['POST'])
@token_required
def create_shipment(current_user):
    """Criar novo envio"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = [
            'recipient_name', 'origin_address', 'destination_address',
            'origin_city', 'destination_city', 'origin_country',
            'destination_country', 'weight', 'package_type', 'service_type'
        ]
        
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'{field} is required'}), 400
        
        # Gerar número de rastreamento
        tracking_number = generate_tracking_number()
        
        # Criar envio
        shipment = Shipment(
            tracking_number=tracking_number,
            sender_id=current_user.id,
            recipient_name=data['recipient_name'],
            origin_address=data['origin_address'],
            destination_address=data['destination_address'],
            origin_city=data['origin_city'],
            destination_city=data['destination_city'],
            origin_country=data['origin_country'],
            destination_country=data['destination_country'],
            weight=float(data['weight']),
            package_type=data['package_type'],
            service_type=data['service_type']
        )
        
        # Campos opcionais
        if 'recipient_email' in data:
            shipment.recipient_email = data['recipient_email']
        if 'recipient_phone' in data:
            shipment.recipient_phone = data['recipient_phone']
        if 'dimensions' in data:
            shipment.dimensions = data['dimensions']
        if 'cost' in data:
            shipment.cost = float(data['cost'])
        if 'currency' in data:
            shipment.currency = data['currency']
        
        # Calcular estimativa de entrega baseada no tipo de serviço
        if data['service_type'] == 'overnight':
            shipment.estimated_delivery = datetime.utcnow() + timedelta(days=1)
        elif data['service_type'] == 'express':
            shipment.estimated_delivery = datetime.utcnow() + timedelta(days=3)
        else:  # standard
            shipment.estimated_delivery = datetime.utcnow() + timedelta(days=7)
        
        db.session.add(shipment)
        db.session.commit()
        
        # Criar evento inicial de rastreamento
        initial_event = TrackingEvent(
            shipment_id=shipment.id,
            event_type='created',
            description='Shipment created and pending pickup',
            location=data['origin_city']
        )
        db.session.add(initial_event)
        db.session.commit()
        
        return jsonify({
            'message': 'Shipment created successfully',
            'shipment': shipment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating shipment: {str(e)}'}), 500

@logistics_bp.route('/shipments', methods=['GET'])
@token_required
def list_shipments(current_user):
    """Listar envios do usuário"""
    try:
        # Usuários normais veem apenas seus envios, admins veem todos
        if current_user.role == 'admin':
            shipments = Shipment.query.all()
        else:
            shipments = Shipment.query.filter_by(sender_id=current_user.id).all()
        
        return jsonify({
            'shipments': [shipment.to_dict() for shipment in shipments]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error listing shipments: {str(e)}'}), 500

@logistics_bp.route('/shipments/<tracking_number>', methods=['GET'])
def track_shipment(tracking_number):
    """Rastrear envio por número de rastreamento (público)"""
    try:
        shipment = Shipment.query.filter_by(tracking_number=tracking_number).first()
        
        if not shipment:
            return jsonify({'message': 'Shipment not found'}), 404
        
        # Incluir eventos de rastreamento
        shipment_data = shipment.to_dict()
        shipment_data['tracking_events'] = [event.to_dict() for event in shipment.tracking_events]
        
        return jsonify({
            'shipment': shipment_data
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error tracking shipment: {str(e)}'}), 500

@logistics_bp.route('/shipments/<int:shipment_id>/status', methods=['PUT'])
@token_required
def update_shipment_status(current_user, shipment_id):
    """Atualizar status do envio"""
    try:
        # Apenas admins podem atualizar status
        if current_user.role != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        
        shipment = Shipment.query.get(shipment_id)
        if not shipment:
            return jsonify({'message': 'Shipment not found'}), 404
        
        data = request.get_json()
        if 'status' not in data:
            return jsonify({'message': 'Status is required'}), 400
        
        old_status = shipment.status
        shipment.status = data['status']
        
        # Se foi entregue, definir data de entrega
        if data['status'] == 'delivered':
            shipment.actual_delivery = datetime.utcnow()
        
        db.session.commit()
        
        # Criar evento de rastreamento
        event_descriptions = {
            'pending': 'Shipment is pending pickup',
            'in_transit': 'Shipment is in transit',
            'out_for_delivery': 'Shipment is out for delivery',
            'delivered': 'Shipment has been delivered',
            'cancelled': 'Shipment has been cancelled'
        }
        
        tracking_event = TrackingEvent(
            shipment_id=shipment.id,
            event_type=data['status'],
            description=event_descriptions.get(data['status'], f'Status updated to {data["status"]}'),
            location=data.get('location')
        )
        db.session.add(tracking_event)
        db.session.commit()
        
        return jsonify({
            'message': 'Shipment status updated successfully',
            'shipment': shipment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating shipment status: {str(e)}'}), 500

@logistics_bp.route('/routes', methods=['GET'])
@token_required
def list_routes(current_user):
    """Listar rotas disponíveis"""
    try:
        routes = Route.query.filter_by(is_active=True).all()
        return jsonify({
            'routes': [route.to_dict() for route in routes]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error listing routes: {str(e)}'}), 500

@logistics_bp.route('/routes', methods=['POST'])
@token_required
def create_route(current_user):
    """Criar nova rota (apenas admin)"""
    try:
        if current_user.role != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        
        data = request.get_json()
        
        required_fields = [
            'name', 'origin_city', 'destination_city', 
            'distance_km', 'estimated_duration_hours', 'transport_mode'
        ]
        
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'{field} is required'}), 400
        
        route = Route(
            name=data['name'],
            origin_city=data['origin_city'],
            destination_city=data['destination_city'],
            distance_km=float(data['distance_km']),
            estimated_duration_hours=float(data['estimated_duration_hours']),
            transport_mode=data['transport_mode']
        )
        
        db.session.add(route)
        db.session.commit()
        
        return jsonify({
            'message': 'Route created successfully',
            'route': route.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating route: {str(e)}'}), 500

@logistics_bp.route('/analytics/dashboard', methods=['GET'])
@token_required
def get_dashboard_analytics(current_user):
    """Obter dados analíticos para dashboard"""
    try:
        # Filtrar por usuário se não for admin
        if current_user.role == 'admin':
            shipments = Shipment.query.all()
        else:
            shipments = Shipment.query.filter_by(sender_id=current_user.id).all()
        
        # Estatísticas básicas
        total_shipments = len(shipments)
        pending_shipments = len([s for s in shipments if s.status == 'pending'])
        in_transit_shipments = len([s for s in shipments if s.status == 'in_transit'])
        delivered_shipments = len([s for s in shipments if s.status == 'delivered'])
        
        # Estatísticas por tipo de serviço
        service_stats = {}
        for shipment in shipments:
            service = shipment.service_type
            if service not in service_stats:
                service_stats[service] = 0
            service_stats[service] += 1
        
        # Estatísticas por país de destino
        country_stats = {}
        for shipment in shipments:
            country = shipment.destination_country
            if country not in country_stats:
                country_stats[country] = 0
            country_stats[country] += 1
        
        return jsonify({
            'analytics': {
                'total_shipments': total_shipments,
                'pending_shipments': pending_shipments,
                'in_transit_shipments': in_transit_shipments,
                'delivered_shipments': delivered_shipments,
                'service_type_distribution': service_stats,
                'destination_country_distribution': country_stats
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error getting analytics: {str(e)}'}), 500

