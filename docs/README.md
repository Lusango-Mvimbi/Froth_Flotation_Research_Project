# ⚗️ Froth Flotation Digital Twin

A real-time industrial monitoring system for froth flotation processes using **React** and **WebSocket** technology.

## 🚀 Features

- **🔐 Secure Authentication**: Database-backed user login system
- **Real-time Data Updates**: WebSocket-powered live data streaming
- **Smooth Visualizations**: No page reloads or flickering
- **Interactive Controls**: Adjustable process parameters
- **Live Metrics**: Real-time Pb concentrate and recovery monitoring
- **Smart Recommendations**: AI-powered optimization suggestions
- **Professional UI**: Industrial-grade dashboard design
- **📊 Data Persistence**: SQLite database for historical data storage

## 📊 Dashboard Components

### Real-time Metrics
- **Pb Concentrate**: Lead concentration percentage
- **Recovery Rate**: Process recovery efficiency
- **pH Level**: Process pH monitoring
- **Air Flow**: Air flow rate in L/min

### Interactive Controls
- **KEX Flowrate**: Collector dosage control
- **SIPX Flowrate**: Frother dosage control
- **Air Flow**: Air flow rate adjustment
- **pH Control**: Process pH adjustment
- **Temperature**: Process temperature control
- **Cell Level**: Flotation cell level control

### Live Monitoring
- **Real-time Plot**: Continuous line chart with data history
- **WebSocket Status**: Live connection monitoring
- **Data Points**: Accumulating data visualization
- **Fullscreen Support**: Maintains view state

## 🛠️ Technology Stack

- **Frontend**: React.js with TypeScript
- **Real-time**: WebSocket communication
- **Backend**: FastAPI WebSocket server
- **Visualization**: Plotly interactive charts
- **Styling**: Bootstrap components
- **Data Processing**: Pandas & NumPy
- **Database**: SQLite with user authentication
- **Security**: SHA-256 password hashing & session management

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Froth_Flotation_Research_Project
   ```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the complete system with login**
   ```bash
   python launch_with_login.py
   ```

   Or run individual components:
```bash
   # Data server only
   python websocket_server.py
   
   # Login page only
   python login_page.py
   
   # Frontend only
   cd frontend && npm start
   ```

## 🔐 Authentication

The system includes a secure login system with the following features:

- **Default Admin User**: 
  - Contact your system administrator for login credentials
- **Password Security**: SHA-256 hashing
- **Session Management**: Secure session tokens with expiration
- **Database Storage**: User credentials stored in SQLite database

### Access Points:
- **Login Page**: http://localhost:3000/login
- **Dashboard**: http://localhost:3000/dashboard (requires authentication)
- **Data Server**: http://localhost:8000

## 🚀 Quick Start

### Option 1: Single Command Launcher
```bash
python start_system.py
```

### Option 2: Manual Start
```bash
# Terminal 1: Start WebSocket server
python websocket_server.py

# Terminal 2: Start Dash dashboard
python dash_dashboard.py
```

### Access the Dashboard
Open your browser and navigate to: **http://localhost:8050**

## 📁 Project Structure

```
Froth_Flotation_Research_Project/
├── dash_dashboard.py              # Main Dash application
├── websocket_server.py            # WebSocket data server
├── launch_dash_dashboard.py       # Launcher script
├── requirements.txt               # Python dependencies
├── Models/                        # ML models directory
│   └── rf_optimized_model.pkl     # Trained model
├── src/                           # Source code
│   ├── dashboard/                 # Dashboard components
│   ├── models/                    # Model utilities
│   └── utils/                     # Utility functions
└── docs/                          # Documentation
```

## 🔧 Configuration

### WebSocket Server
- **Port**: 8000
- **Data Rate**: 2-second intervals
- **Features**: Real-time data generation

### Dash Dashboard
- **Port**: 8050
- **Update Rate**: 2-second intervals
- **Data History**: Last 100 data points
- **Theme**: Bootstrap professional

## 📈 Real-time Features

### WebSocket Integration
- **Live Data Streaming**: Real-time process data
- **Connection Monitoring**: Live status indicators
- **Automatic Reconnection**: Robust connection handling
- **Data Buffering**: Smooth data accumulation

### Interactive Elements
- **Responsive Controls**: Real-time parameter adjustment
- **Live Recommendations**: Dynamic optimization suggestions
- **Smooth Updates**: No page refreshes required
- **State Preservation**: Maintains user interactions

## 🎯 Key Advantages

### Over Streamlit
- ✅ **No Page Reloads**: Smooth, flicker-free updates
- ✅ **Better Performance**: Native WebSocket support
- ✅ **Professional UI**: Bootstrap-based design
- ✅ **State Management**: Preserves user interactions
- ✅ **Real-time Updates**: True live data streaming

### Industrial Features
- 🔄 **Continuous Monitoring**: 24/7 process tracking
- 📊 **Data Visualization**: Professional charts
- 🎛️ **Process Control**: Interactive parameter adjustment
- 🎯 **Smart Alerts**: AI-powered recommendations
- 📱 **Responsive Design**: Works on all devices

## 🔍 Monitoring Features

### Real-time Metrics
- **Pb Concentrate**: 0-100% range with live updates
- **Recovery Rate**: Process efficiency monitoring
- **pH Level**: Critical process parameter
- **Air Flow**: Flow rate monitoring

### Process Controls
- **Reagent Dosage**: KEX and SIPX flowrate control
- **Process Parameters**: pH, temperature, cell level
- **Real-time Feedback**: Immediate parameter effects
- **Optimization**: AI-driven recommendations

## 🚨 Troubleshooting

### Common Issues

1. **Dashboard not loading**
   - Ensure WebSocket server is running on port 8000
   - Check if port 8050 is available
   - Verify all dependencies are installed

2. **No data updates**
   - Check WebSocket connection status
   - Verify server is generating data
   - Check browser console for errors

3. **Connection issues**
   - Restart WebSocket server
   - Check firewall settings
   - Verify network connectivity

### Debug Mode
Run with debug enabled:
```bash
python dash_dashboard.py
```

## 📊 Performance

- **Update Rate**: 2 seconds
- **Data Points**: 100 historical points
- **Memory Usage**: Optimized data structures
- **CPU Usage**: Minimal resource consumption
- **Network**: Efficient WebSocket protocol

## 🔮 Future Enhancements

- **3D Visualization**: Unity integration
- **Advanced Analytics**: Machine learning insights
- **Mobile App**: Native mobile dashboard
- **Cloud Integration**: Multi-site monitoring
- **Predictive Maintenance**: AI-powered alerts

## 📄 License

This project is part of the Froth Flotation Research Project.

## 🤝 Contributing

For research collaboration and contributions, please contact the project team.

---

**⚗️ Froth Flotation Digital Twin** - Real-time industrial monitoring with WebSocket technology
