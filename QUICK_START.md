# Froth Flotation Digital Twin - Quick Start

## 🚀 Launch the System

### Option 1: Simple Launch (Recommended)
```bash
# Double-click this file or run:
launch.bat
```

### Option 2: Python Launch
```bash
python launch.py
```

### Option 3: Clean Launch (Stops all processes first)
```bash
scripts\launch_clean.bat
```

## 🛑 Stop All Processes
```bash
scripts\stop_all.bat
```

## 📁 Project Structure

```
Froth_Flotation_Research_Project/
├── launch.bat              # Main launcher (double-click to start)
├── launch.py               # Main Python launcher
├── QUICK_START.md          # This guide
├── scripts/                # All launcher scripts
│   ├── launch_froth_flotation_system.py  # Main system launcher
│   ├── launch_clean.bat    # Clean launch (stops processes first)
│   └── stop_all.bat        # Stop all processes
├── backend/                # Backend services (FastAPI)
│   ├── services/           # Core services
│   ├── models/             # Database models
│   └── utils/              # Utilities
├── frontend/               # React dashboard
│   └── src/                # Source code
├── data/                   # Data files
├── logs/                   # System logs
├── docs/                   # Documentation
└── tests/                  # Test files
```

## 🔐 Login Credentials
- **Username**: LusangoM
- **Password**: admin

## 🌐 Access Points
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Login Page**: http://localhost:8051

## 📝 Notes
- The system starts with the login page first
- You must authenticate before accessing the dashboard
- All services start automatically in the correct order
