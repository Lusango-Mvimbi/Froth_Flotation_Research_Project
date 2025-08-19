#!/usr/bin/env python3
"""
Launch Froth Flotation Digital Twin System
==========================================

This script launches the complete froth flotation system:
- Backend FastAPI server (port 8000)
- Frontend React development server (port 3000)
- ML model integration
- Real-time data processing
"""

import os
import sys
import time
import subprocess
import threading
import signal
import requests
from pathlib import Path

class FrothFlotationLauncher:
    def __init__(self, cleanup_first=False):
        self.project_root = Path(__file__).parent.parent
        self.backend_process = None
        self.auth_process = None
        self.frontend_process = None
        self.running = True
        self.cleanup_first = cleanup_first
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def print_banner(self):
        """Print startup banner"""
        print("=" * 70)
        print("FROTH FLOTATION DIGITAL TWIN SYSTEM")
        print("=" * 70)
        print("Industrial Process Monitoring & Control")
        print("ML-Powered Predictive Analytics")
        print("Real-time Dashboard & WebSocket Communication")
        print("=" * 70)
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals for graceful shutdown"""
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.stop_system()
        # Force exit to ensure all processes are killed
        os._exit(0)
    
    def start_backend(self):
        """Start the backend FastAPI server"""
        print("\nStarting Backend Server...")
        
        # Check if backend is already running
        try:
            response = requests.get('http://localhost:8000/api/current-data', timeout=2)
            if response.status_code == 200:
                print("  Backend server already running")
                print("  WebSocket: ws://localhost:8000/ws/flotation-data")
                print("  API: http://localhost:8000/api/current-data")
                print("  Docs: http://localhost:8000/docs")
                self.backend_process = None  # No process to manage
                return True
        except requests.exceptions.RequestException:
            pass  # Backend not running, continue with startup
        
        backend_dir = self.project_root / 'backend' / 'services'
        backend_script = backend_dir / 'simple_data_service.py'
        
        # Use absolute paths
        backend_script_abs = backend_script.absolute()
        backend_dir_abs = backend_dir.absolute()
        
        try:
            # Start the backend server with real-time output
            self.backend_process = subprocess.Popen(
                [sys.executable, str(backend_script_abs)],
                stdout=None,  # Show output in real-time
                stderr=None,  # Show errors in real-time
                text=True
            )
            
            # Give it a moment to start
            time.sleep(3)
            
            # Check if process is still running
            if self.backend_process.poll() is None:
                print("  Backend server started")
                print("  WebSocket: ws://localhost:8000/ws/flotation-data")
                print("  API: http://localhost:8000/api/current-data")
                print("  Docs: http://localhost:8000/docs")
                return True
            else:
                print("  Backend server failed to start (process exited)")
                return False
        except Exception as e:
            print(f"  Failed to start backend: {e}")
            return False
    
    def start_auth_service(self):
        """Start the authentication service"""
        print("\nStarting Authentication Service...")
        
        # Check if auth service is already running
        try:
            response = requests.get('http://localhost:8051/login', timeout=2)
            if response.status_code == 200:
                print("  Authentication service already running")
                print("  Auth API: http://localhost:8051")
                print("  Login: http://localhost:8051/login")
                self.auth_process = None  # No process to manage
                return True
        except requests.exceptions.RequestException:
            pass  # Auth service not running, continue with startup
        
        backend_dir = self.project_root / 'backend' / 'services'
        auth_script = backend_dir / 'authentication_service.py'
        
        # Use absolute paths
        auth_script_abs = auth_script.absolute()
        backend_dir_abs = backend_dir.absolute()
        
        try:
            # Start the authentication service
            self.auth_process = subprocess.Popen(
                [sys.executable, str(auth_script_abs)],
                stdout=None,  # Show output in real-time
                stderr=None,  # Show errors in real-time
                text=True
            )
            
            # Give it a moment to start
            time.sleep(3)
            
            # Check if process is still running
            if self.auth_process.poll() is None:
                print("  Authentication service started")
                print("  Auth API: http://localhost:8051")
                print("  Login: http://localhost:8051/login")
                return True
            else:
                print("  Authentication service failed to start (process exited)")
                return False

        except Exception as e:
            print(f"  Failed to start authentication service: {e}")
            return False
    
    def start_frontend(self):
        """Start the frontend React development server"""
        print("\nStarting Frontend Server...")
        
        # Check if frontend is already running
        try:
            response = requests.get('http://localhost:3000', timeout=2)
            if response.status_code == 200:
                print("  Frontend server already running")
                print("  Dashboard: http://localhost:3000")
                self.frontend_process = None  # No process to manage
                return True
        except requests.exceptions.RequestException:
            pass  # Frontend not running, continue with startup
        
        frontend_dir = self.project_root / 'frontend'
        
        try:
            # Start the frontend server with real-time output
            self.frontend_process = subprocess.Popen(
                ['npm', 'start'],
                stdout=None,  # Show output in real-time
                stderr=None,  # Show errors in real-time
                text=True,
                shell=True,
                cwd=str(frontend_dir)  # Set working directory without changing current dir
            )
            
            # Give it a moment to start
            time.sleep(3)
            
            # Check if process is still running
            if self.frontend_process.poll() is None:
                print("  Frontend server started")
                print("  Dashboard: http://localhost:3000")
                return True
            else:
                print("  Frontend server failed to start (process exited)")
                return False
            
        except Exception as e:
            print(f"  Failed to start frontend: {e}")
            return False
    
    def wait_for_services(self):
        """Wait for services to be ready"""
        print("\nWaiting for services to be ready...")
        
        # Wait for authentication service first
        auth_ready = False
        print("  Checking authentication service...")
        for i in range(30):
            try:
                response = requests.get('http://localhost:8051/login', timeout=2)
                if response.status_code == 200:
                    auth_ready = True
                    print("  Authentication service ready")
                    break
            except requests.exceptions.RequestException:
                if i % 5 == 0:  # Show progress every 5 seconds
                    print(f"  Auth service not ready yet... ({i+1}/30)")
            time.sleep(1)
        
        if not auth_ready:
            print("  Authentication service failed to start")
            print("  Try running: cd backend\\services && python authentication_service.py")
            return False
        
        # Wait for backend
        backend_ready = False
        print("  Checking backend server...")
        for i in range(30):
            try:
                response = requests.get('http://localhost:8000/api/current-data', timeout=2)
                if response.status_code == 200:
                    backend_ready = True
                    print("  Backend server ready")
                    break
            except requests.exceptions.RequestException:
                if i % 5 == 0:  # Show progress every 5 seconds
                    print(f"  Backend not ready yet... ({i+1}/30)")
            time.sleep(1)
        
        if not backend_ready:
            print("  Backend server failed to start")
            print("  Try running: cd backend\\services && python simple_data_service.py")
            return False
        
        # Wait for frontend
        frontend_ready = False
        print("  Checking frontend server...")
        for i in range(30):
            try:
                response = requests.get('http://localhost:3000', timeout=2)
                if response.status_code == 200:
                    frontend_ready = True
                    print("  Frontend server ready")
                    break
            except requests.exceptions.RequestException:
                if i % 5 == 0:  # Show progress every 5 seconds
                    print(f"  Frontend not ready yet... ({i+1}/30)")
            time.sleep(1)
        
        if not frontend_ready:
            print("  Frontend server failed to start")
            print("  Try running: cd frontend && npm start")
            return False
        
        return True
    
    def test_system(self):
        """Test the complete system"""
        print("\nTesting System Functionality...")
        
        try:
            # Test backend API
            response = requests.get('http://localhost:8000/api/current-data')
            if response.status_code == 200:
                data = response.json()
                print("  Backend API responding")
                print(f"  Data fields: {len(data)} parameters")
                
                # Check for ML model data
                if 'Pb_Concentrate' in data and 'Model_Info' in data:
                    print("  ML Model integrated")
                    print(f"  Model: {data.get('Model_Info', {}).get('model_name', 'N/A')}")
                    print(f"  Pb Concentrate: {data.get('Pb_Concentrate', 'N/A')}%")
                else:
                    print("  ML Model data not found")
            else:
                print("  Backend API not responding")
                return False
            
            # Test authentication service
            response = requests.get('http://localhost:8051/login')
            if response.status_code == 200:
                print("  Authentication service responding")
            else:
                print("  Authentication service not responding")
                return False
            
            # Test frontend
            response = requests.get('http://localhost:3000')
            if response.status_code == 200:
                print("  Frontend responding")
            else:
                print("  Frontend not responding")
                return False
            
            return True
            
        except Exception as e:
            print(f"  System test failed: {e}")
            return False
    
    def monitor_services(self):
        """Monitor running services"""
        print("\nSystem Status:")
        print("=" * 50)
        print("Press Ctrl+C to stop all services")
        print("=" * 50)
        
        while self.running:
            try:
                # Check backend
                backend_status = "Running" if self.backend_process and self.backend_process.poll() is None else "Stopped"
                auth_status = "Running" if self.auth_process and self.auth_process.poll() is None else "Stopped"
                frontend_status = "Running" if self.frontend_process and self.frontend_process.poll() is None else "Stopped"
                
                # Clear previous lines and show status
                print(f"\rBackend: {backend_status} | Auth: {auth_status} | Frontend: {frontend_status} | Press Ctrl+C to stop", end="", flush=True)
                
                time.sleep(5)
                
            except KeyboardInterrupt:
                print("\n")  # New line after status
                print("Shutting down all services...")
                self.stop_system()
                break
            except Exception as e:
                print(f"\nError in monitoring: {e}")
                break
    
    def stop_system(self):
        """Stop all services"""
        print("\nStopping System...")
        self.running = False
        
        # Terminate processes gracefully first
        if self.backend_process and self.backend_process.poll() is None:
            try:
                self.backend_process.terminate()
                print("  Backend process terminated")
            except Exception as e:
                print(f"  Error terminating backend: {e}")
        
        if self.auth_process and self.auth_process.poll() is None:
            try:
                self.auth_process.terminate()
                print("  Authentication service terminated")
            except Exception as e:
                print(f"  Error terminating auth service: {e}")
        
        if self.frontend_process and self.frontend_process.poll() is None:
            try:
                self.frontend_process.terminate()
                print("  Frontend process terminated")
            except Exception as e:
                print(f"  Error terminating frontend: {e}")
        
        # Wait a moment for graceful shutdown
        time.sleep(1)
        
        # Force kill if processes are still running
        if self.backend_process and self.backend_process.poll() is None:
            try:
                self.backend_process.kill()
                print("  Backend process force killed")
            except Exception as e:
                print(f"  Error force killing backend: {e}")
        
        if self.auth_process and self.auth_process.poll() is None:
            try:
                self.auth_process.kill()
                print("  Authentication service force killed")
            except Exception as e:
                print(f"  Error force killing auth service: {e}")
        
        if self.frontend_process and self.frontend_process.poll() is None:
            try:
                self.frontend_process.kill()
                print("  Frontend process force killed")
            except Exception as e:
                print(f"  Error force killing frontend: {e}")
        
        # Additional cleanup - kill any remaining processes by PID
        try:
            # Get current process and kill any child processes
            import psutil
            current_process = psutil.Process()
            children = current_process.children(recursive=True)
            for child in children:
                try:
                    child.terminate()
                except:
                    try:
                        child.kill()
                    except:
                        pass
        except ImportError:
            # psutil not available, use taskkill
            pass
        
        # Force kill any remaining Node.js processes
        try:
            subprocess.run(['taskkill', '/f', '/im', 'node.exe'], 
                         capture_output=True, text=True, shell=True)
            print("  Node.js processes terminated")
        except Exception as e:
            print(f"  Could not terminate Node.js processes: {e}")
        
        # Force kill any remaining Python processes related to our services
        try:
            # Kill all Python processes that might be running our services
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                         capture_output=True, text=True, shell=True)
            print("  All Python processes terminated")
        except Exception as e:
            print(f"  Could not terminate Python processes: {e}")
        
        # Also kill any remaining Node.js processes
        try:
            subprocess.run(['taskkill', '/f', '/im', 'node.exe'], 
                         capture_output=True, text=True, shell=True)
            print("  All Node.js processes terminated")
        except Exception as e:
            print(f"  Could not terminate Node.js processes: {e}")
        
        print("System shutdown complete")
    
    def cleanup_processes(self):
        """Clean up all Python and Node.js processes before starting"""
        print("\nCleaning up existing processes...")
        print("=" * 50)
        
        # Stop all Python processes
        print("Stopping all Python processes...")
        try:
            result = subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print("  All Python processes stopped")
            else:
                print("  No Python processes were running")
        except Exception as e:
            print(f"  Error stopping Python processes: {e}")
        
        # Stop all Node.js processes using PowerShell
        print("Stopping all Node.js processes...")
        try:
            result = subprocess.run(['powershell', '-Command', 'Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force'], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print("  All Node.js processes stopped")
            else:
                print("  No Node.js processes were running")
        except Exception as e:
            print(f"  Error stopping Node.js processes: {e}")
        
        # Wait for processes to terminate
        print("Waiting for processes to terminate...")
        time.sleep(3)
        print("Cleanup complete!")
    
    def run(self):
        """Main launch sequence"""
        try:
            self.print_banner()
            
            # Clean up processes first if requested
            if self.cleanup_first:
                self.cleanup_processes()
            
            # Start authentication service first
            if not self.start_auth_service():
                print("\nFailed to start authentication service. Check if port 8051 is available.")
                return False
            
            # Start backend
            if not self.start_backend():
                print("\nFailed to start backend. Check if port 8000 is available.")
                return False
            
            # Start frontend
            if not self.start_frontend():
                print("\nFailed to start frontend. Check if port 3000 is available.")
                return False
            
            # Wait for services
            if not self.wait_for_services():
                print("\nSome services failed to start. Check the error messages above.")
                print("\nTroubleshooting:")
                print("   1. Make sure no other processes are using ports 3000, 8000, or 8051")
                print("   2. Try running services individually to see specific errors")
                print("   3. Check if all dependencies are installed")
                return False
            
            # Test system
            if not self.test_system():
                print("\nSystem test failed. Some services may not be working properly.")
                return False
            
            print("\nSYSTEM LAUNCH COMPLETE!")
            print("=" * 70)
            print("Backend: FastAPI + WebSocket Server (Port 8000)")
            print("Authentication: Flask Auth Service (Port 8051)")
            print("Frontend: React Dashboard (Port 3000)")
            print("ML Model: Gradient Boosting Integration")
            print("Database: SQLite initialized")
            print("=" * 70)
            print("Dashboard: http://localhost:3000")
            print("API Documentation: http://localhost:8000/docs")
            print("Authentication: http://localhost:8051")
            print("Login Credentials:")
            print("   Username: LusangoM")
            print("   Password: admin")
            print("=" * 70)
            print("Status updates will appear below...")
            print("=" * 70)
            
            # Monitor services
            self.monitor_services()
            
        except KeyboardInterrupt:
            self.stop_system()
        except Exception as e:
            print(f"\nLaunch failed: {e}")
            self.stop_system()
            return False
        
        return True

def main():
    """Main function"""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Launch Froth Flotation Digital Twin System')
    parser.add_argument('--cleanup', action='store_true', 
                       help='Stop all Python and Node.js processes before launching')
    args = parser.parse_args()
    
    launcher = None
    try:
        launcher = FrothFlotationLauncher(cleanup_first=args.cleanup)
        success = launcher.run()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\nInterrupted by user. Shutting down...")
        if launcher:
            launcher.stop_system()
        # Force kill all Python processes
        try:
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                         capture_output=True, text=True, shell=True)
        except:
            pass
        return 0
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        if launcher:
            launcher.stop_system()
        return 1

if __name__ == "__main__":
    exit(main())
