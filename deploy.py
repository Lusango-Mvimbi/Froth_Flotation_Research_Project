#!/usr/bin/env python3
"""
Automated Deployment Pipeline
============================

Handles complete system deployment with rollback capabilities.
"""

import os
import sys
import shutil
import subprocess
import json
import datetime
from pathlib import Path
import logging

class DeploymentPipeline:
    def __init__(self, config_file='deployment_config.json'):
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.deployment_id = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def setup_logging(self):
        """Setup deployment logging."""
        log_dir = Path('logs/deployments')
        log_dir.mkdir(exist_ok=True, parents=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f'deployment_{self.deployment_id}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self, config_file):
        """Load deployment configuration."""
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                "environment": "production",
                "backup_retention_days": 30,
                "health_check_timeout": 30,
                "services": {
                    "backend": {"port": 8000, "health_endpoint": "/docs"},
                    "auth": {"port": 8051, "health_endpoint": "/"},
                    "frontend": {"port": 3000, "health_endpoint": "/"}
                }
            }
    
    def create_backup(self):
        """Create backup of current deployment."""
        self.logger.info("Creating system backup...")
        
        backup_dir = Path(f'backups/backup_{self.deployment_id}')
        backup_dir.mkdir(exist_ok=True, parents=True)
        
        # Backup critical directories
        critical_dirs = [
            'backend/services',
            'backend/trained_models', 
            'frontend/build',
            'logs'
        ]
        
        for dir_path in critical_dirs:
            if os.path.exists(dir_path):
                dest_path = backup_dir / dir_path
                dest_path.parent.mkdir(exist_ok=True, parents=True)
                if os.path.isdir(dir_path):
                    shutil.copytree(dir_path, dest_path)
                else:
                    shutil.copy2(dir_path, dest_path)
                self.logger.info(f"Backed up {dir_path}")
        
        self.logger.info(f"Backup created at {backup_dir}")
        return backup_dir
    
    def deploy_models(self, models_source_dir):
        """Deploy new ML models."""
        self.logger.info("Deploying ML models...")
        
        models_dir = Path('backend/trained_models')
        
        # Validate model files exist
        required_files = [
            '5min/rf_model.pkl',
            '60min/rf_model.pkl', 
            'model_metadata.pkl'
        ]
        
        for file_path in required_files:
            full_path = Path(models_source_dir) / file_path
            if not full_path.exists():
                raise FileNotFoundError(f"Required model file not found: {full_path}")
        
        # Deploy models
        if models_dir.exists():
            shutil.rmtree(models_dir)
        shutil.copytree(models_source_dir, models_dir)
        
        self.logger.info("ML models deployed successfully")
        
    def install_dependencies(self):
        """Install/update system dependencies."""
        self.logger.info("Installing dependencies...")
        
        # Backend dependencies
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                         check=True, capture_output=True)
            self.logger.info("Backend dependencies installed")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install backend dependencies: {e}")
            raise
        
        # Frontend dependencies
        frontend_dir = Path('frontend')
        if frontend_dir.exists():
            try:
                subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True, capture_output=True)
                self.logger.info("Frontend dependencies installed")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to install frontend dependencies: {e}")
                raise
    
    def build_frontend(self):
        """Build frontend for production."""
        self.logger.info("Building frontend...")
        
        frontend_dir = Path('frontend')
        if frontend_dir.exists():
            try:
                subprocess.run(['npm', 'run', 'build'], cwd=frontend_dir, check=True, capture_output=True)
                self.logger.info("Frontend built successfully")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Frontend build failed: {e}")
                raise
    
    def start_services(self):
        """Start all system services."""
        self.logger.info("Starting services...")
        
        # Use the launch script to start services
        try:
            # Note: In production, you might want to use a process manager like systemd
            self.logger.info("Services should be started using the launch script or process manager")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start services: {e}")
            return False
    
    def health_check(self):
        """Perform comprehensive health checks."""
        self.logger.info("Performing health checks...")
        
        import requests
        import time
        
        services = self.config['services']
        timeout = self.config.get('health_check_timeout', 30)
        
        for service_name, service_config in services.items():
            port = service_config['port']
            endpoint = service_config['health_endpoint']
            url = f"http://localhost:{port}{endpoint}"
            
            self.logger.info(f"Checking {service_name} at {url}")
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        self.logger.info(f"✅ {service_name} is healthy")
                        break
                except requests.RequestException:
                    pass
                time.sleep(2)
            else:
                self.logger.error(f"❌ {service_name} failed health check")
                return False
        
        # Additional prediction service checks
        return self.check_prediction_services()
    
    def check_prediction_services(self):
        """Check prediction services specifically."""
        self.logger.info("Checking prediction services...")
        
        import requests
        
        try:
            # Test future predictions
            response = requests.get("http://localhost:8000/api/future-predictions", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'future_predictions' in data:
                    self.logger.info("✅ Future prediction service operational")
                    
                    # Test additional endpoints
                    endpoints = [
                        "/api/prediction-info",
                        "/api/predictive-alerts"
                    ]
                    
                    for endpoint in endpoints:
                        try:
                            resp = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
                            if resp.status_code == 200:
                                self.logger.info(f"✅ {endpoint} operational")
                            else:
                                self.logger.warning(f"⚠️ {endpoint} returned {resp.status_code}")
                        except:
                            self.logger.warning(f"⚠️ {endpoint} not responding")
                    
                    return True
                else:
                    self.logger.error("❌ Future predictions not available")
                    return False
            else:
                self.logger.error(f"❌ Prediction service returned {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Prediction service check failed: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Remove old backups based on retention policy."""
        self.logger.info("Cleaning up old backups...")
        
        backup_dir = Path('backups')
        if not backup_dir.exists():
            return
        
        retention_days = self.config.get('backup_retention_days', 30)
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
        
        for backup_folder in backup_dir.iterdir():
            if backup_folder.is_dir() and backup_folder.name.startswith('backup_'):
                try:
                    # Extract date from folder name
                    date_str = backup_folder.name.split('_')[1]
                    backup_date = datetime.datetime.strptime(date_str, '%Y%m%d')
                    
                    if backup_date < cutoff_date:
                        shutil.rmtree(backup_folder)
                        self.logger.info(f"Removed old backup: {backup_folder.name}")
                except:
                    pass  # Skip folders that don't match expected format
    
    def deploy(self, models_source_dir=None):
        """Execute complete deployment pipeline."""
        self.logger.info(f"Starting deployment {self.deployment_id}")
        
        try:
            # Step 1: Create backup
            backup_dir = self.create_backup()
            
            # Step 2: Install dependencies
            self.install_dependencies()
            
            # Step 3: Deploy models (if provided)
            if models_source_dir:
                self.deploy_models(models_source_dir)
            
            # Step 4: Build frontend
            self.build_frontend()
            
            # Step 5: Start services
            if not self.start_services():
                raise Exception("Failed to start services")
            
            # Step 6: Health checks
            if not self.health_check():
                raise Exception("Health checks failed")
            
            # Step 7: Cleanup
            self.cleanup_old_backups()
            
            self.logger.info(f"✅ Deployment {self.deployment_id} completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Deployment {self.deployment_id} failed: {e}")
            self.logger.info("Consider rolling back to previous version")
            return False
    
    def rollback(self, backup_id):
        """Rollback to a previous backup."""
        self.logger.info(f"Rolling back to backup {backup_id}")
        
        backup_dir = Path(f'backups/backup_{backup_id}')
        if not backup_dir.exists():
            raise FileNotFoundError(f"Backup {backup_id} not found")
        
        try:
            # Restore critical directories
            critical_dirs = [
                'backend/services',
                'backend/trained_models',
                'frontend/build'
            ]
            
            for dir_path in critical_dirs:
                backup_path = backup_dir / dir_path
                if backup_path.exists():
                    if os.path.exists(dir_path):
                        if os.path.isdir(dir_path):
                            shutil.rmtree(dir_path)
                        else:
                            os.remove(dir_path)
                    
                    if backup_path.is_dir():
                        shutil.copytree(backup_path, dir_path)
                    else:
                        shutil.copy2(backup_path, dir_path)
                    
                    self.logger.info(f"Restored {dir_path}")
            
            self.logger.info(f"✅ Rollback to {backup_id} completed")
            self.logger.info("Restart services to complete rollback")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Rollback failed: {e}")
            return False
    
    def list_backups(self):
        """List available backups."""
        backup_dir = Path('backups')
        if not backup_dir.exists():
            print("No backups directory found")
            return []
        
        backups = []
        for backup_folder in backup_dir.iterdir():
            if backup_folder.is_dir() and backup_folder.name.startswith('backup_'):
                backup_id = backup_folder.name.replace('backup_', '')
                try:
                    # Parse date from backup ID
                    date_str = backup_id.split('_')[0]
                    time_str = backup_id.split('_')[1]
                    backup_date = datetime.datetime.strptime(f"{date_str}_{time_str}", '%Y%m%d_%H%M%S')
                    
                    backups.append({
                        'id': backup_id,
                        'date': backup_date,
                        'path': backup_folder
                    })
                except:
                    pass
        
        # Sort by date (newest first)
        backups.sort(key=lambda x: x['date'], reverse=True)
        
        print("Available backups:")
        for backup in backups:
            print(f"  {backup['id']} - {backup['date'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        return backups

def main():
    """Main deployment entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deployment Pipeline')
    parser.add_argument('action', choices=['deploy', 'rollback', 'list-backups'], help='Action to perform')
    parser.add_argument('--models-dir', help='Directory containing new models to deploy')
    parser.add_argument('--backup-id', help='Backup ID to rollback to')
    parser.add_argument('--config', default='deployment_config.json', help='Configuration file')
    
    args = parser.parse_args()
    
    pipeline = DeploymentPipeline(args.config)
    
    if args.action == 'deploy':
        success = pipeline.deploy(args.models_dir)
        sys.exit(0 if success else 1)
    elif args.action == 'rollback':
        if not args.backup_id:
            print("Error: --backup-id required for rollback")
            sys.exit(1)
        success = pipeline.rollback(args.backup_id)
        sys.exit(0 if success else 1)
    elif args.action == 'list-backups':
        pipeline.list_backups()
        sys.exit(0)

if __name__ == "__main__":
    main()
