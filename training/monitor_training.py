#!/usr/bin/env python3
"""
Training Progress Monitor
========================

This script helps monitor the progress of training scripts by:
1. Reading log files to show recent activity
2. Checking checkpoint files to show completion status
3. Displaying estimated progress based on completed steps
"""

import os
import time
from pathlib import Path
from datetime import datetime
import argparse

def check_log_file(log_path, lines=20):
    """Read and display recent log entries."""
    if not log_path.exists():
        return f"❌ Log file not found: {log_path}"
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines_list = f.readlines()
        
        if not lines_list:
            return f"📄 Log file is empty: {log_path}"
        
        # Get the last N lines
        recent_lines = lines_list[-lines:] if len(lines_list) > lines else lines_list
        return f"📄 Recent log entries from {log_path}:\n" + "".join(recent_lines)
    
    except Exception as e:
        return f"❌ Error reading log file {log_path}: {e}"

def check_checkpoints(checkpoint_dir):
    """Check checkpoint files and their status."""
    if not checkpoint_dir.exists():
        return f"❌ Checkpoint directory not found: {checkpoint_dir}"
    
    checkpoint_files = list(checkpoint_dir.glob("checkpoint_*.pkl"))
    if not checkpoint_files:
        return f"📁 No checkpoint files found in {checkpoint_dir}"
    
    status = f"📁 Checkpoint files in {checkpoint_dir}:\n"
    for checkpoint_file in checkpoint_files:
        file_size = checkpoint_file.stat().st_size
        mod_time = datetime.fromtimestamp(checkpoint_file.stat().st_mtime)
        status += f"   • {checkpoint_file.name} ({file_size:,} bytes, modified {mod_time.strftime('%Y-%m-%d %H:%M:%S')})\n"
    
    return status

def estimate_progress(checkpoint_dir):
    """Estimate training progress based on checkpoint files."""
    if not checkpoint_dir.exists():
        return "❌ Cannot estimate progress - checkpoint directory not found"
    
    stages = ['data_preparation', 'model_optimization', 'model_evaluation', 'final_results']
    completed_stages = []
    
    for stage in stages:
        checkpoint_file = checkpoint_dir / f"checkpoint_{stage}.pkl"
        if checkpoint_file.exists():
            completed_stages.append(stage)
    
    if not completed_stages:
        return "🔄 Training not started yet"
    
    progress = len(completed_stages) / len(stages) * 100
    
    status = f"🔄 Estimated Progress: {progress:.1f}% ({len(completed_stages)}/{len(stages)} stages)\n"
    status += "📋 Completed stages:\n"
    for stage in completed_stages:
        status += f"   ✅ {stage}\n"
    
    status += "📋 Remaining stages:\n"
    for stage in stages:
        if stage not in completed_stages:
            status += f"   ⏳ {stage}\n"
    
    return status

def monitor_training(horizon):
    """Monitor training for a specific horizon."""
    print(f"🔍 Monitoring {horizon}-minute training progress...")
    print("=" * 60)
    
    # Check log file
    log_path = Path(f"logs/{horizon}min_training.log")
    print(check_log_file(log_path))
    print()
    
    # Check checkpoints
    checkpoint_dir = Path(f"checkpoints_{horizon}min_efficient")
    print(check_checkpoints(checkpoint_dir))
    print()
    
    # Estimate progress
    print(estimate_progress(checkpoint_dir))
    print()
    
    # Check output directory
    output_dir = Path(f"backend/trained_models/{horizon}min_efficient")
    if output_dir.exists():
        output_files = list(output_dir.glob("*"))
        if output_files:
            print(f"📁 Output files in {output_dir}:")
            for file in output_files:
                file_size = file.stat().st_size
                mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                print(f"   • {file.name} ({file_size:,} bytes, modified {mod_time.strftime('%Y-%m-%d %H:%M:%S')})")
        else:
            print(f"📁 Output directory {output_dir} is empty")
    else:
        print(f"📁 Output directory {output_dir} not found")

def main():
    parser = argparse.ArgumentParser(description="Monitor training progress")
    parser.add_argument("horizon", type=int, choices=[5, 15, 30, 60], 
                       help="Training horizon to monitor (5, 15, 30, or 60 minutes)")
    
    args = parser.parse_args()
    monitor_training(args.horizon)

if __name__ == "__main__":
    main()
