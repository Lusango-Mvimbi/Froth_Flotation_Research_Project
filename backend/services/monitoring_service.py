"""
Monitoring and Logging Service
=============================

Comprehensive monitoring service for the prediction system including:
- Performance monitoring
- Prediction tracking
- Alert management
- System health monitoring
"""

import logging
import json
import time
import psutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests

# Configure specialized logging for predictions
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create prediction-specific logger
prediction_logger = logging.getLogger('predictions')
prediction_handler = logging.FileHandler('logs/predictions.log')
prediction_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)
prediction_logger.addHandler(prediction_handler)
prediction_logger.setLevel(logging.INFO)

class PredictionMonitor:
    """Monitors prediction performance and accuracy."""
    
    def __init__(self):
        self.prediction_stats = {
            'total_predictions': 0,
            'successful_predictions': 0,
            'failed_predictions': 0,
            'average_response_time': 0,
            'last_prediction_time': None,
            'accuracy_metrics': {},
            'drift_alerts': []
        }
        self.performance_history = []
        self.max_history_size = 10000
        
    def log_prediction_request(self, request_data: Dict[str, Any], 
                             response_data: Dict[str, Any], 
                             response_time: float, 
                             success: bool = True):
        """Log prediction request details."""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'request_data': request_data,
            'response_data': response_data if success else None,
            'response_time_ms': response_time * 1000,
            'success': success,
            'horizons': list(response_data.get('future_predictions', {}).keys()) if success else []
        }
        
        # Log to prediction-specific logger
        prediction_logger.info(f"PREDICTION_REQUEST: {json.dumps(log_entry)}")
        
        # Update statistics
        self.prediction_stats['total_predictions'] += 1
        if success:
            self.prediction_stats['successful_predictions'] += 1
        else:
            self.prediction_stats['failed_predictions'] += 1
        
        # Update average response time
        total_time = (self.prediction_stats['average_response_time'] * 
                     (self.prediction_stats['total_predictions'] - 1) + response_time)
        self.prediction_stats['average_response_time'] = total_time / self.prediction_stats['total_predictions']
        
        self.prediction_stats['last_prediction_time'] = datetime.now().isoformat()
        
        # Store in history
        self.performance_history.append(log_entry)
        if len(self.performance_history) > self.max_history_size:
            self.performance_history.pop(0)
        
        # Check for performance alerts
        self._check_performance_alerts(response_time, success)
    
    def log_prediction_validation(self, horizon: str, actual_value: float, 
                                predicted_value: float, accuracy_metrics: Dict[str, float]):
        """Log prediction validation results."""
        
        validation_entry = {
            'timestamp': datetime.now().isoformat(),
            'horizon': horizon,
            'actual_value': actual_value,
            'predicted_value': predicted_value,
            'error': abs(actual_value - predicted_value),
            'percentage_error': abs(actual_value - predicted_value) / abs(actual_value) if actual_value != 0 else 0,
            'accuracy_metrics': accuracy_metrics
        }
        
        prediction_logger.info(f"PREDICTION_VALIDATION: {json.dumps(validation_entry)}")
        
        # Update accuracy metrics
        if horizon not in self.prediction_stats['accuracy_metrics']:
            self.prediction_stats['accuracy_metrics'][horizon] = []
        
        self.prediction_stats['accuracy_metrics'][horizon].append(validation_entry)
        
        # Keep only recent validations
        if len(self.prediction_stats['accuracy_metrics'][horizon]) > 1000:
            self.prediction_stats['accuracy_metrics'][horizon] = \
                self.prediction_stats['accuracy_metrics'][horizon][-1000:]
    
    def log_drift_detection(self, horizon: str, drift_detected: bool, 
                          drift_score: float, details: Dict[str, Any]):
        """Log model drift detection results."""
        
        drift_entry = {
            'timestamp': datetime.now().isoformat(),
            'horizon': horizon,
            'drift_detected': drift_detected,
            'drift_score': drift_score,
            'details': details
        }
        
        prediction_logger.warning(f"DRIFT_DETECTION: {json.dumps(drift_entry)}")
        
        if drift_detected:
            self.prediction_stats['drift_alerts'].append(drift_entry)
            logger.warning(f"🚨 Model drift detected for {horizon} horizon: score={drift_score:.3f}")
    
    def _check_performance_alerts(self, response_time: float, success: bool):
        """Check for performance-related alerts."""
        
        # Alert on slow predictions (>1 second)
        if response_time > 1.0:
            logger.warning(f"⚠️ Slow prediction detected: {response_time:.3f}s")
        
        # Alert on failed predictions
        if not success:
            logger.error("❌ Prediction request failed")
        
        # Alert on low success rate
        if self.prediction_stats['total_predictions'] > 10:
            success_rate = (self.prediction_stats['successful_predictions'] / 
                          self.prediction_stats['total_predictions'])
            if success_rate < 0.95:
                logger.warning(f"⚠️ Low prediction success rate: {success_rate:.2%}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary."""
        
        recent_predictions = [p for p in self.performance_history 
                            if datetime.fromisoformat(p['timestamp']) > 
                            datetime.now() - timedelta(hours=1)]
        
        summary = {
            'current_stats': self.prediction_stats.copy(),
            'recent_predictions_count': len(recent_predictions),
            'recent_avg_response_time': sum(p['response_time_ms'] for p in recent_predictions) / len(recent_predictions) if recent_predictions else 0,
            'recent_success_rate': sum(1 for p in recent_predictions if p['success']) / len(recent_predictions) if recent_predictions else 0,
            'active_drift_alerts': len([a for a in self.prediction_stats['drift_alerts'] 
                                      if datetime.fromisoformat(a['timestamp']) > 
                                      datetime.now() - timedelta(hours=24)])
        }
        
        return summary

class SystemMonitor:
    """Monitors overall system health and performance."""
    
    def __init__(self):
        self.monitoring_active = False
        self.monitoring_thread = None
        self.system_stats = {
            'cpu_usage': [],
            'memory_usage': [],
            'disk_usage': [],
            'network_io': [],
            'service_health': {}
        }
        self.alert_thresholds = {
            'cpu_threshold': 80,
            'memory_threshold': 85,
            'disk_threshold': 90
        }
        
    def start_monitoring(self, interval: int = 60):
        """Start continuous system monitoring."""
        
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info(f"🔍 System monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("🛑 System monitoring stopped")
    
    def _monitoring_loop(self, interval: int):
        """Main monitoring loop."""
        
        while self.monitoring_active:
            try:
                # Collect system metrics
                metrics = self._collect_system_metrics()
                
                # Store metrics
                self._store_metrics(metrics)
                
                # Check thresholds and generate alerts
                self._check_system_alerts(metrics)
                
                # Check service health
                service_health = self._check_service_health()
                self.system_stats['service_health'] = service_health
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics."""
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'usage_percent': psutil.cpu_percent(interval=1),
                'cores': psutil.cpu_count(),
                'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'usage_percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'free': psutil.disk_usage('/').free,
                'usage_percent': psutil.disk_usage('/').percent
            },
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv,
                'packets_sent': psutil.net_io_counters().packets_sent,
                'packets_recv': psutil.net_io_counters().packets_recv
            }
        }
        
        return metrics
    
    def _store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in history."""
        
        # Store in appropriate lists
        self.system_stats['cpu_usage'].append({
            'timestamp': metrics['timestamp'],
            'usage_percent': metrics['cpu']['usage_percent']
        })
        
        self.system_stats['memory_usage'].append({
            'timestamp': metrics['timestamp'],
            'usage_percent': metrics['memory']['usage_percent']
        })
        
        self.system_stats['disk_usage'].append({
            'timestamp': metrics['timestamp'],
            'usage_percent': metrics['disk']['usage_percent']
        })
        
        self.system_stats['network_io'].append({
            'timestamp': metrics['timestamp'],
            'bytes_sent': metrics['network']['bytes_sent'],
            'bytes_recv': metrics['network']['bytes_recv']
        })
        
        # Keep only recent data (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        for stat_list in [self.system_stats['cpu_usage'], 
                         self.system_stats['memory_usage'],
                         self.system_stats['disk_usage'],
                         self.system_stats['network_io']]:
            while (stat_list and 
                   datetime.fromisoformat(stat_list[0]['timestamp']) < cutoff_time):
                stat_list.pop(0)
        
        # Log system metrics
        logger.info(f"SYSTEM_METRICS: {json.dumps(metrics)}")
    
    def _check_system_alerts(self, metrics: Dict[str, Any]):
        """Check system metrics against thresholds."""
        
        alerts = []
        
        # CPU usage alert
        if metrics['cpu']['usage_percent'] > self.alert_thresholds['cpu_threshold']:
            alerts.append(f"High CPU usage: {metrics['cpu']['usage_percent']:.1f}%")
        
        # Memory usage alert
        if metrics['memory']['usage_percent'] > self.alert_thresholds['memory_threshold']:
            alerts.append(f"High memory usage: {metrics['memory']['usage_percent']:.1f}%")
        
        # Disk usage alert
        if metrics['disk']['usage_percent'] > self.alert_thresholds['disk_threshold']:
            alerts.append(f"High disk usage: {metrics['disk']['usage_percent']:.1f}%")
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"🚨 SYSTEM_ALERT: {alert}")
    
    def _check_service_health(self) -> Dict[str, Any]:
        """Check health of all services."""
        
        services = {
            'backend': 'http://localhost:8000/docs',
            'auth': 'http://localhost:8051/',
            'predictions': 'http://localhost:8000/api/future-predictions'
        }
        
        health_status = {}
        
        for service_name, url in services.items():
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                response_time = time.time() - start_time
                
                health_status[service_name] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'timestamp': datetime.now().isoformat()
                }
                
                if response.status_code != 200:
                    logger.warning(f"⚠️ Service {service_name} returned status {response.status_code}")
                
            except Exception as e:
                health_status[service_name] = {
                    'status': 'unreachable',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                logger.error(f"❌ Service {service_name} is unreachable: {e}")
        
        return health_status
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status summary."""
        
        recent_cpu = [m for m in self.system_stats['cpu_usage'] 
                     if datetime.fromisoformat(m['timestamp']) > 
                     datetime.now() - timedelta(minutes=5)]
        
        recent_memory = [m for m in self.system_stats['memory_usage'] 
                        if datetime.fromisoformat(m['timestamp']) > 
                        datetime.now() - timedelta(minutes=5)]
        
        status = {
            'monitoring_active': self.monitoring_active,
            'current_metrics': {
                'cpu_usage': sum(m['usage_percent'] for m in recent_cpu) / len(recent_cpu) if recent_cpu else 0,
                'memory_usage': sum(m['usage_percent'] for m in recent_memory) / len(recent_memory) if recent_memory else 0,
                'services_healthy': sum(1 for s in self.system_stats['service_health'].values() 
                                      if s.get('status') == 'healthy'),
                'total_services': len(self.system_stats['service_health'])
            },
            'service_health': self.system_stats['service_health'],
            'alert_thresholds': self.alert_thresholds
        }
        
        return status

class AlertManager:
    """Manages alerts and notifications."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.alert_history = []
        self.active_alerts = {}
        
    def send_alert(self, alert_type: str, message: str, severity: str = 'WARNING'):
        """Send alert through configured channels."""
        
        alert = {
            'id': f"{alert_type}_{int(time.time())}",
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'acknowledged': False
        }
        
        # Store alert
        self.alert_history.append(alert)
        self.active_alerts[alert['id']] = alert
        
        # Log alert
        logger.warning(f"🚨 ALERT [{severity}] {alert_type}: {message}")
        
        # Send through configured channels
        self._send_email_alert(alert)
        self._send_webhook_alert(alert)
        
        return alert['id']
    
    def _send_email_alert(self, alert: Dict[str, Any]):
        """Send email alert (if configured)."""
        
        smtp_config = self.config.get('alerts', {}).get('smtp', {})
        if not smtp_config.get('server'):
            return
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = smtp_config.get('from_email')
            msg['To'] = ', '.join(smtp_config.get('to_emails', []))
            msg['Subject'] = f"[{alert['severity']}] Flotation System Alert: {alert['type']}"
            
            body = f"""
            Froth Flotation Digital Twin Alert
            
            Type: {alert['type']}
            Severity: {alert['severity']}
            Time: {alert['timestamp']}
            
            Message: {alert['message']}
            
            Alert ID: {alert['id']}
            
            Please check the system status and take appropriate action.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_config.get('server'), smtp_config.get('port', 587))
            server.starttls()
            server.login(smtp_config.get('username'), smtp_config.get('password'))
            
            text = msg.as_string()
            server.sendmail(smtp_config.get('from_email'), smtp_config.get('to_emails'), text)
            server.quit()
            
            logger.info(f"📧 Email alert sent for {alert['id']}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _send_webhook_alert(self, alert: Dict[str, Any]):
        """Send webhook alert (if configured)."""
        
        webhook_url = self.config.get('alerts', {}).get('webhook_url')
        if not webhook_url:
            return
        
        try:
            payload = {
                'text': f"🚨 *{alert['severity']}* Alert: {alert['type']}\n{alert['message']}\nTime: {alert['timestamp']}"
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"📱 Webhook alert sent for {alert['id']}")
            else:
                logger.warning(f"Webhook alert failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an active alert."""
        
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id]['acknowledged'] = True
            self.active_alerts[alert_id]['acknowledged_at'] = datetime.now().isoformat()
            logger.info(f"✅ Alert {alert_id} acknowledged")
        
    def resolve_alert(self, alert_id: str):
        """Resolve an active alert."""
        
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id]['resolved'] = True
            self.active_alerts[alert_id]['resolved_at'] = datetime.now().isoformat()
            del self.active_alerts[alert_id]
            logger.info(f"✅ Alert {alert_id} resolved")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get list of active alerts."""
        return list(self.active_alerts.values())

# Global monitoring instances
prediction_monitor = PredictionMonitor()
system_monitor = SystemMonitor()
alert_manager = AlertManager()

def initialize_monitoring(config: Dict[str, Any] = None):
    """Initialize monitoring services."""
    
    global alert_manager, system_monitor
    
    # Initialize alert manager with config
    if config:
        alert_manager = AlertManager(config)
    
    # Start system monitoring
    system_monitor.start_monitoring(interval=60)
    
    logger.info("🔍 Monitoring services initialized")

def get_monitoring_status() -> Dict[str, Any]:
    """Get comprehensive monitoring status."""
    
    return {
        'prediction_performance': prediction_monitor.get_performance_summary(),
        'system_status': system_monitor.get_system_status(),
        'active_alerts': alert_manager.get_active_alerts(),
        'monitoring_timestamp': datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Example usage
    print("🔍 Starting monitoring service...")
    
    # Initialize monitoring
    initialize_monitoring()
    
    # Keep monitoring running
    try:
        while True:
            time.sleep(10)
            status = get_monitoring_status()
            print(f"Monitoring status: {json.dumps(status, indent=2)}")
    except KeyboardInterrupt:
        print("🛑 Stopping monitoring service...")
        system_monitor.stop_monitoring()
