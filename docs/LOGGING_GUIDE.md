# 📋 Logging Guide - Froth Flotation Digital Twin

## 🎯 **Overview**

This guide explains the comprehensive logging system implemented across all services in the Froth Flotation Digital Twin project. The logging system is designed to provide developers with clear, actionable information for debugging and monitoring.

## 🏗️ **Logging Architecture**

### **Centralized Configuration**
- **Location**: `backend/utils/logging_config.py`
- **Purpose**: Provides consistent logging configuration across all services
- **Features**: Colored console output, detailed file logging, structured formatting

### **Service-Specific Loggers**
Each service has its own dedicated logger with appropriate log levels:

| Service | Logger Name | Log File | Level |
|---------|-------------|----------|-------|
| FastAPI Data Service | `flotation_data_service` | `logs/flotation_data_service.log` | INFO |
| Flask Auth Service | `authentication_service` | `logs/authentication_service.log` | INFO |
| Database Manager | `database_manager` | `logs/database_manager.log` | INFO |
| ML Model Manager | `ml_model_manager` | `logs/ml_model_manager.log` | INFO |

## 📝 **Log Format**

### **Console Output (Colored)**
```
2025-08-14 20:30:15 - INFO - 🚀 Starting Froth Flotation Data Service
2025-08-14 20:30:15 - INFO - 📁 Log file: /path/to/logs/flotation_data_service.log
2025-08-14 20:30:15 - INFO - 🔧 Service: FastAPI WebSocket Server
2025-08-14 20:30:15 - INFO - 🌐 Port: 8000
```

### **File Output (Detailed)**
```
2025-08-14 20:30:15,123 - flotation_data_service - INFO - [flotation_data_service.py:45] - main() - 🚀 Starting Froth Flotation Data Service
2025-08-14 20:30:15,124 - flotation_data_service - INFO - [flotation_data_service.py:46] - main() - 📁 Log file: /path/to/logs/flotation_data_service.log
2025-08-14 20:30:15,125 - flotation_data_service - INFO - [flotation_data_service.py:47] - main() - 🔧 Service: FastAPI WebSocket Server
2025-08-14 20:30:15,126 - flotation_data_service - INFO - [flotation_data_service.py:48] - main() - 🌐 Port: 8000
```

## 🔧 **Logging Levels**

### **DEBUG**
- Detailed diagnostic information
- Function entry/exit points
- Variable values for debugging
- **Use**: Development and troubleshooting

### **INFO**
- General operational messages
- Service startup/shutdown
- Successful operations
- **Use**: Normal operation monitoring

### **WARNING**
- Potential issues that don't stop operation
- Deprecated feature usage
- Performance concerns
- **Use**: Monitoring for potential problems

### **ERROR**
- Errors that don't stop the service
- Failed operations
- Invalid input handling
- **Use**: Error tracking and debugging

### **CRITICAL**
- Critical errors that may stop the service
- System failures
- Security violations
- **Use**: Immediate attention required

## 📊 **Log Categories**

### **Service Lifecycle**
```python
# Startup
logger.info("🚀 Starting Froth Flotation Data Service")
logger.info(f"📁 Log file: {log_file}")
logger.info(f"🔧 Service: FastAPI WebSocket Server")
logger.info(f"🌐 Port: 8000")

# Shutdown
logger.info("🛑 Shutting down Froth Flotation Data Service")
```

### **API Operations**
```python
# Request logging
logger.info(f"✅ GET /api/current-data - 200 (0.045s)")

# Error logging
logger.error(f"❌ POST /api/control-settings - 400 - Invalid parameters")
```

### **Database Operations**
```python
# Success
logger.info(f"✅ DB INSERT on sensor_data - Record ID: 12345")

# Error
logger.error(f"❌ DB SELECT on sensor_data - Connection timeout")
```

### **Authentication Events**
```python
# Login success
logger.info(f"✅ Auth LOGIN - User: LusangoM")

# Login failure
logger.error(f"❌ Auth LOGIN - User: invalid_user - Invalid credentials")
```

### **WebSocket Events**
```python
# Connection
logger.info(f"🔌 WebSocket CONNECT - Client: 192.168.1.100")

# Message
logger.info(f"🔌 WebSocket MESSAGE - Client: 192.168.1.100 - Data: 2KB")
```

### **ML Predictions**
```python
# Prediction success
logger.info(f"🤖 ML Prediction - Model: RandomForest, Confidence: 0.92, Result: Optimal")

# Model loading
logger.info(f"🤖 ML Model loaded - RandomForest_v1.0.pkl - 2.3MB")
```

## 🛠️ **Using the Logging System**

### **Basic Usage**
```python
import logging
from backend.utils.logging_config import setup_logging

# Set up logger for your service
logger = setup_logging('my_service', 'INFO')

# Log messages
logger.info("Service started successfully")
logger.warning("High memory usage detected")
logger.error("Database connection failed")
```

### **Advanced Usage**
```python
from backend.utils.logging_config import (
    log_service_startup,
    log_error_with_context,
    log_api_request,
    log_database_operation
)

# Service startup
log_service_startup(logger, "My Service", 8080)

# Error with context
try:
    # Some operation
    pass
except Exception as e:
    log_error_with_context(logger, e, "data_processing")

# API request
log_api_request(logger, "GET", "/api/data", 200, 0.045)

# Database operation
log_database_operation(logger, "INSERT", "sensor_data", True, "Record ID: 12345")
```

## 📁 **Log File Management**

### **Log File Locations**
```
logs/
├── flotation_data_service.log    # FastAPI service logs
├── authentication_service.log    # Flask auth service logs
├── database_manager.log          # Database operation logs
├── ml_model_manager.log          # ML model logs
└── test_report.json              # Test results
```

### **Log Rotation**
- **Size Limit**: 10MB per log file
- **Backup Count**: 5 rotated files
- **Compression**: Gzip compression for old logs

### **Log Cleanup**
```bash
# Clean old log files (older than 30 days)
find logs/ -name "*.log.*" -mtime +30 -delete

# Compress old logs
gzip logs/*.log.old
```

## 🔍 **Debugging with Logs**

### **Common Debugging Scenarios**

#### **1. Service Won't Start**
```bash
# Check service logs
tail -f logs/flotation_data_service.log
tail -f logs/authentication_service.log
```

#### **2. API Endpoint Issues**
```bash
# Look for API request logs
grep "API" logs/flotation_data_service.log
grep "POST\|GET" logs/flotation_data_service.log
```

#### **3. Database Connection Problems**
```bash
# Check database logs
grep "ERROR" logs/database_manager.log
grep "connection" logs/database_manager.log
```

#### **4. Authentication Issues**
```bash
# Check auth logs
grep "Auth" logs/authentication_service.log
grep "LOGIN" logs/authentication_service.log
```

### **Log Analysis Tools**

#### **Real-time Monitoring**
```bash
# Monitor all logs in real-time
tail -f logs/*.log

# Monitor specific service
tail -f logs/flotation_data_service.log | grep ERROR
```

#### **Log Search**
```bash
# Search for errors across all logs
grep -r "ERROR" logs/

# Search for specific user activity
grep "LusangoM" logs/authentication_service.log
```

#### **Log Statistics**
```bash
# Count log entries by level
grep -c "ERROR" logs/*.log
grep -c "WARNING" logs/*.log
grep -c "INFO" logs/*.log
```

## 🧪 **Testing Logging**

### **Run Logging Tests**
```bash
# Run comprehensive logging test
python test_system_logging.py

# Test specific service logging
python -c "from backend.utils.logging_config import get_flotation_data_logger; logger = get_flotation_data_logger(); logger.info('Test message')"
```

### **Verify Log Output**
```bash
# Check if logs are being written
ls -la logs/
tail -5 logs/flotation_data_service.log
```

## 📈 **Performance Monitoring**

### **Log Performance Metrics**
```python
# Response time logging
import time

start_time = time.time()
# ... operation ...
response_time = time.time() - start_time
logger.info(f"Operation completed in {response_time:.3f}s")
```

### **Memory Usage Logging**
```python
import psutil

memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
logger.info(f"Memory usage: {memory_usage:.1f}MB")
```

## 🔒 **Security Considerations**

### **Sensitive Data**
- **Never log**: Passwords, API keys, personal information
- **Sanitize**: User input, database queries
- **Mask**: Sensitive data in error messages

### **Log Access Control**
- **File Permissions**: Restrict log file access
- **Network Security**: Secure log transmission
- **Audit Trail**: Track log access

## 🎯 **Best Practices**

### **Do's**
- ✅ Use appropriate log levels
- ✅ Include context in log messages
- ✅ Use structured logging for complex data
- ✅ Log both success and failure cases
- ✅ Include timestamps and service identification

### **Don'ts**
- ❌ Log sensitive information
- ❌ Use print statements instead of logging
- ❌ Log too much or too little
- ❌ Use generic error messages
- ❌ Ignore log file rotation

## 📞 **Support**

For logging-related issues or questions:
1. Check the log files first
2. Review this documentation
3. Run the logging test suite
4. Contact the development team

---

**Last Updated**: August 14, 2025
**Version**: 1.0.0
