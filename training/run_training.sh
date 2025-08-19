#!/bin/bash
# Froth Flotation ML Training - Server Run Script
# ==============================================

echo "🚀 Starting Froth Flotation ML Training on Server"
echo "=================================================="

# Set environment variables for optimal performance
export OMP_NUM_THREADS=$(nproc)
export MKL_NUM_THREADS=$(nproc)
export NUMEXPR_NUM_THREADS=$(nproc)

# Check if data file exists
if [ ! -f "HZL_RA4_Pb_Rougher_enhanced_clean.parquet" ]; then
    echo "❌ Data file not found: HZL_RA4_Pb_Rougher_enhanced_clean.parquet"
    exit 1
fi

# Check if optimized pipeline exists
if [ ! -f "training_pipeline_optimized.py" ]; then
    echo "❌ Optimized pipeline not found. Run server_training_setup.py first."
    exit 1
fi

echo "📊 Starting training with optimized settings..."
echo "⏰ Start time: $(date)"

# Run the training pipeline
python training_pipeline_optimized.py

echo "⏰ End time: $(date)"
echo "✅ Training completed!"

# Check for generated model files
if [ -f "backend/trained_models/"*.pkl ]; then
    echo "🎉 Model files generated successfully!"
    ls -la backend/trained_models/
else
    echo "⚠️  No model files found in backend/trained_models/"
fi
