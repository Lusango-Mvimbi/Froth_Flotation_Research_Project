import os
import sys
import argparse
from typing import List
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.feature_selection import SelectKBest, mutual_info_regression


def list_raw_files(raw_dir: str) -> List[str]:
    """List all raw monthly parquet files."""
    files = [
        os.path.join(raw_dir, f)
        for f in os.listdir(raw_dir)
        if f.lower().endswith('.parquet') and 'HZL_RA4_Pb_Rougher' in f
    ]
    files.sort()
    return files


def read_month(path: str) -> pd.DataFrame:
    """Read a monthly parquet file."""
    try:
        df = pd.read_parquet(path)
        return df
    except Exception as exc:
        raise RuntimeError(f"Failed to read {path}: {exc}")


def ensure_timestamp_index(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure DataFrame has proper timestamp index."""
    # Try common timestamp column names
    candidate_cols = [
        'Timestamp', 'timestamp', 'DateTime', 'Datetime', 'date', 'time', 'Date_Time', 'DATE_TIME'
    ]
    for col in candidate_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce', utc=False)
            df = df.set_index(col)
            df.index.name = 'Timestamp'
            return df
    
    # If already indexed by datetime
    if isinstance(df.index, pd.DatetimeIndex):
        df.index.name = 'Timestamp'
        return df
    
    # As a last resort, try to infer from any column with datetime dtype
    datetime_cols = [c for c in df.columns if np.issubdtype(df[c].dtype, np.datetime64)]
    if datetime_cols:
        col = datetime_cols[0]
        df = df.set_index(col)
        df.index.name = 'Timestamp'
        return df
    
    raise ValueError("Could not find a timestamp column to index the data.")


def unify_columns(monthly_frames: List[pd.DataFrame]) -> List[pd.DataFrame]:
    """Make columns consistent across all monthly frames."""
    # Build the union of columns across all months
    all_cols = set()
    for frame in monthly_frames:
        all_cols.update(frame.columns.tolist())
    all_cols = list(all_cols)
    
    # Reindex each frame to have the same columns
    unified = []
    for frame in monthly_frames:
        missing = [c for c in all_cols if c not in frame.columns]
        if missing:
            frame = frame.reindex(columns=frame.columns.tolist() + missing)
        unified.append(frame)
    
    return unified


def clean_and_impute(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and impute the dataset as per documentation."""
    # Sort and de-duplicate by timestamp index
    df = df[~df.index.duplicated(keep='last')]
    df = df.sort_index()
    
    # Remove entirely empty columns
    df = df.dropna(axis=1, how='all')
    
    # Handle infinite values
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # Handle missing values in features (median imputation as per documentation)
    if df.isnull().any().any():
        print("   Handling missing values in features...")
        df = df.fillna(df.median())
    
    # Handle missing values in target
    if 'Pb_Rougher_Conc_Pb' in df.columns and df['Pb_Rougher_Conc_Pb'].isnull().any():
        print("   Handling missing values in target...")
        df['Pb_Rougher_Conc_Pb'] = df['Pb_Rougher_Conc_Pb'].fillna(df['Pb_Rougher_Conc_Pb'].median())
    
    # Remove any remaining problematic values
    valid_mask = (
        np.isfinite(df).all(axis=1) & 
        (df['Pb_Rougher_Conc_Pb'] > 0) if 'Pb_Rougher_Conc_Pb' in df.columns else np.isfinite(df).all(axis=1)
    )
    df = df[valid_mask]
    
    return df


def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create time-based features as per documentation."""
    print("   Creating time features...")
    df_time = df.copy()
    
    # Extract time components
    df_time['year'] = df.index.year
    df_time['month'] = df.index.month
    df_time['hour'] = df.index.hour
    df_time['day_of_week'] = df.index.dayofweek
    df_time['day_of_year'] = df.index.dayofyear
    
    # Cyclical encoding for periodic features
    df_time['hour_sin'] = np.sin(2 * np.pi * df_time['hour'] / 24)
    df_time['hour_cos'] = np.cos(2 * np.pi * df_time['hour'] / 24)
    df_time['day_sin'] = np.sin(2 * np.pi * df_time['day_of_week'] / 7)
    df_time['day_cos'] = np.cos(2 * np.pi * df_time['day_of_week'] / 7)
    df_time['month_sin'] = np.sin(2 * np.pi * df_time['month'] / 12)
    df_time['month_cos'] = np.cos(2 * np.pi * df_time['month'] / 12)
    
    return df_time


def create_lagged_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create lagged features (1-5 period lags) as per documentation."""
    print("   Creating lagged features...")
    df_lagged = df.copy()
    
    # Get base columns (exclude time features and target)
    base_cols = [col for col in df.columns if col != 'Pb_Rougher_Conc_Pb' and col not in 
                 ['year', 'month', 'hour', 'day_of_week', 'day_of_year', 
                  'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos']]
    
    # 1-5 period lags for key variables as per documentation
    lag_periods = [1, 2, 3, 4, 5]
    
    for col in base_cols:
        for lag in lag_periods:
            df_lagged[f'{col}_lag_{lag}'] = df[col].shift(lag)
    
    return df_lagged


def create_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create rolling statistics (30-minute periods) as per documentation."""
    print("   Creating rolling features...")
    df_rolling = df.copy()
    
    # 30-minute rolling window (6 rows for 5-minute intervals)
    window_30min = 6
    
    # Get base columns (exclude time features and target)
    base_cols = [col for col in df.columns if col != 'Pb_Rougher_Conc_Pb' and col not in 
                 ['year', 'month', 'hour', 'day_of_week', 'day_of_year', 
                  'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos']]
    
    for col in base_cols:
        # Rolling statistics: Mean, standard deviation, minimum, maximum
        df_rolling[f'{col}_roll_mean_30min'] = df[col].rolling(window=window_30min, min_periods=1).mean()
        df_rolling[f'{col}_roll_std_30min'] = df[col].rolling(window=window_30min, min_periods=1).std()
        df_rolling[f'{col}_roll_min_30min'] = df[col].rolling(window=window_30min, min_periods=1).min()
        df_rolling[f'{col}_roll_max_30min'] = df[col].rolling(window=window_30min, min_periods=1).max()
    
    return df_rolling


def create_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create interaction features (cross-products) as per documentation."""
    print("   Creating interaction features...")
    df_interaction = df.copy()
    
    # Get key process variables (exclude time features and target)
    key_cols = [col for col in df.columns if col != 'Pb_Rougher_Conc_Pb' and col not in 
                ['year', 'month', 'hour', 'day_of_week', 'day_of_year', 
                 'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos']]
    
    # Limit to top 5 key variables to avoid explosion (reduced from 10)
    key_cols = key_cols[:5]
    
    # Create cross-products of key process variables
    for i, col1 in enumerate(key_cols):
        for col2 in key_cols[i+1:]:
            df_interaction[f'{col1}_x_{col2}'] = df[col1] * df[col2]
    
    return df_interaction


def create_polynomial_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create polynomial features (quadratic and cubic) as per documentation."""
    print("   Creating polynomial features...")
    df_poly = df.copy()
    
    # Get key process variables (exclude time features and target)
    key_cols = [col for col in df.columns if col != 'Pb_Rougher_Conc_Pb' and col not in 
                ['year', 'month', 'hour', 'day_of_week', 'day_of_year', 
                 'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos']]
    
    # Limit to top 3 key variables to avoid explosion (reduced from 5)
    key_cols = key_cols[:3]
    
    # Create quadratic and cubic terms for key variables
    for col in key_cols:
        df_poly[f'{col}_squared'] = df[col] ** 2
        df_poly[f'{col}_cubed'] = df[col] ** 3
    
    return df_poly


def create_rate_of_change_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create rate of change features (derivatives) as per documentation."""
    print("   Creating rate of change features...")
    df_roc = df.copy()
    
    # Get base columns (exclude time features and target)
    base_cols = [col for col in df.columns if col != 'Pb_Rougher_Conc_Pb' and col not in 
                 ['year', 'month', 'hour', 'day_of_week', 'day_of_year', 
                  'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos']]
    
    for col in base_cols:
        # First derivative (rate of change)
        df_roc[f'{col}_rate_of_change'] = df[col].diff()
        
        # Second derivative (acceleration)
        df_roc[f'{col}_acceleration'] = df[col].diff().diff()
    
    return df_roc


def create_statistical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create statistical features (z-scores, percentiles) as per documentation."""
    print("   Creating statistical features...")
    df_stats = df.copy()
    
    # Get base columns (exclude time features and target)
    base_cols = [col for col in df.columns if col != 'Pb_Rougher_Conc_Pb' and col not in 
                 ['year', 'month', 'hour', 'day_of_week', 'day_of_year', 
                  'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos']]
    
    # Limit to top 10 base columns to avoid memory explosion
    base_cols = base_cols[:10]
    
    # 30-minute rolling window for statistical measures
    window_30min = 6
    
    for col in base_cols:
        # Z-scores (rolling)
        rolling_mean = df[col].rolling(window=window_30min, min_periods=1).mean()
        rolling_std = df[col].rolling(window=window_30min, min_periods=1).std()
        zscore = (df[col] - rolling_mean) / rolling_std
        # Handle division by zero and infinite values
        zscore = zscore.replace([np.inf, -np.inf], np.nan)
        df_stats[f'{col}_zscore_30min'] = zscore
        
        # Percentiles (rolling)
        df_stats[f'{col}_p25_30min'] = df[col].rolling(window=window_30min, min_periods=1).quantile(0.25)
        df_stats[f'{col}_p75_30min'] = df[col].rolling(window=window_30min, min_periods=1).quantile(0.75)
        
        # Distribution statistics
        df_stats[f'{col}_skew_30min'] = df[col].rolling(window=window_30min, min_periods=1).skew()
        df_stats[f'{col}_kurt_30min'] = df[col].rolling(window=window_30min, min_periods=1).kurt()
    
    return df_stats


def enhance_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all 7 feature engineering steps as per documentation."""
    print("🔧 Applying comprehensive feature engineering...")
    
    # 1. Time-based Features
    df = create_time_features(df)
    
    # 2. Lagged Features (1-5 period lags)
    df = create_lagged_features(df)
    
    # 3. Rolling Statistics (30-minute periods)
    df = create_rolling_features(df)
    
    # 4. Interaction Features (cross-products)
    df = create_interaction_features(df)
    
    # 5. Polynomial Features (quadratic and cubic)
    df = create_polynomial_features(df)
    
    # 6. Rate of Change Features (derivatives)
    df = create_rate_of_change_features(df)
    
    # 7. Statistical Features (z-scores, percentiles)
    df = create_statistical_features(df)
    
    # Clean up any NaN and infinite values created by feature engineering
    print("   Cleaning up NaN and infinite values...")
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(method='bfill').fillna(method='ffill')
    
    print(f"   Enhanced features: {df.shape[1]} columns")
    return df


def apply_feature_selection(df: pd.DataFrame, target_col: str = 'Pb_Rougher_Conc_Pb') -> pd.DataFrame:
    """Apply feature selection as per documentation."""
    print("🎯 Applying feature selection...")
    
    if target_col not in df.columns:
        print("   Target column not found, skipping feature selection")
        return df
    
    # Separate features and target
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Final cleanup of any remaining infinite values
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())
    
    # Apply mutual information selection (k=200 as per documentation)
    k = min(200, X.shape[1])
    selector = SelectKBest(score_func=mutual_info_regression, k=k)
    X_selected = selector.fit_transform(X, y)
    selected_features = X.columns[selector.get_support()].tolist()
    
    # Create final dataframe with selected features and target
    df_selected = df[selected_features + [target_col]]
    
    print(f"   Selected {len(selected_features)} features from {X.shape[1]} initial features")
    return df_selected


def sample_data(df: pd.DataFrame, max_samples: int = 50000) -> pd.DataFrame:
    """Sample data for processing efficiency as per documentation."""
    print("⚡ Sampling data for processing efficiency...")
    
    if len(df) <= max_samples:
        print(f"   No sampling needed: {len(df)} samples")
        return df
    
    # Random sampling without replacement
    sample_size = max_samples
    sample_indices = np.random.choice(len(df), sample_size, replace=False)
    df_sampled = df.iloc[sample_indices]
    
    print(f"   Sampled {sample_size} records from {len(df)} total records")
    return df_sampled


def build_enhanced_dataset(raw_dir: str) -> pd.DataFrame:
    """Build the enhanced dataset from raw monthly files as per documentation."""
    raw_files = list_raw_files(raw_dir)
    if not raw_files:
        raise FileNotFoundError(f"No parquet files found in: {raw_dir}")
    
    print(f"📊 Processing {len(raw_files)} monthly files...")
    monthly_frames = []
    for i, path in enumerate(raw_files):
        print(f"   Reading {os.path.basename(path)} ({i+1}/{len(raw_files)})")
        month_df = read_month(path)
        month_df = ensure_timestamp_index(month_df)
        monthly_frames.append(month_df)
    
    # Make columns consistent across months
    print("🔄 Unifying columns across months...")
    monthly_frames = unify_columns(monthly_frames)
    
    # Concatenate chronologically
    print("📈 Concatenating monthly data...")
    df_all = pd.concat(monthly_frames, axis=0, sort=False)
    
    # Ensure timestamp index formatting
    df_all.index = pd.to_datetime(df_all.index, errors='coerce')
    df_all.index.name = 'Timestamp'
    
    # Keep only numeric features
    print("🔢 Selecting numeric features...")
    df_all = df_all.select_dtypes(include=[np.number])
    
    # Clean and impute missing values
    print("🧹 Cleaning and imputing data...")
    df_all = clean_and_impute(df_all)
    
    # Sample data FIRST for processing efficiency (as per documentation)
    print("⚡ Sampling data for processing efficiency...")
    df_all = sample_data(df_all, max_samples=50000)
    
    # Apply comprehensive feature engineering (all 7 types) on sampled data
    df_all = enhance_features(df_all)
    
    # Apply feature selection (mutual information, k=200)
    df_all = apply_feature_selection(df_all)
    
    return df_all


def build_enhanced_dataset_simple(raw_dir: str) -> pd.DataFrame:
    """Build simplified enhanced dataset for fast processing."""
    raw_files = list_raw_files(raw_dir)
    if not raw_files:
        raise FileNotFoundError(f"No parquet files found in: {raw_dir}")
    
    print(f"📊 Processing {len(raw_files)} monthly files...")
    monthly_frames = []
    for i, path in enumerate(raw_files):
        print(f"   Reading {os.path.basename(path)} ({i+1}/{len(raw_files)})")
        month_df = read_month(path)
        month_df = ensure_timestamp_index(month_df)
        monthly_frames.append(month_df)
    
    # Make columns consistent across months
    print("🔄 Unifying columns across months...")
    monthly_frames = unify_columns(monthly_frames)
    
    # Concatenate chronologically
    print("📈 Concatenating monthly data...")
    df_all = pd.concat(monthly_frames, axis=0, sort=False)
    
    # Ensure timestamp index formatting
    df_all.index = pd.to_datetime(df_all.index, errors='coerce')
    df_all.index.name = 'Timestamp'
    
    # Keep only numeric features
    print("🔢 Selecting numeric features...")
    df_all = df_all.select_dtypes(include=[np.number])
    
    # Clean and impute missing values
    print("🧹 Cleaning and imputing data...")
    df_all = clean_and_impute(df_all)
    
    # Add basic time features only
    df_all = create_time_features(df_all)
    
    return df_all


def save_parquet(df: pd.DataFrame, output_path: str, overwrite: bool = False) -> None:
    """Save the enhanced dataset to parquet format."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(
            f"Output already exists: {output_path}. Use --overwrite to replace it."
        )
    df.to_parquet(output_path)


def parse_args(argv: List[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Rebuild enhanced clean dataset from monthly raw files.')
    parser.add_argument('--raw-dir', type=str, default=r'C:\@Python Projects\TUT Research Project\Raw_Data', 
                       help='Directory containing monthly raw parquet files')
    parser.add_argument('--output', type=str, default=os.path.join('data', 'HZL_RA4_Pb_Rougher_enhanced_clean.parquet'), 
                       help='Path to save enhanced parquet')
    parser.add_argument('--inspect', action='store_true', help='Only build in-memory and print stats without saving')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite output file if it exists')
    parser.add_argument('--fast', action='store_true', help='Use fast mode with limited features')
    return parser.parse_args(argv)


def main(argv: List[str]) -> None:
    """Main function."""
    args = parse_args(argv)
    print(f"📁 Raw dir: {args.raw_dir}")
    print(f"💾 Output:  {args.output}")
    print("🚀 Building enhanced dataset...")
    
    if args.fast:
        print("⚡ Fast mode: Using simplified feature engineering...")
        # Use simplified version for speed
        df = build_enhanced_dataset_simple(args.raw_dir)
    else:
        print("🔧 Full mode: Using complete feature engineering as per documentation...")
        # Use full version for complete features
        df = build_enhanced_dataset(args.raw_dir)
    
    print(f"✅ Built dataframe: shape={df.shape}, columns={len(df.columns)}")
    print(f"   Index name: {df.index.name}, type: {type(df.index)}")
    print(f"   Index range: {df.index.min()} to {df.index.max()}")
    print("   Dtypes summary:\n", df.dtypes.value_counts())
    
    if args.inspect:
        print("🔎 Inspect mode: not saving to disk.")
        return
    
    print("💾 Saving parquet...")
    save_parquet(df, args.output, overwrite=args.overwrite)
    print("🎉 Done.")


if __name__ == '__main__':
    main(sys.argv[1:])
