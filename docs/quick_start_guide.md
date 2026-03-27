# Quick Start Guide

## Getting Started

This guide will help you get the Froth Flotation Digital Twin system up and running quickly.

## Prerequisites

### Required Software
- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **Node.js 16+**: [Download Node.js](https://nodejs.org/)
- **Git**: [Download Git](https://git-scm.com/)

### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 2GB free space
- **OS**: Windows 10+, macOS 10.15+, or Linux

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Froth_Flotation_Research_Project
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python --version
pip list | grep fastapi
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Verify installation
node --version
npm --version
```

## Quick Launch

### Option 1: Automated Launch (Recommended)
```bash
# From project root directory
python launch.py
```

This will:
- Start the backend API service
- Start the authentication service
- Start the frontend dashboard
- Open your browser to the login page

### Option 2: Manual Launch
```bash
# Terminal 1: Start Backend
cd backend
python services/flotation_data_service_refactored.py

# Terminal 2: Start Frontend
cd frontend
npm start
```

## Default Login Credentials (Development)

On first startup, the backend creates a default admin user automatically.

- Username: `admin`
- Password: `admin123`

Use these credentials at `http://localhost:3000` (or `http://localhost:8051/login` for the Flask login page).
For security, change this password after first login in any shared environment.

### Common Issues

#### Backend Won't Start
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for port conflicts
netstat -an | findstr :8000
```

#### Frontend Won't Start
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules
npm install

# Check Node.js version
node --version
```