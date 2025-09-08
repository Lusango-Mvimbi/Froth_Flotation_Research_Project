@echo off
echo Starting 30-minute horizon training...
echo.
echo This will:
echo - Train Ridge, Random Forest, and XGBoost models
echo - Save progress to logs/30min_training.log
echo - Create checkpoints for resumable training
echo - Generate visualizations and model files
echo.
echo Press any key to start training...
pause >nul

python training/train_30min_efficient.py

echo.
echo Training completed! Check logs/30min_training.log for details.
pause

