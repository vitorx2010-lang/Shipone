from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Shipment(db.Model):
    __tablename__ = 'shipments'
    
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(100), unique=True, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_name = db.Column(db.String(200), nullable=False)
    recipient_email = db.Column(db.String(120), nullable=True)
    recipient_phone = db.Column(db.String(20), nullable=True)
    
    # Endereços
    origin_address = db.Column(db.Text, nullable=False)
    destination_address = db.Column(db.Text, nullable=False)
    origin_city = db.Column(db.String(100), nullable=False)
    destination_city = db.Column(db.String(100), nullable=False)
    origin_country = db.Column(db.String(50), nullable=False)
    destination_country = db.Column(db.String(50), nullable=False)
    
    # Detalhes do envio
    weight = db.Column(db.Float, nullable=False)  # em kg
    dimensions = db.Column(db.String(100), nullable=True)  # LxWxH em cm
    package_type = db.Column(db.String(50), nullable=False)  # box, envelope, pallet
    service_type = db.Column(db.String(50), nullable=False)  # standard, express, overnight
    
    # Status e datas
    status = db.Column(db.String(50), default='pending')  # pending, in_transit, delivered, cancelled
    estimated_delivery = db.Column(db.DateTime, nullable=True)
    actual_delivery = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Custos
    cost = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(3), default='USD')
    
    # Relacionamentos
    sender = db.relationship('User', backref=db.backref('sent_shipments', lazy=True))
    
    def __init__(self, tracking_number, sender_id, recipient_name, origin_address, 
                 destination_address, origin_city, destination_city, origin_country, 
                 destination_country, weight, package_type, service_type):
        self.tracking_number = tracking_number
        self.sender_id = sender_id
        self.recipient_name = recipient_name
        self.origin_address = origin_address
        self.destination_address = destination_address
        self.origin_city = origin_city
        self.destination_city = destination_city
        self.origin_country = origin_country
        self.destination_country = destination_country
        self.weight = weight
        self.package_type = package_type
        self.service_type = service_type
    
    def to_dict(self):
        return {
            'id': self.id,
            'tracking_number': self.tracking_number,
            'sender_id': self.sender_id,
            'recipient_name': self.recipient_name,
            'recipient_email': self.recipient_email,
            'recipient_phone': self.recipient_phone,
            'origin_address': self.origin_address,
            'destination_address': self.destination_address,
            'origin_city': self.origin_city,
            'destination_city': self.destination_city,
            'origin_country': self.origin_country,
            'destination_country': self.destination_country,
            'weight': self.weight,
            'dimensions': self.dimensions,
            'package_type': self.package_type,
            'service_type': self.service_type,
            'status': self.status,
            'estimated_delivery': self.estimated_delivery.isoformat() if self.estimated_delivery else None,
            'actual_delivery': self.actual_delivery.isoformat() if self.actual_delivery else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'cost': self.cost,
            'currency': self.currency
        }

class TrackingEvent(db.Model):
    __tablename__ = 'tracking_events'
    
    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # pickup, in_transit, out_for_delivery, delivered
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    shipment = db.relationship('Shipment', backref=db.backref('tracking_events', lazy=True, order_by='TrackingEvent.timestamp'))
    
    def __init__(self, shipment_id, event_type, description, location=None):
        self.shipment_id = shipment_id
        self.event_type = event_type
        self.description = description
        self.location = location
    
    def to_dict(self):
        return {
            'id': self.id,
            'shipment_id': self.shipment_id,
            'event_type': self.event_type,
            'description': self.description,
            'location': self.location,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class Route(db.Model):
    __tablename__ = 'routes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    origin_city = db.Column(db.String(100), nullable=False)
    destination_city = db.Column(db.String(100), nullable=False)
    distance_km = db.Column(db.Float, nullable=False)
    estimated_duration_hours = db.Column(db.Float, nullable=False)
    transport_mode = db.Column(db.String(50), nullable=False)  # truck, plane, ship, train
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, name, origin_city, destination_city, distance_km, 
                 estimated_duration_hours, transport_mode):
        self.name = name
        self.origin_city = origin_city
        self.destination_city = destination_city
        self.distance_km = distance_km
        self.estimated_duration_hours = estimated_duration_hours
        self.transport_mode = transport_mode
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'origin_city': self.origin_city,
            'destination_city': self.destination_city,
            'distance_km': self.distance_km,
            'estimated_duration_hours': self.estimated_duration_hours,
            'transport_mode': self.transport_mode,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

