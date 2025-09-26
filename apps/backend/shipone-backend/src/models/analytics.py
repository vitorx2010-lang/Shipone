from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from src.models.user import db
import json

class PredictiveModel(db.Model):
    __tablename__ = 'predictive_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # delivery_time, cost_optimization, route_optimization
    version = db.Column(db.String(20), nullable=False)
    accuracy = db.Column(db.Float, nullable=True)
    parameters = db.Column(db.Text, nullable=True)  # JSON string with model parameters
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, name, model_type, version, accuracy=None, parameters=None):
        self.name = name
        self.model_type = model_type
        self.version = version
        self.accuracy = accuracy
        self.parameters = json.dumps(parameters) if parameters else None
    
    def get_parameters(self):
        return json.loads(self.parameters) if self.parameters else {}
    
    def set_parameters(self, parameters):
        self.parameters = json.dumps(parameters)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'model_type': self.model_type,
            'version': self.version,
            'accuracy': self.accuracy,
            'parameters': self.get_parameters(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DeliveryPrediction(db.Model):
    __tablename__ = 'delivery_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('predictive_models.id'), nullable=False)
    predicted_delivery_date = db.Column(db.DateTime, nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)  # 0.0 to 1.0
    factors = db.Column(db.Text, nullable=True)  # JSON string with prediction factors
    actual_delivery_date = db.Column(db.DateTime, nullable=True)
    accuracy_score = db.Column(db.Float, nullable=True)  # Calculated after delivery
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    shipment = db.relationship('Shipment', backref=db.backref('delivery_predictions', lazy=True))
    model = db.relationship('PredictiveModel', backref=db.backref('predictions', lazy=True))
    
    def __init__(self, shipment_id, model_id, predicted_delivery_date, confidence_score, factors=None):
        self.shipment_id = shipment_id
        self.model_id = model_id
        self.predicted_delivery_date = predicted_delivery_date
        self.confidence_score = confidence_score
        self.factors = json.dumps(factors) if factors else None
    
    def get_factors(self):
        return json.loads(self.factors) if self.factors else {}
    
    def set_factors(self, factors):
        self.factors = json.dumps(factors)
    
    def calculate_accuracy(self):
        if self.actual_delivery_date and self.predicted_delivery_date:
            predicted_date = self.predicted_delivery_date.date()
            actual_date = self.actual_delivery_date.date()
            diff_days = abs((actual_date - predicted_date).days)
            
            # Accuracy decreases with days difference
            if diff_days == 0:
                self.accuracy_score = 1.0
            elif diff_days == 1:
                self.accuracy_score = 0.8
            elif diff_days <= 3:
                self.accuracy_score = 0.6
            elif diff_days <= 7:
                self.accuracy_score = 0.4
            else:
                self.accuracy_score = 0.2
    
    def to_dict(self):
        return {
            'id': self.id,
            'shipment_id': self.shipment_id,
            'model_id': self.model_id,
            'predicted_delivery_date': self.predicted_delivery_date.isoformat() if self.predicted_delivery_date else None,
            'confidence_score': self.confidence_score,
            'factors': self.get_factors(),
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'accuracy_score': self.accuracy_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class RouteOptimization(db.Model):
    __tablename__ = 'route_optimizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    origin_city = db.Column(db.String(100), nullable=False)
    destination_city = db.Column(db.String(100), nullable=False)
    optimized_route = db.Column(db.Text, nullable=False)  # JSON with waypoints
    estimated_time_hours = db.Column(db.Float, nullable=False)
    estimated_cost = db.Column(db.Float, nullable=False)
    fuel_efficiency = db.Column(db.Float, nullable=True)  # km per liter
    carbon_footprint = db.Column(db.Float, nullable=True)  # kg CO2
    traffic_factor = db.Column(db.Float, default=1.0)
    weather_factor = db.Column(db.Float, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, name, origin_city, destination_city, optimized_route, 
                 estimated_time_hours, estimated_cost):
        self.name = name
        self.origin_city = origin_city
        self.destination_city = destination_city
        self.optimized_route = json.dumps(optimized_route)
        self.estimated_time_hours = estimated_time_hours
        self.estimated_cost = estimated_cost
    
    def get_route(self):
        return json.loads(self.optimized_route)
    
    def set_route(self, route):
        self.optimized_route = json.dumps(route)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'origin_city': self.origin_city,
            'destination_city': self.destination_city,
            'optimized_route': self.get_route(),
            'estimated_time_hours': self.estimated_time_hours,
            'estimated_cost': self.estimated_cost,
            'fuel_efficiency': self.fuel_efficiency,
            'carbon_footprint': self.carbon_footprint,
            'traffic_factor': self.traffic_factor,
            'weather_factor': self.weather_factor,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PerformanceMetric(db.Model):
    __tablename__ = 'performance_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    metric_unit = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(50), nullable=False)  # delivery, cost, efficiency, customer_satisfaction
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    additional_data = db.Column(db.Text, nullable=True)  # JSON with additional data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, metric_name, metric_value, category, period_start, period_end, 
                 metric_unit=None, additional_data=None):
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.category = category
        self.period_start = period_start
        self.period_end = period_end
        self.metric_unit = metric_unit
        self.additional_data = json.dumps(additional_data) if additional_data else None
    
    def get_additional_data(self):
        return json.loads(self.additional_data) if self.additional_data else {}
    
    def set_additional_data(self, data):
        self.additional_data = json.dumps(data)
    
    def to_dict(self):
        return {
            'id': self.id,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'metric_unit': self.metric_unit,
            'category': self.category,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'additional_data': self.get_additional_data(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

