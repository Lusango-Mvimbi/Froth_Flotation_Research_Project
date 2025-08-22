# Froth Flotation Digital Twin Research Project

## 🎯 Project Overview

A comprehensive digital twin system for froth flotation processes, featuring real-time ML predictions, dynamic optimization, and an interactive dashboard. Built with SOLID principles and modern software architecture.

## 🏗️ Architecture

### SOLID Principles Implementation

- **Single Responsibility**: Each service has one clear purpose
- **Open/Closed**: Services are extensible without modification
- **Liskov Substitution**: Interfaces allow for interchangeable implementations
- **Interface Segregation**: Clean, focused interfaces
- **Dependency Inversion**: High-level modules don't depend on low-level modules

### System Components

```
├── backend/
│   ├── services/           # Core business logic (SOLID architecture)
│   │   ├── interfaces.py   # Abstract interfaces
│   │   ├── data_generator.py
│   │   ├── ml_model_service.py
│   │   ├── optimization_service.py
│   │   ├── service_orchestrator.py
│   │   └── dynamic_ranges_service.py
│   ├── models/            # Database models
│   ├── trained_models/    # ML model artifacts
│   └── tests/            # Unit tests
├── frontend/              # React TypeScript dashboard
└── docs/                 # Documentation
```

## 🚀 Features

### Phase 1: Core Infrastructure ✅
- [x] SOLID architecture implementation
- [x] ML model integration (Random Forest, R² = 0.973)
- [x] Real-time data generation
- [x] Database integration (SQLite)
- [x] Authentication system

### Phase 2: Dynamic System ✅
- [x] Dynamic percentile-based reagent classification
- [x] Realistic parameter impact analysis
- [x] KEX/SIPX control optimization
- [x] Process status analysis
- [x] Real-time dashboard updates

### Phase 3: Production Ready ✅
- [x] Clean workspace organization
- [x] SOLID principles compliance
- [x] Proper file naming conventions
- [x] Comprehensive documentation

## 🎛️ Control Parameters

### Primary Controls (Operator-Adjustable)
- **KEX Flow Rate**: 0-100 L/min (Collector reagent)
- **SIPX Flow Rate**: 0-60 L/min (Frother reagent)

### Process Variables (Auto-Generated)
- **Feed_Pb**: 0.5-2.5% (Feed lead grade)
- **Feed_Zn**: 8.0-12.5% (Feed zinc grade)
- **AirFlow**: 8-12 L/min (Cell aeration)
- **Level**: 25-55% (Cell level)

## 📊 ML Model Performance

- **Model Type**: Random Forest Regressor
- **R² Score**: 0.973 (97.3% accuracy)
- **RMSE**: 1.23%
- **MAE**: 0.77%
- **Features**: 200 (including lag features)

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- SQLite

### Backend Setup
```bash
pip install -r requirements.txt
cd backend
python services/flotation_data_service_refactored.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Quick Start
```bash
# Use the launch script
python launch.py
```

## 🔧 Configuration

### Dynamic Ranges
The system uses percentile-based classification:
- **Low**: 25th percentile of realistic ranges
- **Optimal**: 25th-75th percentile range
- **High**: Above 75th percentile
- **Excessive**: 95th percentile (triggers critical status)

### Update Intervals
- **Data Generation**: 4 seconds
- **Frontend Polling**: 4 seconds
- **Cache Duration**: 4 seconds

## 📈 Key Metrics

### Prediction Accuracy
- Pb Concentrate: ±1.5% variation
- Recovery Rate: ±2.0% variation
- Process Status: Real-time classification

### Performance
- **API Response Time**: <100ms
- **Data Update Frequency**: 4 seconds
- **Rate Limiting**: 120 requests/minute

## 🔒 Security

- JWT-based authentication
- Rate limiting middleware
- Input validation
- SQL injection protection

## 📝 API Endpoints

### Core Endpoints
- `GET /api/current-data` - Real-time process data
- `GET /api/control-settings` - Current control parameters
- `POST /api/control-settings` - Update control parameters
- `GET /api/optimization` - Optimization recommendations
- `POST /api/auth/login` - User authentication

### WebSocket
- `ws://localhost:8000/ws` - Real-time data streaming

## 🧪 Testing

```bash
# Run backend tests
cd backend/tests
python -m pytest

# Run frontend tests
cd frontend
npm test
```

## 📚 Documentation

- [Project Summary](PROJECT_SUMMARY.md)
- [Quick Start Guide](QUICK_START.md)
- [API Documentation](docs/api.md)
- [Architecture Guide](docs/architecture.md)

## 🤝 Contributing

1. Follow SOLID principles
2. Write unit tests for new features
3. Update documentation
4. Use conventional commit messages

## 📄 License

This project is part of academic research on froth flotation digital twins.

## 🎓 Research Context

This digital twin system demonstrates the application of:
- Machine learning in mineral processing
- Real-time process optimization
- SOLID software architecture principles
- Modern web technologies for industrial applications

---

**Status**: ✅ Production Ready  
**Last Updated**: August 2025  
**Version**: 3.0.0
