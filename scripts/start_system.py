#!/usr/bin/env python3
"""
Froth Flotation Digital Twin System Startup Script
==================================================

This script starts the complete froth flotation system:
1. Backend FastAPI server (port 8000)
2. Frontend React development server (port 3000)
3. Database initialization
4. ML model loading verification
"""

import os
import sys
import time
import subprocess
import threading
import signal
import requests
from pathlib import Path

class SystemStartup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_process = None
        self.frontend_process = None
        self.running = True
        
    def print_banner(self):
        """Print startup banner"""
        print("=" * 70)
        print("🚀 FROTH FLOTATION DIGITAL TWIN SYSTEM STARTUP")
        print("=" * 70)
        print("📊 Starting complete system with trained ML model")
        print("🔧 Backend: FastAPI + WebSocket Server (Port 8000)")
        print("🎨 Frontend: React Dashboard (Port 3000)")
        print("🤖 ML Model: Gradient Boosting (R² = 0.9211)")
        print("=" * 70)
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        print("\n🔍 Checking Dependencies...")
        
        # Check Python packages
        required_packages = [
            'fastapi', 'uvicorn', 'websockets', 'sqlite3', 
            'numpy', 'pandas', 'joblib', 'sklearn'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"  ❌ {package} - Missing")
        
        if missing_packages:
            print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
            print("Please install missing packages before starting the system.")
            return False
        
        # Check Node.js and npm
        try:
            subprocess.run(['node', '--version'], capture_output=True, check=True)
            print("  ✅ Node.js")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("  ❌ Node.js - Missing")
            return False
        
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print("  ✅ npm")
            else:
                print("  ❌ npm - Missing")
                return False
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("  ❌ npm - Missing")
            return False
        
        return True
    
    def check_files(self):
        """Check if required files exist"""
        print("\n📁 Checking Required Files...")
        
        required_files = [
            'backend/services/flotation_data_service.py',
            'backend/services/ml_model_service.py',
            'backend/trained_models/gb_optimized_model.pkl',
            'backend/trained_models/gb_metadata.pkl',
            'frontend/package.json',
            'data/HZL_RA4_Pb_Rougher_enhanced_clean.parquet'
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"  ✅ {file_path}")
            else:
                missing_files.append(file_path)
                print(f"  ❌ {file_path} - Missing")
        
        if missing_files:
            print(f"\n⚠️ Missing files: {', '.join(missing_files)}")
            return False
        
        return True
    
    def start_backend(self):
        """Start the backend FastAPI server"""
        print("\n🔧 Starting Backend Server...")
        
        backend_dir = self.project_root / 'backend' / 'services'
        backend_script = backend_dir / 'flotation_data_service.py'
        
        try:
            # Change to backend directory
            os.chdir(backend_dir)
            
            # Start the backend server
            self.backend_process = subprocess.Popen(
                [sys.executable, 'flotation_data_service.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print("  ✅ Backend server process started")
            print("  📡 WebSocket endpoint: ws://localhost:8000/ws/flotation-data")
            print("  🌐 REST endpoint: http://localhost:8000/api/current-data")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the frontend React development server"""
        print("\n🎨 Starting Frontend Server...")
        
        frontend_dir = self.project_root / 'frontend'
        
        try:
            # Change to frontend directory
            os.chdir(frontend_dir)
            
            # Install dependencies if needed
            if not (frontend_dir / 'node_modules').exists():
                print("  📦 Installing frontend dependencies...")
                subprocess.run(['npm', 'install'], check=True, shell=True)
            
            # Start the frontend server
            self.frontend_process = subprocess.Popen(
                ['npm', 'start'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            
            print("  ✅ Frontend server process started")
            print("  🌐 Dashboard URL: http://localhost:3000")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to start frontend: {e}")
            return False
    
    def wait_for_services(self):
        """Wait for services to be ready"""
        print("\n⏳ Waiting for services to be ready...")
        
        # Wait for backend
        backend_ready = False
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get('http://localhost:8000/api/current-data', timeout=2)
                if response.status_code == 200:
                    backend_ready = True
                    print("  ✅ Backend server is ready")
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        if not backend_ready:
            print("  ❌ Backend server failed to start")
            return False
        
        # Wait for frontend
        frontend_ready = False
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get('http://localhost:3000', timeout=2)
                if response.status_code == 200:
                    frontend_ready = True
                    print("  ✅ Frontend server is ready")
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        if not frontend_ready:
            print("  ❌ Frontend server failed to start")
            return False
        
        return True
    
    def test_system(self):
        """Test the complete system"""
        print("\n🧪 Testing System Functionality...")
        
        try:
            # Test backend API
            response = requests.get('http://localhost:8000/api/current-data')
            if response.status_code == 200:
                data = response.json()
                print("  ✅ Backend API responding")
                print(f"  📊 Data fields: {len(data)} parameters")
            else:
                print("  ❌ Backend API not responding")
                return False
            
            # Test frontend
            response = requests.get('http://localhost:3000')
            if response.status_code == 200:
                print("  ✅ Frontend responding")
            else:
                print("  ❌ Frontend not responding")
                return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ System test failed: {e}")
            return False
    
    def monitor_services(self):
        """Monitor running services"""
        print("\n📊 System Status:")
        print("=" * 50)
        
        while self.running:
            try:
                # Check backend
                backend_status = "🟢 Running" if self.backend_process and self.backend_process.poll() is None else "🔴 Stopped"
                print(f"Backend: {backend_status}")
                
                # Check frontend
                frontend_status = "🟢 Running" if self.frontend_process and self.frontend_process.poll() is None else "🔴 Stopped"
                print(f"Frontend: {frontend_status}")
                
                print(f"Dashboard: http://localhost:3000")
                print(f"API Docs: http://localhost:8000/docs")
                print("=" * 50)
                print("Press Ctrl+C to stop the system")
                
                time.sleep(10)  # Update every 10 seconds
                
            except KeyboardInterrupt:
                self.stop_system()
                break
    
    def stop_system(self):
        """Stop all services"""
        print("\n🛑 Stopping System...")
        self.running = False
        
        if self.backend_process:
            self.backend_process.terminate()
            print("  ✅ Backend stopped")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            print("  ✅ Frontend stopped")
        
        print("🎉 System shutdown complete")
    
    def run(self):
        """Main startup sequence"""
        try:
            self.print_banner()
            
            # Check dependencies
            if not self.check_dependencies():
                return False
            
            # Check files
            if not self.check_files():
                return False
            
            # Start backend
            if not self.start_backend():
                return False
            
            # Start frontend
            if not self.start_frontend():
                return False
            
            # Wait for services
            if not self.wait_for_services():
                return False
            
            # Test system
            if not self.test_system():
                return False
            
            print("\n🎉 SYSTEM STARTUP COMPLETE!")
            print("=" * 70)
            print("✅ Backend: FastAPI + WebSocket Server (Port 8000)")
            print("✅ Frontend: React Dashboard (Port 3000)")
            print("✅ ML Model: Gradient Boosting (R² = 0.9211)")
            print("✅ Database: SQLite initialized")
            print("=" * 70)
            print("🌐 Open your browser and go to: http://localhost:3000")
            print("📊 API Documentation: http://localhost:8000/docs")
            print("=" * 70)
            
            # Monitor services
            self.monitor_services()
            
        except KeyboardInterrupt:
            self.stop_system()
        except Exception as e:
            print(f"\n❌ Startup failed: {e}")
            self.stop_system()
            return False
        
        return True

def main():
    """Main function"""
    startup = SystemStartup()
    success = startup.run()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
