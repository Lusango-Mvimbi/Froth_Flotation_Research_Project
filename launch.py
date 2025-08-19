#!/usr/bin/env python3
"""
Main Launcher Script
===================

Simple launcher that calls the main system launcher.
"""

import sys
import os

def main():
    """Main function"""
    # Get the path to the scripts directory
    scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
    launcher_script = os.path.join(scripts_dir, 'launch_froth_flotation_system.py')
    
    # Check if the launcher script exists
    if not os.path.exists(launcher_script):
        print("Error: Main launcher script not found!")
        print(f"Expected location: {launcher_script}")
        return 1
    
    # Import and run the launcher
    sys.path.insert(0, scripts_dir)
    
    try:
        from launch_froth_flotation_system import main as launcher_main
        return launcher_main()
    except ImportError as e:
        print(f"Error importing launcher: {e}")
        return 1
    except Exception as e:
        print(f"Error running launcher: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

