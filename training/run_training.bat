@echo off
REM Froth Flotation ML Training - Windows Run Script
REM ================================================

echo 🚀 Starting Froth Flotation ML Training on Server
echo ==================================================

REM Set environment variables for optimal performance
set OMP_NUM_THREADS=%NUMBER_OF_PROCESSORS%
set MKL_NUM_THREADS=%NUMBER_OF_PROCESSORS%
set NUMEXPR_NUM_THREADS=%NUMBER_OF_PROCESSORS%

REM Check if data file exists
if not exist "HZL_RA4_Pb_Rougher_enhanced_clean.parquet" (
    echo ❌ Data file not found: HZL_RA4_Pb_Rougher_enhanced_clean.parquet
    pause
    exit /b 1
)

REM Check if optimized pipeline exists
if not exist "training_pipeline_optimized.py" (
    echo ❌ Optimized pipeline not found. Run server_training_setup.py first.
    pause
    exit /b 1
)

echo 📊 Starting training with optimized settings...
echo ⏰ Start time: %date% %time%

REM Run the training pipeline
python training_pipeline_optimized.py

echo ⏰ End time: %date% %time%
echo ✅ Training completed!

REM Check for generated model files
if exist "backend\trained_models\*.pkl" (
    echo 🎉 Model files generated successfully!
    dir backend\trained_models\*.pkl
) else (
    echo ⚠️  No model files found in backend\trained_models\
)

pause
