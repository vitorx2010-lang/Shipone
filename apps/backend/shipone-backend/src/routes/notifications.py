from flask import Blueprint, request, jsonify
from src.models.user import User, db
from src.models.logistics import Shipment, TrackingEvent
from src.routes.auth import token_required, admin_required
from datetime import datetime, timedelta
import json

notifications_bp = Blueprint('notifications', __name__)

class NotificationService:
    """Serviço para gerenciar notificações"""
    
    @staticmethod
    def create_notification(user_id, title, message, notification_type='info', metadata=None):
        """Criar uma nova notificação"""
        # Em um sistema real, isso seria salvo no banco de dados
        # Por simplicidade, vamos simular com uma estrutura em memória
        notification = {
            'id': f"notif_{datetime.utcnow().timestamp()}",
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': notification_type,  # info, warning, error, success
            'metadata': metadata or {},
            'read': False,
            'created_at': datetime.utcnow().isoformat()
        }
        return notification
    
    @staticmethod
    def send_shipment_notification(shipment, event_type, users=None):
        """Enviar notificação relacionada a envio"""
        if not users:
            users = [shipment.sender]
        
        messages = {
            'created': f'Seu envio {shipment.tracking_number} foi criado com sucesso',
            'in_transit': f'Seu envio {shipment.tracking_number} está em trânsito',
            'out_for_delivery': f'Seu envio {shipment.tracking_number} saiu para entrega',
            'delivered': f'Seu envio {shipment.tracking_number} foi entregue',
            'delayed': f'Seu envio {shipment.tracking_number} está atrasado',
            'cancelled': f'Seu envio {shipment.tracking_number} foi cancelado'
        }
        
        titles = {
            'created': 'Envio Criado',
            'in_transit': 'Envio em Trânsito',
            'out_for_delivery': 'Saiu para Entrega',
            'delivered': 'Envio Entregue',
            'delayed': 'Envio Atrasado',
            'cancelled': 'Envio Cancelado'
        }
        
        notification_types = {
            'created': 'success',
            'in_transit': 'info',
            'out_for_delivery': 'info',
            'delivered': 'success',
            'delayed': 'warning',
            'cancelled': 'error'
        }
        
        notifications = []
        for user in users:
            notification = NotificationService.create_notification(
                user_id=user.id,
                title=titles.get(event_type, 'Atualização de Envio'),
                message=messages.get(event_type, f'Atualização no envio {shipment.tracking_number}'),
                notification_type=notification_types.get(event_type, 'info'),
                metadata={
                    'shipment_id': shipment.id,
                    'tracking_number': shipment.tracking_number,
                    'event_type': event_type
                }
            )
            notifications.append(notification)
        
        return notifications

# Simulação de armazenamento de notificações em memória
# Em um sistema real, isso seria uma tabela no banco de dados
NOTIFICATIONS_STORE = {}

@notifications_bp.route('/notifications', methods=['GET'])
@token_required
def get_user_notifications(current_user):
    """Obter notificações do usuário"""
    try:
        user_notifications = NOTIFICATIONS_STORE.get(current_user.id, [])
        
        # Filtros opcionais
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 50))
        
        if unread_only:
            user_notifications = [n for n in user_notifications if not n['read']]
        
        # Ordenar por data (mais recentes primeiro)
        user_notifications.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Aplicar limite
        user_notifications = user_notifications[:limit]
        
        return jsonify({
            'notifications': user_notifications,
            'total_count': len(NOTIFICATIONS_STORE.get(current_user.id, [])),
            'unread_count': len([n for n in NOTIFICATIONS_STORE.get(current_user.id, []) if not n['read']])
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error getting notifications: {str(e)}'}), 500

@notifications_bp.route('/notifications/<notification_id>/read', methods=['POST'])
@token_required
def mark_notification_read(current_user, notification_id):
    """Marcar notificação como lida"""
    try:
        user_notifications = NOTIFICATIONS_STORE.get(current_user.id, [])
        
        for notification in user_notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                notification['read_at'] = datetime.utcnow().isoformat()
                break
        else:
            return jsonify({'message': 'Notification not found'}), 404
        
        return jsonify({'message': 'Notification marked as read'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error marking notification as read: {str(e)}'}), 500

@notifications_bp.route('/notifications/read-all', methods=['POST'])
@token_required
def mark_all_notifications_read(current_user):
    """Marcar todas as notificações como lidas"""
    try:
        user_notifications = NOTIFICATIONS_STORE.get(current_user.id, [])
        
        for notification in user_notifications:
            if not notification['read']:
                notification['read'] = True
                notification['read_at'] = datetime.utcnow().isoformat()
        
        return jsonify({'message': 'All notifications marked as read'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error marking all notifications as read: {str(e)}'}), 500

@notifications_bp.route('/notifications/send', methods=['POST'])
@token_required
@admin_required
def send_custom_notification(current_user):
    """Enviar notificação personalizada (apenas admin)"""
    try:
        data = request.get_json()
        
        required_fields = ['title', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'{field} is required'}), 400
        
        # Determinar destinatários
        if 'user_ids' in data:
            user_ids = data['user_ids']
        elif 'send_to_all' in data and data['send_to_all']:
            users = User.query.filter_by(is_active=True).all()
            user_ids = [user.id for user in users]
        else:
            return jsonify({'message': 'Must specify user_ids or send_to_all'}), 400
        
        notifications_created = []
        
        for user_id in user_ids:
            notification = NotificationService.create_notification(
                user_id=user_id,
                title=data['title'],
                message=data['message'],
                notification_type=data.get('type', 'info'),
                metadata=data.get('metadata')
            )
            
            # Adicionar ao store
            if user_id not in NOTIFICATIONS_STORE:
                NOTIFICATIONS_STORE[user_id] = []
            NOTIFICATIONS_STORE[user_id].append(notification)
            
            notifications_created.append(notification)
        
        return jsonify({
            'message': f'Notification sent to {len(user_ids)} users',
            'notifications_created': len(notifications_created)
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error sending notification: {str(e)}'}), 500

@notifications_bp.route('/notifications/shipment-updates', methods=['POST'])
@token_required
@admin_required
def send_shipment_update_notifications(current_user):
    """Enviar notificações de atualização de envios"""
    try:
        data = request.get_json()
        
        if 'shipment_id' not in data or 'event_type' not in data:
            return jsonify({'message': 'shipment_id and event_type are required'}), 400
        
        shipment = Shipment.query.get(data['shipment_id'])
        if not shipment:
            return jsonify({'message': 'Shipment not found'}), 404
        
        # Criar notificações
        notifications = NotificationService.send_shipment_notification(
            shipment=shipment,
            event_type=data['event_type']
        )
        
        # Adicionar ao store
        for notification in notifications:
            user_id = notification['user_id']
            if user_id not in NOTIFICATIONS_STORE:
                NOTIFICATIONS_STORE[user_id] = []
            NOTIFICATIONS_STORE[user_id].append(notification)
        
        return jsonify({
            'message': 'Shipment notifications sent successfully',
            'notifications_sent': len(notifications)
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error sending shipment notifications: {str(e)}'}), 500

@notifications_bp.route('/notifications/preferences', methods=['GET'])
@token_required
def get_notification_preferences(current_user):
    """Obter preferências de notificação do usuário"""
    try:
        # Em um sistema real, isso seria salvo no banco de dados
        # Por simplicidade, retornamos preferências padrão
        default_preferences = {
            'email_notifications': True,
            'push_notifications': True,
            'sms_notifications': False,
            'notification_types': {
                'shipment_created': True,
                'shipment_in_transit': True,
                'shipment_delivered': True,
                'shipment_delayed': True,
                'shipment_cancelled': True,
                'system_updates': True,
                'promotional': False
            },
            'quiet_hours': {
                'enabled': False,
                'start_time': '22:00',
                'end_time': '08:00'
            }
        }
        
        return jsonify({
            'preferences': default_preferences
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error getting notification preferences: {str(e)}'}), 500

@notifications_bp.route('/notifications/preferences', methods=['PUT'])
@token_required
def update_notification_preferences(current_user):
    """Atualizar preferências de notificação do usuário"""
    try:
        data = request.get_json()
        
        # Em um sistema real, isso seria salvo no banco de dados
        # Por simplicidade, apenas retornamos sucesso
        
        return jsonify({
            'message': 'Notification preferences updated successfully',
            'preferences': data
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error updating notification preferences: {str(e)}'}), 500

@notifications_bp.route('/notifications/test', methods=['POST'])
@token_required
def send_test_notification(current_user):
    """Enviar notificação de teste"""
    try:
        notification = NotificationService.create_notification(
            user_id=current_user.id,
            title='Notificação de Teste',
            message='Esta é uma notificação de teste do sistema ShipOne.',
            notification_type='info',
            metadata={'test': True}
        )
        
        # Adicionar ao store
        if current_user.id not in NOTIFICATIONS_STORE:
            NOTIFICATIONS_STORE[current_user.id] = []
        NOTIFICATIONS_STORE[current_user.id].append(notification)
        
        return jsonify({
            'message': 'Test notification sent successfully',
            'notification': notification
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error sending test notification: {str(e)}'}), 500

