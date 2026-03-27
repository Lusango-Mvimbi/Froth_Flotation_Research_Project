# Architecture Guide

## System Architecture Overview

The Froth Flotation Digital Twin system follows a modern, scalable architecture based on SOLID principles and microservices patterns.

## Architecture Principles

### SOLID Principles Implementation

1. **Single Responsibility Principle (SRP)**
   - Each service has one clear purpose
   - Data generation, ML prediction, optimization, and authentication are separate services

2. **Open/Closed Principle (OCP)**
   - Services are extensible without modification
   - New prediction models can be added without changing existing code

3. **Liskov Substitution Principle (LSP)**
   - Interfaces allow for interchangeable implementations
   - Different ML models can be swapped without breaking the system

4. **Interface Segregation Principle (ISP)**
   - Clean, focused interfaces
   - Services only depend on methods they actually use

5. **Dependency Inversion Principle (DIP)**
   - High-level modules don't depend on low-level modules
   - Both depend on abstractions

## System Layers

### 1. Presentation Layer (Frontend)
- **Technology**: React with TypeScript
- **Components**: Dashboard, Login, Charts, Controls
- **State Management**: React hooks and contexts
- **Styling**: Tailwind CSS
- **Real-time Updates**: WebSocket connections

### 2. API Layer (Backend)
- **Technology**: FastAPI with Python
- **Services**: RESTful API endpoints
- **Authentication**: JWT-based security
- **Documentation**: Auto-generated OpenAPI/Swagger docs

### 3. Business Logic Layer
- **Data Generation**: Realistic flotation process simulation
- **ML Services**: Prediction and optimization algorithms
- **Optimization**: Dynamic process optimization
- **Authentication**: User management and security

### 4. Data Layer
- **Database**: SQLite for development, PostgreSQL for production
- **Models**: Trained ML models (Random Forest, XGBoost)
- **Storage**: File-based model storage with metadata

## Service Architecture

### Core Services

1. **Data Generator Service**
   - Generates realistic flotation process data
   - Simulates sensor readings and process variables
   - Maintains process state and dynamics

2. **ML Model Service**
   - Loads and manages trained models
   - Provides prediction capabilities
   - Handles model versioning and updates

3. **Optimization Service**
   - Implements process optimization algorithms
   - Generates recommendations
   - Handles constraint management

4. **Future Prediction Service**
   - Multi-horizon predictions (5min, 15min, 30min, 60min)
   - Confidence interval calculations
   - Time-series analysis

5. **Authentication Service**
   - User authentication and authorization
   - JWT token management
   - Session handling

### Database Schema

#### Sensor Data Table
```sql
CREATE TABLE flotation_sensor_data (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    Feed_Pb REAL,
    Pb_Conditioner_KEX_Flowrate REAL,
    Pb_Rougher1_SIPX_Flowrate REAL,
    Pb_Rougher1_AirFlow REAL,
    Pb_Rougher1_Level REAL
);
```

#### Calculated Values Table
```sql
CREATE TABLE flotation_calculated_values (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    Actual_Pb_Concentrate REAL,
    Actual_Pb_Recovery REAL,
    Predicted_Pb_Concentrate REAL,
    Predicted_Pb_Recovery REAL
);
```

#### Optimization Data Table
```sql
CREATE TABLE flotation_optimization_data (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    optimal_kex REAL,
    optimal_sipx REAL,
    recommendations TEXT,
    process_variability REAL
);
```

## Data Flow

### Real-time Data Flow
1. Data Generator creates process data
2. ML Model Service processes data for predictions
3. Optimization Service generates recommendations
4. Data is stored in database
5. Frontend receives updates via WebSocket
6. Dashboard displays real-time information

### Prediction Flow
1. Current process data is collected
2. ML models are applied for predictions
3. Confidence intervals are calculated
4. Results are formatted and returned
5. Frontend displays predictions with visualizations

## Security Architecture

### Authentication Flow
1. User provides credentials
2. Authentication service validates credentials
3. JWT token is generated and returned
4. Token is included in subsequent requests
5. Token is validated on each API call

### Authorization
- Role-based access control
- Token expiration and refresh
- Secure password hashing
- CORS configuration

## Deployment Architecture

### Development Environment
- Single machine deployment
- SQLite database
- Local file storage
- Development servers

### Production Environment
- Containerized deployment (Docker)
- PostgreSQL database
- Cloud storage for models
- Load balancing and scaling
- Monitoring and logging

## Performance Considerations

### Optimization Strategies
- Model caching and lazy loading
- Database connection pooling
- Async processing for heavy computations
- Efficient data serialization
- Frontend state management optimization

### Scalability
- Horizontal scaling of API services
- Database sharding for large datasets
- CDN for static assets
- Microservices architecture
- Container orchestration

## Monitoring and Logging

### Logging Strategy
- Centralized logging with structured format
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- Log rotation and archival
- Performance metrics logging

### Monitoring
- Health check endpoints
- Performance metrics collection
- Error tracking and alerting
- Resource usage monitoring
- User activity tracking

## Future Enhancements

### Planned Improvements
- Microservices containerization
- Advanced ML model deployment
- Real-time streaming analytics
- Advanced visualization capabilities
- Mobile application support
- Integration with external systems
