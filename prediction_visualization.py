"""
Split Froth Flotation Prediction Visualization
=============================================

This script creates two separate visualization outputs to ensure
all information is clearly visible without crowding.

Output 1: Main Prediction Analysis (3x2 grid)
Output 2: Time-Based Analysis (2x2 grid)

Author: AI Assistant
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import joblib
import warnings
from datetime import datetime, timedelta
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('default')
sns.set_palette("husl")

class SplitPredictionVisualizer:
    """
    A class for creating split visualizations with clear, uncluttered plots.
    """
    
    def __init__(self, model_path=None, data_path=None):
        """Initialize the visualizer."""
        # Set default paths
        if model_path is None:
            model_path = "models/rf_optimized_model.pkl"
        if data_path is None:
            data_path = r"C:\@Python Projects\TUT Research Project\Clean_Data\HZL_RA4_Pb_Rougher_enhanced_clean.parquet"
        
        self.model_path = Path(model_path)
        self.data_path = Path(data_path)
        
        # Load model and data
        self.load_model()
        self.load_data()
        
    def load_model(self):
        """Load the trained model."""
        print(f"🤖 Loading model from: {self.model_path}")
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        self.model = joblib.load(self.model_path)
        print(f"✅ Model loaded: {type(self.model).__name__}")
        
        # Get feature names
        if hasattr(self.model, 'feature_names_in_'):
            self.feature_names = list(self.model.feature_names_in_)
            print(f"📊 Model uses {len(self.feature_names)} features")
        else:
            self.feature_names = None
            print("⚠️ Feature names not available")
    
    def load_data(self):
        """Load and prepare the dataset with robust error handling."""
        print(f"📊 Loading data from: {self.data_path}")
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data not found: {self.data_path}")
        
        # Load the enhanced dataset
        self.df = pd.read_parquet(self.data_path)
        print(f"✅ Data loaded: {self.df.shape}")
        
        # Prepare features and target
        target_col = 'Pb_Rougher_Conc_Pb'
        if target_col not in self.df.columns:
            raise ValueError(f"Target column '{target_col}' not found in data")
        
        # Select features
        if self.feature_names:
            # Use only the features the model was trained on
            available_features = [f for f in self.feature_names if f in self.df.columns]
            missing_features = set(self.feature_names) - set(available_features)
            
            if missing_features:
                print(f"⚠️ Missing features: {missing_features}")
                # Add missing features with zeros
                for feature in missing_features:
                    self.df[feature] = 0
            
            self.X = self.df[self.feature_names]
        else:
            # Use all numeric features except target
            self.X = self.df.drop(columns=[target_col]).select_dtypes(include=[np.number])
        
        self.y = self.df[target_col]
        
        print(f"📈 Features: {self.X.shape[1]}, Samples: {self.X.shape[0]}")
        
        # Robust data cleaning
        print("🔧 Cleaning data...")
        
        # Handle infinite values
        self.X = self.X.replace([np.inf, -np.inf], np.nan)
        self.y = self.y.replace([np.inf, -np.inf], np.nan)
        
        # Handle missing values
        if self.X.isnull().any().any():
            print("   Handling missing values in features...")
            self.X = self.X.fillna(self.X.median())
        
        if self.y.isnull().any():
            print("   Handling missing values in target...")
            self.y = self.y.fillna(self.y.median())
        
        # Remove any remaining problematic values
        valid_mask = (
            np.isfinite(self.X).all(axis=1) & 
            np.isfinite(self.y) &
            (self.y > 0)  # Ensure positive values for percentage calculations
        )
        
        self.X = self.X[valid_mask]
        self.y = self.y[valid_mask]
        
        print(f"📈 After cleaning: {self.X.shape[1]} features, {self.X.shape[0]} samples")
        
        # Create time index
        print("⏰ Creating time index...")
        self.time_index = pd.date_range(
            start='2023-01-01', 
            periods=len(self.df), 
            freq='5T'  # 5-minute intervals
        )
        
        # Adjust time index to match cleaned data
        self.time_index = self.time_index[valid_mask]
    
    def make_predictions(self):
        """Make predictions on the cleaned dataset."""
        print("🔮 Making predictions...")
        
        # Make predictions
        self.predictions = self.model.predict(self.X)
        
        # Ensure predictions are finite
        self.predictions = np.where(np.isfinite(self.predictions), self.predictions, self.y.median())
        
        # Calculate errors
        self.errors = self.y - self.predictions
        self.absolute_errors = np.abs(self.errors)
        self.percentage_errors = (self.absolute_errors / self.y) * 100
        
        # Ensure percentage errors are finite
        self.percentage_errors = np.where(np.isfinite(self.percentage_errors), self.percentage_errors, 0)
        
        # Calculate metrics
        from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
        
        self.r2 = r2_score(self.y, self.predictions)
        self.rmse = np.sqrt(mean_squared_error(self.y, self.predictions))
        self.mae = mean_absolute_error(self.y, self.predictions)
        self.within_10_percent = np.mean(self.percentage_errors <= 10)
        
        print(f"✅ Predictions completed:")
        print(f"   R² Score: {self.r2:.4f}")
        print(f"   RMSE: {self.rmse:.4f}")
        print(f"   MAE: {self.mae:.4f}")
        print(f"   Within 10%: {self.within_10_percent:.2%}")
        
        # Create results DataFrame
        self.results_df = pd.DataFrame({
            'timestamp': self.time_index,
            'actual': self.y,
            'predicted': self.predictions,
            'error': self.errors,
            'absolute_error': self.absolute_errors,
            'percentage_error': self.percentage_errors
        })
        
        return self.results_df
    
    def create_main_analysis_plot(self):
        """Create the main prediction analysis plot (3x2 grid)."""
        print("📊 Creating main prediction analysis plot...")
        
        # Create a figure with 3x2 subplots
        fig, axes = plt.subplots(3, 2, figsize=(20, 24))
        fig.suptitle('Froth Flotation Prediction Analysis - Main Results', fontsize=20, fontweight='bold')
        
        # 1. Raw Data vs Predictions (Time Series) - First 1000 points for clarity
        sample_size = min(1000, len(self.time_index))
        ax1 = axes[0, 0]
        
        # Ensure data is finite for plotting
        y_sample = self.y[:sample_size]
        pred_sample = self.predictions[:sample_size]
        time_sample = self.time_index[:sample_size]
        
        # Filter out any remaining non-finite values
        finite_mask = np.isfinite(y_sample) & np.isfinite(pred_sample)
        
        if np.sum(finite_mask) > 0:
            ax1.plot(time_sample[finite_mask], y_sample[finite_mask], 'b-', alpha=0.7, label='Actual', linewidth=1.5)
            ax1.plot(time_sample[finite_mask], pred_sample[finite_mask], 'r-', alpha=0.7, label='Predicted', linewidth=1.5)
        
        ax1.set_title('Raw Data vs Predictions (Time Series)', fontsize=16, fontweight='bold')
        ax1.set_xlabel('Time', fontsize=12)
        ax1.set_ylabel('Pb Rougher Concentrate (%)', fontsize=12)
        ax1.legend(fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45, labelsize=10)
        ax1.tick_params(axis='y', labelsize=10)
        
        # 2. Scatter Plot: Actual vs Predicted
        ax2 = axes[0, 1]
        
        # Filter finite values for scatter plot
        finite_mask = np.isfinite(self.y) & np.isfinite(self.predictions)
        
        if np.sum(finite_mask) > 0:
            ax2.scatter(self.y[finite_mask], self.predictions[finite_mask], alpha=0.6, color='blue', s=2)
            
            # Add perfect prediction line
            min_val = min(self.y[finite_mask].min(), self.predictions[finite_mask].min())
            max_val = max(self.y[finite_mask].max(), self.predictions[finite_mask].max())
            ax2.plot([min_val, max_val], [min_val, max_val], 'r--', lw=3, label='Perfect Prediction')
        
        ax2.set_xlabel('Actual Values', fontsize=12)
        ax2.set_ylabel('Predicted Values', fontsize=12)
        ax2.set_title('Actual vs Predicted Scatter Plot', fontsize=16, fontweight='bold')
        ax2.legend(fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(labelsize=10)
        
        # Add R² text
        ax2.text(0.05, 0.95, f'R² = {self.r2:.4f}', transform=ax2.transAxes, 
                bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.9), fontsize=14)
        
        # 3. Error Distribution
        ax3 = axes[1, 0]
        finite_errors = self.errors[np.isfinite(self.errors)]
        
        if len(finite_errors) > 0:
            ax3.hist(finite_errors, bins=50, alpha=0.7, color='green', edgecolor='black')
            ax3.axvline(x=0, color='red', linestyle='--', linewidth=3, label='Zero Error')
        
        ax3.set_xlabel('Prediction Error', fontsize=12)
        ax3.set_ylabel('Frequency', fontsize=12)
        ax3.set_title('Error Distribution', fontsize=16, fontweight='bold')
        ax3.legend(fontsize=12)
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(labelsize=10)
        
        # 4. Percentage Error Distribution
        ax4 = axes[1, 1]
        finite_pct_errors = self.percentage_errors[np.isfinite(self.percentage_errors)]
        
        if len(finite_pct_errors) > 0:
            # Limit to reasonable range for visualization
            finite_pct_errors = finite_pct_errors[finite_pct_errors <= 100]
            ax4.hist(finite_pct_errors, bins=50, alpha=0.7, color='orange', edgecolor='black')
            ax4.axvline(x=10, color='red', linestyle='--', linewidth=3, label='10% Threshold')
        
        ax4.set_xlabel('Percentage Error (%)', fontsize=12)
        ax4.set_ylabel('Frequency', fontsize=12)
        ax4.set_title('Percentage Error Distribution', fontsize=16, fontweight='bold')
        ax4.legend(fontsize=12)
        ax4.grid(True, alpha=0.3)
        ax4.tick_params(labelsize=10)
        
        # 5. Error Over Time (First 1000 points)
        ax5 = axes[2, 0]
        finite_abs_errors = self.absolute_errors[:sample_size]
        finite_time = self.time_index[:sample_size]
        finite_mask = np.isfinite(finite_abs_errors)
        
        if np.sum(finite_mask) > 0:
            ax5.plot(finite_time[finite_mask], finite_abs_errors[finite_mask], 'orange', alpha=0.7, linewidth=1.5)
        
        ax5.set_xlabel('Time', fontsize=12)
        ax5.set_ylabel('Absolute Error', fontsize=12)
        ax5.set_title('Prediction Error Over Time', fontsize=16, fontweight='bold')
        ax5.grid(True, alpha=0.3)
        ax5.tick_params(axis='x', rotation=45, labelsize=10)
        ax5.tick_params(axis='y', labelsize=10)
        
        # 6. Summary Statistics
        ax6 = axes[2, 1]
        ax6.axis('off')
        
        # Create summary text
        summary_text = f"""
        MODEL PERFORMANCE SUMMARY
        
        Overall Metrics:
        • R² Score: {self.r2:.4f}
        • RMSE: {self.rmse:.4f}
        • MAE: {self.mae:.4f}
        • Predictions within 10%: {self.within_10_percent:.2%}
        
        Data Statistics:
        • Total samples: {len(self.y):,}
        • Time period: {self.time_index[0].strftime('%Y-%m-%d')} to {self.time_index[-1].strftime('%Y-%m-%d')}
        • Duration: {(self.time_index[-1] - self.time_index[0]).days} days
        
        Error Analysis:
        • Mean error: {self.errors.mean():.4f}
        • Std error: {self.errors.std():.4f}
        • Max error: {self.absolute_errors.max():.4f}
        • Min error: {self.absolute_errors.min():.4f}
        
        Model Type: {type(self.model).__name__}
        Features Used: {len(self.feature_names) if self.feature_names else 'Unknown'}
        """
        
        ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes, 
                fontsize=12, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.8", facecolor="lightblue", alpha=0.9))
        
        plt.tight_layout()
        
        # Save the main analysis visualization
        Path('Plots').mkdir(exist_ok=True)
        plt.savefig('Plots/main_prediction_analysis.png', dpi=300, bbox_inches='tight')
        print("💾 Main analysis plot saved: Plots/main_prediction_analysis.png")
        
        plt.show()
        
        return fig
    
    def create_time_analysis_plot(self):
        """Create the time-based analysis plot (2x2 grid)."""
        print("⏰ Creating time-based analysis plot...")
        
        # Sample data for time analysis (first 5000 points for performance)
        sample_size = min(5000, len(self.results_df))
        sample_df = self.results_df.head(sample_size)
        
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle('Froth Flotation Prediction Analysis - Time-Based Insights', fontsize=20, fontweight='bold')
        
        # 1. Daily averages (if we have enough data)
        if len(sample_df) > 24:
            daily_stats = sample_df.groupby(sample_df['timestamp'].dt.date).agg({
                'actual': 'mean',
                'predicted': 'mean',
                'absolute_error': 'mean'
            }).reset_index()
            
            daily_stats['date'] = pd.to_datetime(daily_stats['timestamp'])
            
            # Filter finite values
            finite_mask = (
                np.isfinite(daily_stats['actual']) & 
                np.isfinite(daily_stats['predicted'])
            )
            
            if np.sum(finite_mask) > 0:
                axes[0, 0].plot(daily_stats['date'][finite_mask], daily_stats['actual'][finite_mask], 'b-', label='Actual', alpha=0.7, linewidth=2)
                axes[0, 0].plot(daily_stats['date'][finite_mask], daily_stats['predicted'][finite_mask], 'r-', label='Predicted', alpha=0.7, linewidth=2)
            
            axes[0, 0].set_title('Daily Average: Actual vs Predicted', fontsize=16, fontweight='bold')
            axes[0, 0].set_xlabel('Date', fontsize=12)
            axes[0, 0].set_ylabel('Pb Concentrate (%)', fontsize=12)
            axes[0, 0].legend(fontsize=12)
            axes[0, 0].tick_params(axis='x', rotation=45, labelsize=10)
            axes[0, 0].tick_params(axis='y', labelsize=10)
            axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Hourly performance
        if len(sample_df) > 24:
            hourly_stats = sample_df.groupby(sample_df['timestamp'].dt.hour).agg({
                'actual': 'mean',
                'predicted': 'mean',
                'absolute_error': 'mean'
            })
            
            # Filter finite values
            finite_mask = (
                np.isfinite(hourly_stats['actual']) & 
                np.isfinite(hourly_stats['predicted'])
            )
            
            if np.sum(finite_mask) > 0:
                axes[0, 1].plot(hourly_stats.index[finite_mask], hourly_stats['actual'][finite_mask], 'b-o', label='Actual', markersize=8, linewidth=2)
                axes[0, 1].plot(hourly_stats.index[finite_mask], hourly_stats['predicted'][finite_mask], 'r-o', label='Predicted', markersize=8, linewidth=2)
            
            axes[0, 1].set_title('Hourly Average Performance', fontsize=16, fontweight='bold')
            axes[0, 1].set_xlabel('Hour of Day', fontsize=12)
            axes[0, 1].set_ylabel('Pb Concentrate (%)', fontsize=12)
            axes[0, 1].legend(fontsize=12)
            axes[0, 1].grid(True, alpha=0.3)
            axes[0, 1].set_xticks(range(0, 24, 2))
            axes[0, 1].tick_params(labelsize=10)
        
        # 3. Error trends over time
        finite_mask = np.isfinite(sample_df['absolute_error'])
        if np.sum(finite_mask) > 0:
            axes[1, 0].plot(sample_df['timestamp'][finite_mask], sample_df['absolute_error'][finite_mask], 'orange', alpha=0.7, linewidth=1.5)
        
        axes[1, 0].set_title('Error Trends Over Time', fontsize=16, fontweight='bold')
        axes[1, 0].set_xlabel('Time', fontsize=12)
        axes[1, 0].set_ylabel('Absolute Error', fontsize=12)
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].tick_params(axis='x', rotation=45, labelsize=10)
        axes[1, 0].tick_params(axis='y', labelsize=10)
        
        # 4. Performance by time period
        sample_df['hour'] = sample_df['timestamp'].dt.hour
        sample_df['period'] = pd.cut(sample_df['hour'], 
                                   bins=[0, 6, 12, 18, 24], 
                                   labels=['Night', 'Morning', 'Afternoon', 'Evening'])
        
        period_errors = sample_df.groupby('period')['absolute_error'].mean()
        
        # Filter finite values
        finite_periods = period_errors[np.isfinite(period_errors)]
        
        if len(finite_periods) > 0:
            colors = ['navy', 'skyblue', 'orange', 'red'][:len(finite_periods)]
            bars = axes[1, 1].bar(finite_periods.index, finite_periods.values, color=colors, alpha=0.8)
            
            # Add value labels on bars
            for bar, value in zip(bars, finite_periods.values):
                height = bar.get_height()
                axes[1, 1].text(bar.get_x() + bar.get_width()/2., height + 0.01,
                               f'{value:.3f}', ha='center', va='bottom', fontsize=10)
        
        axes[1, 1].set_title('Average Error by Time Period', fontsize=16, fontweight='bold')
        axes[1, 1].set_xlabel('Time Period', fontsize=12)
        axes[1, 1].set_ylabel('Average Absolute Error', fontsize=12)
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].tick_params(labelsize=10)
        
        plt.tight_layout()
        
        # Save time analysis
        plt.savefig('Plots/time_analysis_detailed.png', dpi=300, bbox_inches='tight')
        print("💾 Time analysis plot saved: Plots/time_analysis_detailed.png")
        
        plt.show()
        
        return fig
    
    def print_summary(self):
        """Print a detailed summary."""
        print("\n" + "="*80)
        print("📊 SPLIT PREDICTION ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"\n🏆 MODEL PERFORMANCE:")
        print(f"   • R² Score: {self.r2:.4f} ({self.r2*100:.2f}% accuracy)")
        print(f"   • RMSE: {self.rmse:.4f}")
        print(f"   • MAE: {self.mae:.4f}")
        print(f"   • Predictions within 10%: {self.within_10_percent:.2%}")
        
        print(f"\n📈 DATA OVERVIEW:")
        print(f"   • Total samples: {len(self.y):,}")
        print(f"   • Time period: {self.time_index[0].strftime('%Y-%m-%d %H:%M')} to {self.time_index[-1].strftime('%Y-%m-%d %H:%M')}")
        print(f"   • Duration: {(self.time_index[-1] - self.time_index[0]).days} days")
        print(f"   • Features used: {len(self.feature_names) if self.feature_names else 'Unknown'}")
        
        print(f"\n📊 ERROR ANALYSIS:")
        print(f"   • Mean error: {self.errors.mean():.4f}")
        print(f"   • Standard deviation: {self.errors.std():.4f}")
        print(f"   • Maximum absolute error: {self.absolute_errors.max():.4f}")
        print(f"   • Minimum absolute error: {self.absolute_errors.min():.4f}")
        print(f"   • Median absolute error: {np.median(self.absolute_errors):.4f}")
        
        print(f"\n🎯 PREDICTION ACCURACY BREAKDOWN:")
        within_5 = np.mean(self.percentage_errors <= 5)
        within_10 = np.mean(self.percentage_errors <= 10)
        within_15 = np.mean(self.percentage_errors <= 15)
        within_20 = np.mean(self.percentage_errors <= 20)
        
        print(f"   • Within 5%: {within_5:.2%}")
        print(f"   • Within 10%: {within_10:.2%}")
        print(f"   • Within 15%: {within_15:.2%}")
        print(f"   • Within 20%: {within_20:.2%}")
        
        print(f"\n📁 GENERATED FILES:")
        print(f"   • Main analysis: Plots/main_prediction_analysis.png")
        print(f"   • Time analysis: Plots/time_analysis_detailed.png")
        print(f"   • Results data: split_prediction_results.csv")
        
        # Save results to CSV
        self.results_df.to_csv('split_prediction_results.csv', index=False)
        print(f"\n✅ Results saved to: split_prediction_results.csv")
        
        print("\n" + "="*80)


def main():
    """Main function to run the split prediction visualization."""
    print("🚀 SPLIT FROTH FLOTATION PREDICTION VISUALIZATION")
    print("="*55)
    
    try:
        # Initialize the visualizer
        visualizer = SplitPredictionVisualizer()
        
        # Make predictions
        results_df = visualizer.make_predictions()
        
        # Create main analysis plot
        visualizer.create_main_analysis_plot()
        
        # Create time analysis plot
        visualizer.create_time_analysis_plot()
        
        # Print summary
        visualizer.print_summary()
        
        print(f"\n🎉 Split prediction visualization completed successfully!")
        print(f"📊 Check the generated plots in the 'Plots' directory:")
        print(f"   • Main analysis: Plots/main_prediction_analysis.png")
        print(f"   • Time analysis: Plots/time_analysis_detailed.png")
        print(f"📄 Detailed results saved to 'split_prediction_results.csv'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have:")
        print("   1. Run the training pipeline first")
        print("   2. The enhanced dataset is available")
        print("   3. All required packages are installed")


if __name__ == "__main__":
    main()
