@echo off
echo Starting 60-minute horizon training...
echo.
echo This will:
echo - Train Ridge, Random Forest, and XGBoost models
echo - Save progress to logs/60min_training.log
echo - Create checkpoints for resumable training
echo - Generate visualizations and model files
echo.
echo Press any key to start training...
pause >nul

python training/train_60min_efficient.py

echo.
echo Training completed! Check logs/60min_training.log for details.
pause

