"""
Database Utilities for Froth Flotation Data Storage
==================================================

This module handles SQLite database operations for storing and retrieving
flotation process data, sensor readings, and control parameters.
"""

import sqlite3
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import os
import logging

# Set up comprehensive logging for Database Manager
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'database_manager.log')

# Configure logging - Only log errors and warnings
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Log service startup (WARNING level for important startup info)
logger.warning("Starting Froth Flotation Database Manager")
logger.warning(f"Log file: {log_file}")
logger.warning(f"Service: SQLite Database Manager")

class FlotationDatabase:
    """SQLite database manager for flotation data"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Get the absolute path to the database file
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(current_dir, "databases", "flotation_data.db")
        else:
            self.db_path = db_path
        self.init_database()
        self.initialize_default_user()
    
    def get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with required tables"""
        logger.info(f"Initializing database at: {self.db_path}")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
            
            # Create sensor_data table for real-time sensor readings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    pH REAL,
                    temperature REAL,
                    air_flow REAL,
                    kex_flowrate REAL,
                    sipx_flowrate REAL,
                    feed_pb REAL,
                    feed_zn REAL,
                    cell_level REAL,
                    impeller_speed REAL,
                    froth_height REAL,
                    pulp_density REAL,
                    nigrosine_min REAL,
                    nigrosine_max REAL,
                    pb_recovery REAL,
                    pb_concentrate REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create control_settings table for user control parameters
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS control_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    kex_flowrate REAL,
                    sipx_flowrate REAL,
                    feed_grade REAL,
                    impeller_speed REAL,
                    air_flow REAL,
                    ph_level REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create predictions table for ML model predictions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    predicted_pb REAL,
                    predicted_recovery REAL,
                    recovery_efficiency REAL,
                    confidence REAL,
                    status TEXT,
                    model_version TEXT DEFAULT 'v1.0',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create process_events table for important process events
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS process_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT,
                    event_description TEXT,
                    severity TEXT,
                    sensor_data_id INTEGER,
                    control_settings_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sensor_data_id) REFERENCES sensor_data (id),
                    FOREIGN KEY (control_settings_id) REFERENCES control_settings (id)
                )
            ''')
            
            # Create users table for authentication
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    email TEXT,
                    role TEXT DEFAULT 'operator',
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME
                )
            ''')
            
            # Create login_sessions table for session management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS login_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create alerts table for recommendation alerts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    alert_type TEXT NOT NULL,
                    alert_message TEXT NOT NULL,
                    severity TEXT DEFAULT 'warning',
                    parameter_name TEXT,
                    current_value REAL,
                    optimal_range TEXT,
                    is_dismissed BOOLEAN DEFAULT 0,
                    dismissed_at DATETIME,
                    dismissed_by_user_id INTEGER,
                    sensor_data_id INTEGER,
                    control_settings_id INTEGER,
                    predictions_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (dismissed_by_user_id) REFERENCES users (id),
                    FOREIGN KEY (sensor_data_id) REFERENCES sensor_data (id),
                    FOREIGN KEY (control_settings_id) REFERENCES control_settings (id),
                    FOREIGN KEY (predictions_id) REFERENCES predictions (id)
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON sensor_data(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_control_timestamp ON control_settings(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON process_events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON login_sessions(session_token)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(alert_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity)')
            
            conn.commit()
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def save_sensor_data(self, data: Dict[str, Any]) -> int:
        """Save sensor data to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sensor_data (
                    pH, temperature, air_flow, kex_flowrate, sipx_flowrate,
                    feed_pb, feed_zn, cell_level, impeller_speed, froth_height,
                    pulp_density, nigrosine_min, nigrosine_max, pb_recovery, pb_concentrate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('pH'),
                data.get('Temperature'),
                data.get('Pb_Rougher1_AirFlow'),
                data.get('Pb_Conditioner_KEX_Flowrate'),
                data.get('Pb_Rougher1_SIPX_Flowrate'),
                data.get('Feed_Pb'),
                data.get('Feed_Zn'),
                data.get('Cell_Level'),
                data.get('Impeller_Speed'),
                data.get('Froth_Height'),
                data.get('Pulp_Density'),
                data.get('Pb_Conditioner_Nigrosine_Flowrate_Min'),
                data.get('Pb_Conditioner_Nigrosine_Flowrate_Max'),
                data.get('Pb_Recovery'),
                data.get('Pb_Concentrate')
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def save_control_settings(self, controls: Dict[str, Any]) -> int:
        """Save control settings to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO control_settings (
                    kex_flowrate, sipx_flowrate, feed_grade, impeller_speed, air_flow, ph_level
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                controls.get('kex'),
                controls.get('sipx'),
                controls.get('feed_grade'),
                controls.get('impeller_speed'),
                controls.get('air'),
                controls.get('ph')
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def save_prediction(self, prediction: Dict[str, Any]) -> int:
        """Save ML prediction to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO predictions (
                    predicted_pb, predicted_recovery, recovery_efficiency, confidence, status
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                prediction.get('predicted_pb'),
                prediction.get('predicted_recovery'),
                prediction.get('recovery_efficiency'),
                prediction.get('confidence'),
                prediction.get('status')
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def save_process_event(self, event_type: str, description: str, severity: str = "INFO", 
                          sensor_data_id: Optional[int] = None, control_settings_id: Optional[int] = None) -> int:
        """Save process event to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO process_events (
                    event_type, event_description, severity, sensor_data_id, control_settings_id
                ) VALUES (?, ?, ?, ?, ?)
            ''', (event_type, description, severity, sensor_data_id, control_settings_id))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_latest_sensor_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get latest sensor data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM sensor_data 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_sensor_data_by_timerange(self, start_time: str, end_time: str) -> List[Dict[str, Any]]:
        """Get sensor data within a time range"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM sensor_data 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            ''', (start_time, end_time))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_latest_control_settings(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest control settings"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM control_settings 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_latest_predictions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest predictions"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM predictions 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_process_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get process events"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM process_events 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Count records in each table
            tables = ['sensor_data', 'control_settings', 'predictions', 'process_events']
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                stats[f'{table}_count'] = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM sensor_data')
            date_range = cursor.fetchone()
            if date_range[0]:
                stats['data_start'] = date_range[0]
                stats['data_end'] = date_range[1]
            
            # Get database size
            stats['db_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
            
            return stats
    
    def export_to_csv(self, table_name: str, filename: str = None):
        """Export table data to CSV"""
        if filename is None:
            filename = f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            df.to_csv(filename, index=False)
            print(f"Exported {len(df)} records to {filename}")
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to prevent database bloat"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)
            
            # Delete old data from all tables
            tables = ['sensor_data', 'control_settings', 'predictions', 'process_events']
            for table in tables:
                cursor.execute(f'DELETE FROM {table} WHERE timestamp < ?', (cutoff_date,))
                deleted_count = cursor.rowcount
                print(f"Deleted {deleted_count} old records from {table}")
            
            conn.commit()
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str, full_name: str = None, 
                   email: str = None, role: str = 'operator') -> int:
        """Create a new user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, email, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, full_name, email, role))
            
            conn.commit()
            return cursor.lastrowid
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user and return user info if successful"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT * FROM users 
                WHERE username = ? AND password_hash = ? AND is_active = 1
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            
            if user:
                # Update last login
                cursor.execute('''
                    UPDATE users SET last_login = ? WHERE id = ?
                ''', (datetime.now(), user['id']))
                
                conn.commit()
                return dict(user)
            
            return None
    
    def create_session(self, user_id: int, expires_in_hours: int = 24) -> str:
        """Create a new session for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=expires_in_hours)
            
            cursor.execute('''
                INSERT INTO login_sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, session_token, expires_at))
            
            conn.commit()
            return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate a session token and return user info if valid"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.* FROM users u
                JOIN login_sessions s ON u.id = s.user_id
                WHERE s.session_token = ? AND s.is_active = 1 
                AND s.expires_at > ? AND u.is_active = 1
            ''', (session_token, datetime.now()))
            
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def get_valid_sessions(self) -> List[Dict[str, Any]]:
        """Get all valid sessions"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # First, clean up expired sessions
            cursor.execute('''
                UPDATE login_sessions SET is_active = 0 
                WHERE expires_at <= ? AND is_active = 1
            ''', (datetime.now(),))
            
            # Then get valid sessions
            cursor.execute('''
                SELECT s.*, u.username, u.full_name FROM login_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.is_active = 1 AND s.expires_at > ? AND u.is_active = 1
                ORDER BY s.created_at DESC
            ''', (datetime.now(),))
            
            conn.commit()
            return [dict(row) for row in cursor.fetchall()]
    
    def logout_session(self, session_token: str) -> bool:
        """Logout a session by deactivating it"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE login_sessions SET is_active = 0 
                WHERE session_token = ?
            ''', (session_token,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def save_alert(self, alert_type: str, alert_message: str, severity: str = "warning",
                   parameter_name: Optional[str] = None, current_value: Optional[float] = None,
                   optimal_range: Optional[str] = None, sensor_data_id: Optional[int] = None,
                   control_settings_id: Optional[int] = None, predictions_id: Optional[int] = None) -> int:
        """Save an alert to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (
                    alert_type, alert_message, severity, parameter_name, current_value,
                    optimal_range, sensor_data_id, control_settings_id, predictions_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert_type, alert_message, severity, parameter_name, current_value,
                optimal_range, sensor_data_id, control_settings_id, predictions_id
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_recent_alerts(self, limit: int = 50, include_dismissed: bool = False) -> List[Dict[str, Any]]:
        """Get recent alerts from the database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if include_dismissed:
                cursor.execute('''
                    SELECT * FROM alerts 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            else:
                cursor.execute('''
                    SELECT * FROM alerts 
                    WHERE is_dismissed = 0
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def dismiss_alert(self, alert_id: int, user_id: Optional[int] = None) -> bool:
        """Dismiss an alert"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts 
                SET is_dismissed = 1, dismissed_at = ?, dismissed_by_user_id = ?
                WHERE id = ?
            ''', (datetime.now(), user_id, alert_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_alerts_by_type(self, alert_type: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get alerts by type"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM alerts 
                WHERE alert_type = ? AND is_dismissed = 0
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (alert_type, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_alerts_by_severity(self, severity: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get alerts by severity level"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM alerts 
                WHERE severity = ? AND is_dismissed = 0
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (severity, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def initialize_default_user(self):
        """Initialize the default admin user if it doesn't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if default user exists
            cursor.execute('SELECT id FROM users WHERE username = ?', ('LusangoM',))
            if not cursor.fetchone():
                # Create default admin user
                self.create_user(
                    username='LusangoM',
                    password='admin',
                    full_name='Lusango M',
                    role='admin'
                )
                print("✅ Default admin user 'LusangoM' created successfully")
            else:
                print("INFO: Default admin user 'LusangoM' already exists")

# Global database instance
db = FlotationDatabase()

# Export for use in other modules
__all__ = ['FlotationDatabase', 'db']
