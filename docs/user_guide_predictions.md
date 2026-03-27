# Future Prediction User Guide

## Overview

The Future Prediction System provides advanced time-series forecasting capabilities for the froth flotation process, enabling operators to see what will happen 5 minutes and 60 minutes ahead. This guide explains how to use these predictive features effectively.

## Key Features

- **Multi-Horizon Predictions**: See predictions for 5 minutes and 60 minutes ahead
- **Confidence Intervals**: Understand prediction uncertainty with ±2σ bounds
- **Interactive Charts**: Visualize current vs. predicted values over time
- **Predictive Recommendations**: Get AI-powered suggestions for process optimization
- **Scenario Analysis**: Explore "what-if" scenarios before making changes
- **Proactive Alerts**: Receive warnings before problems occur

## Getting Started

### 1. Accessing Future Predictions

The future prediction features are integrated into the main dashboard. After logging in, you'll see:

- **Prediction Cards**: Show current and future values side-by-side
- **Future Prediction Chart**: Interactive time-series visualization
- **Predictive Recommendations**: AI-generated optimization suggestions

### 2. Understanding the Interface

#### Prediction Cards
- **Current Value**: Real-time Pb concentrate grade
- **5-min Prediction**: Expected value in 5 minutes
- **60-min Prediction**: Expected value in 60 minutes
- **Confidence**: Color-coded confidence levels (Green: High, Yellow: Medium, Red: Low)
- **Trend Indicators**: Improving, Declining, Stable

#### Future Prediction Chart
- **Time Horizons**: Toggle between 5-min and 60-min predictions
- **Confidence Bands**: Shaded areas showing prediction uncertainty
- **Interactive Controls**: Zoom, pan, and explore historical data
- **Auto-refresh**: Real-time updates every 4 seconds

## Using Prediction Features

### Multi-Horizon Analysis

1. **Short-term (5 minutes)**:
   - Use for immediate operational decisions
   - React to rapid process changes
   - Fine-tune reagent dosing

2. **Medium-term (60 minutes)**:
   - Plan ahead for process optimization
   - Prepare for feed grade changes
   - Strategic parameter adjustments

### Confidence Interpretation

- **High Confidence (Green)**: Predictions are reliable, act on recommendations
- **Medium Confidence (Yellow)**: Proceed with caution, monitor closely
- **Low Confidence (Red)**: High uncertainty, consider manual oversight

### Example Workflow

```
1. Monitor current Pb concentrate: 12.5%
2. Check 5-min prediction: 11.8% (declining trend)
3. Review recommendation: "Increase KEX flow by 5 L/min"
4. Use scenario analysis to verify impact
5. Apply changes and monitor results
```

## Scenario Analysis

### What-If Modeling

1. **Access Scenario Analysis**:
   - Click "Scenario Analysis" in the recommendations panel
   - Choose from predefined scenarios or create custom ones

2. **Available Scenarios**:
   - **Increase KEX**: +10% collector reagent
   - **Decrease SIPX**: -15% frother reagent
   - **Higher Feed Grade**: +20% feed Pb content
   - **Custom Scenario**: Define your own parameter changes

3. **Interpreting Results**:
   - **Risk Score**: Lower is better (0-1 scale)
   - **Benefit Score**: Higher is better (0-1 scale)
   - **Confidence**: Prediction reliability
   - **Recommendation**: Overall assessment

### Example Scenario Analysis

```
Scenario: "Increase KEX by 10%"
┌─────────────────────────────────────────────┐
│ 5-min Impact:  +0.8% Pb concentrate        │
│ 60-min Impact: +1.2% Pb concentrate        │
│ Risk Score: 0.15 (Low risk)                │
│ Benefit Score: 0.85 (High benefit)         │
│ Recommendation: ✅ Proceed with changes     │
└─────────────────────────────────────────────┘
```

## 🚨 Proactive Alerts

### Alert Types

1. **Performance Alerts**:
   - Low concentrate predictions
   - Declining trend warnings
   - Process instability indicators

2. **Operational Alerts**:
   - Reagent optimization opportunities
   - Feed grade adaptation needs
   - Equipment performance issues

3. **Prediction Quality Alerts**:
   - Low confidence predictions
   - Model drift detection
   - Validation accuracy drops

### Responding to Alerts

1. **Immediate Actions**:
   - Review alert details and severity
   - Check recommended preventive actions
   - Verify current process conditions

2. **Preventive Measures**:
   - Apply suggested parameter changes
   - Monitor results in real-time
   - Document actions for future reference

## 🛠️ Optimization Workflow

### 1. Multi-Horizon Optimization

The system automatically finds optimal settings considering both 5-minute and 60-minute predictions:

```
Current Settings:
- KEX Flow: 45 L/min
- SIPX Flow: 25 L/min

Optimized Settings:
- KEX Flow: 52 L/min (+7)
- SIPX Flow: 28 L/min (+3)

Expected Improvement:
- 5-min: +0.6% Pb concentrate
- 60-min: +1.1% Pb concentrate
```

### 2. Applying Optimizations

1. **Review Recommendations**: Check the optimization score and confidence
2. **Validate with Scenarios**: Use scenario analysis to verify expected outcomes
3. **Apply Changes Gradually**: Implement changes in steps to minimize risk
4. **Monitor Results**: Track actual vs. predicted performance

## 📈 Performance Monitoring

### Prediction Accuracy

The system continuously validates predictions against actual outcomes:

- **Accuracy Metrics**: R², MAE, RMSE for each time horizon
- **Drift Detection**: Alerts when model performance degrades
- **Confidence Scoring**: Real-time assessment of prediction reliability

### Model Performance Dashboard

Access detailed performance metrics:
- **Historical Accuracy**: Trends over time
- **Horizon Comparison**: 5-min vs 60-min performance
- **Confidence Distribution**: Reliability statistics
- **Validation Reports**: Detailed accuracy analysis

## 🔧 Troubleshooting

### Common Issues

1. **Low Prediction Confidence**:
   - **Cause**: Unusual process conditions or data quality issues
   - **Solution**: Check input data quality, consider manual oversight
   - **Prevention**: Regular model retraining and validation

2. **Inconsistent Predictions**:
   - **Cause**: Rapid process changes or sensor malfunctions
   - **Solution**: Verify sensor readings, check for data anomalies
   - **Prevention**: Implement data quality monitoring

3. **Poor Prediction Accuracy**:
   - **Cause**: Model drift or changing process dynamics
   - **Solution**: Review recent validation reports, consider model retraining
   - **Prevention**: Regular performance monitoring and maintenance

### Getting Help

1. **Check System Status**: Review prediction service health in the status panel
2. **Validation Reports**: Examine recent accuracy metrics
3. **Contact Support**: Use the built-in feedback system for technical issues

## 🎓 Best Practices

### Operational Guidelines

1. **Trust but Verify**: Use predictions as guidance, not absolute truth
2. **Consider Confidence**: Always check prediction confidence before acting
3. **Monitor Results**: Track actual outcomes vs. predictions
4. **Document Decisions**: Keep records of prediction-based actions

### Process Optimization

1. **Use Multiple Horizons**: Consider both 5-min and 60-min predictions
2. **Scenario Testing**: Always test changes with scenario analysis first
3. **Gradual Implementation**: Apply large changes in steps
4. **Continuous Learning**: Review prediction accuracy regularly

### Data Quality

1. **Sensor Maintenance**: Ensure accurate input data
2. **Regular Calibration**: Maintain measurement accuracy
3. **Data Validation**: Check for anomalies and outliers
4. **Feedback Loop**: Report prediction accuracy issues

## 📊 API Usage (Advanced)

### Programmatic Access

For advanced users, predictions can be accessed via API:

```python
import requests

# Get future predictions
response = requests.get('http://localhost:8000/api/future-predictions')
predictions = response.json()

print(f"5-min prediction: {predictions['future_predictions']['5min']['prediction']}")
print(f"60-min prediction: {predictions['future_predictions']['60min']['prediction']}")
```

### Available Endpoints

- `GET /api/future-predictions` - Get all future predictions
- `GET /api/prediction-info` - Model performance and status
- `POST /api/scenario-analysis` - Run what-if scenarios
- `GET /api/predictive-alerts` - Get current alerts and recommendations

## 📞 Support

For technical support or questions about the prediction system:

1. **System Status**: Check the dashboard status indicators
2. **Documentation**: Refer to this guide and the API documentation
3. **Validation Reports**: Review prediction accuracy metrics
4. **Contact Team**: Use the support channels for complex issues

---

**Last Updated**: December 2024  
**Version**: 4.0.0  
**System Status**: ✅ Production Ready
