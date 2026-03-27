# Froth Flotation Digital Twin Research Project

## Project Overview

A comprehensive digital twin system for froth flotation processes, featuring real-time ML predictions, dynamic optimization, and an interactive dashboard. Built with SOLID principles and modern software architecture.

## Architecture
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                           │
├─────────────────────────────────────────────────────────────┤
│  React TypeScript Dashboard (Port 3000)                    │
│  ├── FuturePredictionChart.tsx                             │
│  ├── PredictiveRecommendations.tsx                         │
│  ├── PredictionCards.tsx                                   │
│  └── Real-time WebSocket connections                       │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    API LAYER                                │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Backend (Port 8000)                               │
│  ├── /api/predict-future (NEW)                             │
│  ├── /api/current-data                                     │
│  ├── /api/optimization                                     │
│  └── WebSocket /ws endpoint                                │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                  SERVICE LAYER                              │
├─────────────────────────────────────────────────────────────┤
│  SOLID Architecture Services                                │
│  ├── FuturePredictionService (NEW)                         │
│  ├── MLModelService                                         │
│  ├── ServiceOrchestrator                                    │
│  ├── OptimizationService                                    │
│  └── AuthenticationService (Port 8051)                     │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   MODEL LAYER                               │
├─────────────────────────────────────────────────────────────┤
│  Trained ML Models                                          │
│  ├── 5min_efficient/rf_model.pkl (R²=0.9083)              │
│  ├── 15min_efficient/rf_model.pkl (R²=0.9041)             │
│  ├── 30min_efficient/xgb_model.pkl (R²=0.9035)            │
│  └── 60min_efficient/xgb_model.pkl (R²=0.9011)            │
└─────────────────────────────────────────────────────────────┘

### System Components

```
├── backend/
│   ├── services/           # Core business logic (SOLID architecture)
│   │   ├── interfaces.py   # Abstract interfaces
│   │   ├── data_generator.py
│   │   ├── ml_model_service.py
│   │   ├── optimization_service.py
│   │   ├── service_orchestrator.py
│   │   ├── future_prediction_service.py    # Future predictions
│   │   ├── authentication_service.py       # User authentication
│   │   ├── shared_logging.py               # Centralized logging
│   │   └── websocket_manager.py            # Real-time communication
│   ├── models/            # Database models
│   │   └── database_manager.py             # SQLite database operations
│   ├── trained_models/    # ML model artifacts
│   │   ├── 5min_efficient/                 # 5-minute prediction models
│   │   ├── 15min_efficient/                # 15-minute prediction models
│   │   ├── 30min_efficient/                # 30-minute prediction models
│   │   └── 60min_efficient/                # 60-minute prediction models
│   └── tests/            # Comprehensive test suites
│       └── test_backend_services.py        # Backend service tests
├── frontend/              # React TypeScript dashboard
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── Dashboard.tsx               # Main dashboard
│   │   │   ├── Login.tsx                   # Authentication
│   │   │   ├── FuturePredictionChart.tsx   # Time-series predictions
│   │   │   ├── PredictiveRecommendations.tsx # AI recommendations
│   │   │   ├── PredictionCards.tsx         # Multi-horizon display
│   │   │   ├── HistoricalAnalysis.tsx      # Historical data analysis
│   │   │   ├── ControlPanel.tsx            # Process controls
│   │   │   └── RealTimeGraph.tsx           # Real-time monitoring
│   │   ├── services/      # API services
│   │   ├── hooks/         # Custom React hooks
│   │   ├── contexts/      # React contexts
│   │   └── types/         # TypeScript type definitions
├── training/              # ML model training scripts
│   ├── train_5min_efficient.py            # 5-minute model training
│   ├── train_15min_efficient.py           # 15-minute model training
│   ├── train_30min_efficient.py           # 30-minute model training
│   ├── train_60min_efficient.py           # 60-minute model training
│   └── training_pipeline_optimized.py     # Optimized training pipeline
├── docs/                  # Documentation & user guides
│   ├── user_guide_predictions.md          # Future prediction user guide
│   ├── model_training_guide.md            # Model training documentation
│   └── deployment_guide.md                # Deployment instructions
├── cleaning/              # Data cleaning and preprocessing
│   ├── enhanced_data_cleaning.py          # Data cleaning pipeline
│   └── data_cleaning_documentation.md     # Cleaning documentation
└── analysis_visualizations/ # Model performance visualizations
    ├── 5min_efficient_model_performance.png
    ├── 15min_efficient_model_performance.png
    ├── 30min_efficient_model_performance.png
    └── 60min_efficient_model_performance.png
```

## Default Login (Development)

The application initializes a default admin account on first run:

- Username: `admin`
- Password: `admin123`

Use this only for local development and change credentials for shared/deployed environments.