# Model Training & Validation Guide 📈

## Overview

This guide covers the complete model training and validation process for the froth flotation prediction system. It includes procedures for training new models, validating performance, and maintaining prediction accuracy over time.

## 🎯 Model Architecture

### Current Models

The system uses **Random Forest Regressors** optimized for time-series prediction:

- **5-minute horizon model**: Predicts Pb concentrate 5 minutes ahead
- **60-minute horizon model**: Predicts Pb concentrate 60 minutes ahead

### Model Specifications

```python
Random Forest Configuration:
- Estimators: 100 trees
- Max Depth: 15
- Min Samples Split: 5
- Min Samples Leaf: 2
- Random State: 42
- Feature Count: 200 (including lag features)
```

### Performance Targets

| Horizon | R² Score | RMSE | MAE | Accuracy (±10%) |
|---------|----------|------|-----|-----------------|
| 5-min   | ≥ 0.90   | ≤ 2.0% | ≤ 1.5% | ≥ 85% |
| 60-min  | ≥ 0.85   | ≤ 2.5% | ≤ 2.0% | ≥ 80% |

## 📊 Data Preparation

### Feature Engineering

The training process creates 200 features from the base process variables:

#### Core Features (6)
- `Feed_Pb`: Feed lead grade
- `Feed_Zn`: Feed zinc grade  
- `Pb_Conditioner_KEX_Flowrate`: Collector reagent flow
- `Pb_Rougher1_SIPX_Flowrate`: Frother reagent flow
- `Pb_Rougher1_AirFlow`: Air flow rate
- `Pb_Rougher1_Level`: Cell level

#### Lag Features (12)
- 5, 15, 30, 60-minute lags for: `Feed_Pb`, `KEX_Flowrate`, `SIPX_Flowrate`

#### Engineered Features (182)
- Rolling statistics (mean, std, min, max)
- Ratios and interactions
- Polynomial features
- Time-based features
- Trend indicators

### Target Variables

Future target variables are created by shifting the `Pb_Rougher_Conc_Pb` column:

```python
# Create future targets
data['5min_ahead'] = data['Pb_Rougher_Conc_Pb'].shift(-1)  # 5-min future
data['60min_ahead'] = data['Pb_Rougher_Conc_Pb'].shift(-12)  # 60-min future
```

### Data Quality Requirements

1. **Completeness**: ≥ 95% data availability
2. **Consistency**: No gaps > 30 minutes
3. **Range Validation**: All values within expected process ranges
4. **Outlier Detection**: Remove values > 3σ from mean

## 🚀 Training Process

### 1. Environment Setup

```bash
# Install dependencies
pip install scikit-learn pandas numpy joblib

# Verify GPU availability (optional for acceleration)
python -c "import joblib; print(f'CPU cores: {joblib.cpu_count()}')"
```

### 2. Data Loading and Preparation

```python
import pandas as pd
import numpy as np
from pathlib import Path

# Load cleaned data
data_path = Path('data/cleaned_flotation_data.parquet')
df = pd.read_parquet(data_path)

print(f"Loaded {len(df)} rows of data")
print(f"Date range: {df.index.min()} to {df.index.max()}")
```

### 3. Training Configuration

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# Model configuration
model_config = {
    'n_estimators': 100,
    'max_depth': 15,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'random_state': 42,
    'n_jobs': -1  # Use all CPU cores
}

# Training configuration
training_config = {
    'test_size': 0.2,
    'validation_splits': 5,
    'sample_size': 50000,  # For faster training
    'feature_count': 200
}
```

### 4. Model Training

```python
def train_horizon_model(X, y, horizon_name, config):
    """Train a model for a specific time horizon."""
    
    # Time series split for validation
    tscv = TimeSeriesSplit(n_splits=config['validation_splits'])
    
    # Initialize model
    model = RandomForestRegressor(**model_config)
    
    # Train-test split
    split_idx = int(len(X) * (1 - config['test_size']))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Train model
    print(f"Training {horizon_name} model...")
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    metrics = {
        'r2_score': r2_score(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
        'mae': mean_absolute_error(y_test, y_pred),
        'accuracy_10pct': np.mean(np.abs(y_test - y_pred) <= 0.1 * np.abs(y_test))
    }
    
    return model, metrics

# Train models for each horizon
models = {}
metadata = {}

for horizon in [5, 60]:
    horizon_key = f'{horizon}min'
    target_col = f'{horizon}min_ahead'
    
    if target_col in df.columns:
        # Prepare data
        X = df[feature_columns].fillna(0)
        y = df[target_col].fillna(df[target_col].mean())
        
        # Train model
        model, metrics = train_horizon_model(X, y, horizon_key, training_config)
        
        # Store results
        models[horizon_key] = {'rf': model}
        metadata['rf'] = metrics
        
        print(f"{horizon_key} Model Performance:")
        print(f"  R² Score: {metrics['r2_score']:.4f}")
        print(f"  RMSE: {metrics['rmse']:.4f}")
        print(f"  MAE: {metrics['mae']:.4f}")
        print(f"  Accuracy (±10%): {metrics['accuracy_10pct']:.4f}")
```

### 5. Model Saving

```python
import joblib
from pathlib import Path

# Create model directories
models_dir = Path('backend/trained_models')
models_dir.mkdir(exist_ok=True)

# Save models
for horizon_key, horizon_models in models.items():
    horizon_dir = models_dir / horizon_key
    horizon_dir.mkdir(exist_ok=True)
    
    # Save Random Forest model
    model_path = horizon_dir / 'rf_model.pkl'
    joblib.dump(horizon_models['rf'], model_path)
    print(f"Saved {horizon_key} model to {model_path}")

# Save metadata
metadata_path = models_dir / 'model_metadata.pkl'
joblib.dump(metadata, metadata_path)
print(f"Saved metadata to {metadata_path}")

# Create training summary
summary_path = models_dir / 'training_summary.txt'
with open(summary_path, 'w') as f:
    f.write("Random Forest Model Training Summary\n")
    f.write("===================================\n\n")
    f.write(f"Training Date: {pd.Timestamp.now()}\n")
    f.write(f"Model Type: Random Forest\n")
    f.write(f"Feature Count: {training_config['feature_count']}\n")
    f.write(f"Sample Size: {training_config['sample_size']}\n\n")
    
    for horizon in [5, 60]:
        horizon_key = f'{horizon}min'
        if horizon_key in models:
            f.write(f"{horizon_key} Model Performance:\n")
            f.write(f"  R² Score: {metadata['rf']['r2_score']:.4f}\n")
            f.write(f"  RMSE: {metadata['rf']['rmse']:.4f}\n")
            f.write(f"  MAE: {metadata['rf']['mae']:.4f}\n")
            f.write(f"  Accuracy (±10%): {metadata['rf']['accuracy_10pct']:.4f}\n\n")
```

## ✅ Validation Framework

### Real-time Validation

The system continuously validates predictions against actual outcomes:

```python
class PredictionValidator:
    """Validates prediction accuracy in real-time."""
    
    def __init__(self):
        self.validation_history = []
        self.accuracy_thresholds = {
            '5min': {'r2': 0.90, 'rmse': 2.0, 'mae': 1.5},
            '60min': {'r2': 0.85, 'rmse': 2.5, 'mae': 2.0}
        }
    
    def validate_prediction(self, actual_value, predicted_value, horizon):
        """Validate a single prediction."""
        error = abs(actual_value - predicted_value)
        percentage_error = error / abs(actual_value) if actual_value != 0 else 0
        
        validation_result = {
            'timestamp': pd.Timestamp.now(),
            'horizon': horizon,
            'actual': actual_value,
            'predicted': predicted_value,
            'absolute_error': error,
            'percentage_error': percentage_error,
            'within_10_percent': percentage_error <= 0.1
        }
        
        self.validation_history.append(validation_result)
        return validation_result
```

### Drift Detection

Monitor model performance over time to detect when retraining is needed:

```python
def detect_model_drift(validation_history, window_size=100, threshold=0.15):
    """Detect if model performance has degraded."""
    
    if len(validation_history) < window_size:
        return False, "Insufficient data for drift detection"
    
    # Calculate recent vs. historical performance
    recent_errors = [v['percentage_error'] for v in validation_history[-window_size:]]
    historical_errors = [v['percentage_error'] for v in validation_history[:-window_size]]
    
    recent_mean = np.mean(recent_errors)
    historical_mean = np.mean(historical_errors)
    
    # Check for significant increase in error
    drift_ratio = recent_mean / historical_mean if historical_mean > 0 else 0
    drift_detected = drift_ratio > (1 + threshold)
    
    return drift_detected, f"Recent error: {recent_mean:.3f}, Historical: {historical_mean:.3f}"
```

### Performance Monitoring

```python
def generate_performance_report(validation_history, horizon):
    """Generate comprehensive performance metrics."""
    
    horizon_data = [v for v in validation_history if v['horizon'] == horizon]
    
    if not horizon_data:
        return {"error": "No validation data available"}
    
    errors = [v['percentage_error'] for v in horizon_data]
    absolute_errors = [v['absolute_error'] for v in horizon_data]
    within_threshold = [v['within_10_percent'] for v in horizon_data]
    
    report = {
        'horizon': horizon,
        'total_predictions': len(horizon_data),
        'mean_percentage_error': np.mean(errors),
        'mean_absolute_error': np.mean(absolute_errors),
        'rmse': np.sqrt(np.mean([e**2 for e in absolute_errors])),
        'accuracy_within_10pct': np.mean(within_threshold),
        'latest_error': errors[-1] if errors else None,
        'performance_trend': 'improving' if len(errors) > 10 and np.mean(errors[-10:]) < np.mean(errors[-20:-10]) else 'stable'
    }
    
    return report
```

## 🔄 Retraining Guidelines

### When to Retrain

Retrain models when:

1. **Performance Degradation**: Accuracy drops below thresholds
2. **Drift Detection**: Statistical drift in prediction patterns
3. **Process Changes**: Significant modifications to the flotation process
4. **Data Quality Issues**: Systematic errors in input data
5. **Scheduled Maintenance**: Regular retraining (monthly/quarterly)

### Retraining Process

1. **Data Collection**: Gather recent process data (≥ 30 days)
2. **Quality Assessment**: Validate data completeness and accuracy
3. **Feature Engineering**: Update feature calculations if needed
4. **Model Training**: Train new models with updated data
5. **Validation**: Compare new vs. old model performance
6. **Deployment**: Replace old models if improvement is significant

### Performance Comparison

```python
def compare_model_performance(old_metrics, new_metrics):
    """Compare old vs. new model performance."""
    
    improvement_threshold = 0.05  # 5% minimum improvement
    
    comparison = {}
    for metric in ['r2_score', 'rmse', 'mae']:
        old_value = old_metrics.get(metric, 0)
        new_value = new_metrics.get(metric, 0)
        
        if metric == 'r2_score':
            improvement = new_value - old_value
        else:
            improvement = old_value - new_value  # Lower is better for error metrics
        
        comparison[metric] = {
            'old': old_value,
            'new': new_value,
            'improvement': improvement,
            'significant': abs(improvement) > improvement_threshold
        }
    
    return comparison
```

## 📊 Model Deployment

### Deployment Checklist

- [ ] **Performance Validation**: New models meet accuracy thresholds
- [ ] **A/B Testing**: Compare new vs. old models in production
- [ ] **Backup Creation**: Save current models before replacement
- [ ] **Service Restart**: Restart prediction services to load new models
- [ ] **Monitoring Setup**: Ensure validation framework is active
- [ ] **Documentation Update**: Record model changes and performance

### Deployment Script

```python
def deploy_new_models(new_models_dir, production_dir, backup_dir):
    """Deploy new models to production with backup."""
    
    # Create backup of current models
    backup_timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f'backup_{backup_timestamp}'
    backup_path.mkdir(exist_ok=True)
    
    # Backup current models
    for model_file in production_dir.glob('**/*.pkl'):
        backup_file = backup_path / model_file.relative_to(production_dir)
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        backup_file.write_bytes(model_file.read_bytes())
    
    # Deploy new models
    for model_file in new_models_dir.glob('**/*.pkl'):
        production_file = production_dir / model_file.relative_to(new_models_dir)
        production_file.parent.mkdir(parents=True, exist_ok=True)
        production_file.write_bytes(model_file.read_bytes())
    
    print(f"Models deployed successfully. Backup created at {backup_path}")
    
    # Restart prediction services (implementation specific)
    restart_prediction_services()
```

## 🛠️ Troubleshooting

### Common Training Issues

1. **Memory Errors**:
   - Reduce sample size
   - Use data chunking
   - Increase available RAM

2. **Poor Performance**:
   - Check data quality
   - Adjust hyperparameters
   - Increase training data

3. **Overfitting**:
   - Reduce model complexity
   - Add regularization
   - Increase validation splits

### Performance Monitoring

```python
# Monitor training progress
import matplotlib.pyplot as plt

def plot_training_performance(metrics_history):
    """Plot model performance over training iterations."""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # R² Score
    axes[0,0].plot(metrics_history['r2_score'])
    axes[0,0].set_title('R² Score')
    axes[0,0].set_ylabel('R²')
    
    # RMSE
    axes[0,1].plot(metrics_history['rmse'])
    axes[0,1].set_title('RMSE')
    axes[0,1].set_ylabel('RMSE')
    
    # MAE
    axes[1,0].plot(metrics_history['mae'])
    axes[1,0].set_title('MAE')
    axes[1,0].set_ylabel('MAE')
    
    # Accuracy
    axes[1,1].plot(metrics_history['accuracy'])
    axes[1,1].set_title('Accuracy (±10%)')
    axes[1,1].set_ylabel('Accuracy')
    
    plt.tight_layout()
    plt.savefig('training_performance.png')
    plt.show()
```

## 📈 Best Practices

### Training Guidelines

1. **Data Quality First**: Ensure high-quality, clean training data
2. **Feature Engineering**: Invest time in creating meaningful features
3. **Cross-Validation**: Use time-series aware validation techniques
4. **Hyperparameter Tuning**: Optimize model parameters systematically
5. **Regular Retraining**: Maintain model freshness with new data

### Production Monitoring

1. **Continuous Validation**: Track prediction accuracy in real-time
2. **Drift Detection**: Monitor for performance degradation
3. **Alerting**: Set up alerts for accuracy threshold breaches
4. **Documentation**: Keep detailed records of model changes
5. **Backup Strategy**: Maintain model versioning and backups

### Performance Optimization

1. **Parallel Training**: Use multiple CPU cores
2. **Memory Management**: Optimize data loading and processing
3. **Model Compression**: Reduce model size for faster loading
4. **Caching**: Cache frequently used predictions
5. **Load Balancing**: Distribute prediction requests

---

**Last Updated**: December 2024  
**Version**: 4.0.0  
**Training Status**: ✅ Models Trained and Validated
