# Flotation Grade Prediction - Modeling Framework

This project implements a comprehensive modeling framework for predicting Pb grade in rougher concentrate using three different approaches: Linear Regression, Random Forest, and XGBoost. The best performing model is then integrated into a digital twin for real-time process monitoring.

## 🎯 Project Overview

**Target Variable**: `Pb_Rougher_Conc_Pb` (Lead grade in rougher concentrate)

**Models Implemented**:
1. **Linear Regression** - Baseline linear model for comparison
2. **Random Forest** - Non-linear ensemble model with feature importance
3. **XGBoost** - Advanced gradient boosting model with lagged features (expected to be the best performer)

## 📁 Project Structure

```
TUT Research Project/
├── Clean_Data/
│   └── HZL_RA4_Pb_Rougher_2025-07_clean.parquet  # Cleaned data from Part 1
├── Models/                                        # Trained models (created after training)
│   ├── linear_regression_model.pkl
│   ├── linear_regression_scaler.pkl
│   ├── random_forest_model.pkl
│   ├── xgboost_model.pkl
│   ├── xgboost_scaler.pkl
│   └── model_info.pkl
├── flotation_models.py                           # Main modeling framework
├── digital_twin_integration.py                   # Digital twin integration
├── Run_Modeling_Pipeline.ipynb                   # Complete pipeline execution
├── modeling_requirements.txt                     # Dependencies
└── README.md                                     # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r modeling_requirements.txt
```

### 2. Run the Complete Pipeline

```python
# Option 1: Run the notebook
# Open Run_Modeling_Pipeline.ipynb and execute all cells

# Option 2: Run the Python script directly
python flotation_models.py
```

### 3. Test Digital Twin Integration

```python
from digital_twin_integration import FlotationDigitalTwin

# Initialize digital twin
digital_twin = FlotationDigitalTwin()

# Make predictions
prediction = digital_twin.predict_single(your_data)
print(f"Predicted Pb Grade: {prediction:.4f}%")
```

## 📊 Model Details

### Linear Regression
- **Purpose**: Baseline linear model for comparison
- **Features**: Standardized using StandardScaler
- **Advantages**: Interpretable, fast, good baseline
- **Use Case**: When linear relationships dominate

### Random Forest
- **Purpose**: Non-linear ensemble model
- **Features**: No scaling required, handles non-linearities
- **Advantages**: Feature importance, robust to outliers
- **Use Case**: When complex non-linear relationships exist

### XGBoost (eXtreme Gradient Boosting)
- **Purpose**: Advanced gradient boosting model with time series features
- **Features**: Lagged features (3 time steps) + original features
- **Architecture**: Gradient boosting with early stopping and regularization
- **Advantages**: Fast training, excellent performance, feature importance, interpretable
- **Expected Performance**: Highest accuracy due to advanced boosting and temporal features

## 🤖 Digital Twin Features

The `FlotationDigitalTwin` class provides:

### Core Prediction Functions
- `predict_single()` - Single prediction
- `predict_batch()` - Batch predictions
- `predict_with_confidence()` - Predictions with confidence intervals

### Advanced Features
- **Process Monitoring**: Real-time anomaly detection
- **Feature Importance**: Understanding key process variables
- **Process Simulation**: Testing different operating conditions
- **Comprehensive Reporting**: Detailed analysis and statistics

### Example Usage

```python
# Initialize digital twin
digital_twin = FlotationDigitalTwin()

# Real-time monitoring
result = digital_twin.monitor_process(real_time_data)
print(f"Predicted Grade: {result['predicted_grade']:.4f}%")
print(f"Anomaly Detected: {result['is_anomaly']}")

# Process simulation
variations = {
    'Feed_Pb': [1.0, 1.5, 2.0, 2.5],
    'Pb_Rougher1_AirFlow': [100, 120, 140, 160]
}
simulation = digital_twin.simulate_process_conditions(base_data, variations)

# Generate report
report = digital_twin.generate_report(data, 'report.json')
```

## 📈 Model Performance Metrics

The framework evaluates models using:
- **MSE** (Mean Squared Error) - Overall prediction accuracy
- **MAE** (Mean Absolute Error) - Average absolute deviation
- **RMSE** (Root Mean Squared Error) - Standard deviation of residuals
- **R²** (Coefficient of Determination) - Proportion of variance explained

## 🔧 Configuration

### Model Parameters

**Linear Regression**:
- Standard scaling
- No hyperparameters to tune

**Random Forest**:
- n_estimators: 100
- max_depth: 10
- min_samples_split: 5
- min_samples_leaf: 2

**XGBoost**:
- Lag steps: 3 (previous time steps)
- n_estimators: 200
- max_depth: 6
- learning_rate: 0.1
- subsample: 0.8
- colsample_bytree: 0.8
- Early stopping rounds: 20

### Data Splitting
- **Train**: 60% of data (chronological)
- **Validation**: 20% of data
- **Test**: 20% of data (most recent)

## 🎯 Expected Results

Based on the nature of flotation processes and time series characteristics:

1. **XGBoost** should perform best due to:
   - Advanced gradient boosting algorithm
   - Lagged features capturing temporal dependencies
   - Excellent handling of non-linear relationships
   - Robust regularization and early stopping

2. **Random Forest** should be second best due to:
   - Ability to capture non-linear relationships
   - Robust feature importance analysis

3. **Linear Regression** should be the baseline due to:
   - Limited ability to capture complex relationships
   - Good for comparison and interpretability

## 🚀 Integration with Flotation Digital Twin

The trained model integrates seamlessly with flotation digital twin systems:

### Real-time Monitoring
- Continuous grade prediction
- Anomaly detection
- Process optimization recommendations

### Process Control
- Predictive control strategies
- Setpoint optimization
- Feed-forward control

### Decision Support
- Grade forecasting
- Process troubleshooting
- Performance optimization

## 🔄 Model Maintenance

### Retraining Strategy
- **Frequency**: Monthly or when performance degrades
- **Trigger**: R² drops below threshold or new data available
- **Method**: Incremental learning or full retraining

### Performance Monitoring
- Track prediction accuracy over time
- Monitor for concept drift
- Alert when model performance degrades

## 📋 Next Steps

1. **Deploy to Production**:
   - Set up real-time data streaming
   - Implement automated model serving
   - Create monitoring dashboards

2. **Advanced Features**:
   - Multi-step ahead forecasting
   - Uncertainty quantification
   - Ensemble methods

3. **Integration**:
   - Connect to SCADA systems
   - Implement control strategies
   - Create operator interfaces

## 🛠️ Troubleshooting

### Common Issues

1. **Memory Issues with XGBoost**:
   - Reduce n_estimators
   - Use smaller max_depth
   - Implement early stopping

2. **Poor Performance**:
   - Check data quality
   - Verify feature engineering
   - Adjust model parameters

3. **Digital Twin Loading Errors**:
   - Ensure model files exist
   - Check file paths
   - Verify XGBoost version compatibility

### Performance Optimization

1. **For XGBoost**:
   - Use parallel processing (n_jobs=-1)
   - Optimize hyperparameters
   - Implement early stopping

2. **For Production**:
   - Use model serving frameworks
   - Implement caching
   - Optimize inference speed

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Review the code comments
3. Examine the example usage in the notebook

---

**🎉 Congratulations! Your flotation digital twin is ready for deployment! 🎉**
