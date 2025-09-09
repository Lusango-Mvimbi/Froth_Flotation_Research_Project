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
│   │   ├── dynamic_ranges_service.py
│   │   ├── future_prediction_service.py    # 🔮 Future predictions
│   │   ├── scenario_analyzer.py            # 🎯 What-if analysis
│   │   ├── predictive_alerts.py            # 🚨 Proactive alerts
│   │   └── prediction_validator.py         # ✅ Validation framework
│   ├── models/            # Database models
│   ├── trained_models/    # ML model artifacts (Random Forest)
│   └── tests/            # Comprehensive test suites
├── frontend/              # React TypeScript dashboard
│   ├── src/components/
│   │   ├── FuturePredictionChart.tsx      # 📈 Time-series predictions
│   │   ├── PredictiveRecommendations.tsx  # 💡 AI recommendations
│   │   └── PredictionCards.tsx            # 📊 Multi-horizon display
└── docs/                 # Documentation & user guides
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

### Phase 4: Future Prediction System ✅
- [x] **Time-series ML models** for 5-minute and 60-minute predictions
- [x] **Multi-horizon optimization** with confidence intervals
- [x] **Predictive alerts** and proactive control recommendations
- [x] **Scenario analysis** and "what-if" modeling capabilities
- [x] **Real-time prediction validation** and drift detection

### Phase 5: Advanced Analytics ✅
- [x] **Future prediction charts** with interactive time horizons
- [x] **Predictive recommendations** for process optimization
- [x] **Risk assessment** and preventive action suggestions
- [x] **Performance monitoring** and accuracy tracking

### Phase 6: Testing & Validation ✅
- [x] **Comprehensive test suite** (45 tests, 100% pass rate)
- [x] **User acceptance testing** for production readiness
- [x] **Performance benchmarking** (594.9 predictions/second)
- [x] **Prediction validation framework** with drift detection

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

### Current Prediction Model
- **Model Type**: Random Forest Regressor
- **R² Score**: 0.973 (97.3% accuracy)
- **RMSE**: 1.23%
- **MAE**: 0.77%
- **Features**: 200 (including lag features)

### Future Prediction Models 🔮
- **Time Horizons**: 5 minutes, 60 minutes
- **Model Type**: Random Forest (optimized for time-series)
- **Performance Metrics**:
  - **5-minute predictions**: R² = 0.95, RMSE = 1.8%
  - **60-minute predictions**: R² = 0.89, RMSE = 2.4%
- **Prediction Speed**: 594.9 predictions/second
- **Confidence Intervals**: ±2σ based on model RMSE
- **Validation**: Real-time accuracy tracking with drift detection

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

### Future Prediction Endpoints 🔮
- `GET /api/future-predictions` - Multi-horizon future predictions
- `GET /api/prediction-info` - Model performance and status
- `POST /api/validate-prediction` - Validate prediction accuracy
- `GET /api/prediction-analytics` - Prediction analytics and drift detection

### Advanced Analytics Endpoints 🎯
- `POST /api/scenario-analysis` - What-if scenario analysis
- `GET /api/predictive-alerts` - Proactive alerts and recommendations
- `POST /api/multi-horizon-optimization` - Multi-horizon optimization

### WebSocket
- `ws://localhost:8000/ws` - Real-time data streaming

## 🧪 Testing

### Comprehensive Test Suite ✅
- **Unit Tests**: 29 tests covering all prediction components
- **Integration Tests**: End-to-end prediction flow validation
- **Performance Tests**: Speed, memory, and concurrency testing
- **User Acceptance Tests**: 16 tests for production readiness

```bash
# Run future prediction tests
python tests/test_future_prediction.py

# Run user acceptance tests
python tests/user_acceptance_tests.py

# Run backend tests
cd backend/tests
python -m pytest

# Run frontend tests
cd frontend
npm test
```

### Test Results 🎯
- **Pass Rate**: 100% (45/45 tests)
- **Performance**: 594.9 predictions/second
- **Memory Usage**: <100MB under load
- **Concurrent Predictions**: 5 threads successfully handled

## 📚 Documentation

- [Project Summary](PROJECT_SUMMARY.md)
- [Quick Start Guide](QUICK_START.md)
- [Future Prediction User Guide](docs/user_guide_predictions.md) 🔮
- [Model Training & Validation Guide](docs/model_training_guide.md) 📈
- [API Documentation](docs/api.md)
- [Architecture Guide](docs/architecture.md)
- [Deployment Guide](docs/deployment_guide.md) 🚀

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

### Phase 7: Synchronized Updates ✅
- [x] **Backend synchronization** - Identical data for simultaneous calls
- [x] **Frontend component synchronization** - 500ms unified delay
- [x] **UI cleanup** - Single refresh button (next to logout)
- [x] **Real-time coordination** - All components update together
- [x] **Production optimization** - Perfect synchronization across system

**Status**: ✅ Production Ready with Synchronized Updates  
**Last Updated**: September 2025  
**Version**: 4.1.0 🔄
