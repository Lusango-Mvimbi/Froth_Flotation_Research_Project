# API Documentation

## Overview

This document provides comprehensive API documentation for the Froth Flotation Digital Twin system. All endpoints are RESTful and return JSON responses.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

The system uses JWT-based authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Core Endpoints

### Current Data
- **GET** `/api/current-data`
- **Description**: Get real-time flotation process data
- **Response**: Current sensor readings, calculated values, and process status

### Control Settings
- **GET** `/api/control-settings`
- **Description**: Get current control parameters (KEX, SIPX)
- **Response**: Current control settings

- **POST** `/api/control-settings`
- **Description**: Update control parameters
- **Body**: `{"kex": 60.0, "sipx": 30.0}`
- **Response**: Updated control settings

### Optimization
- **GET** `/api/optimization`
- **Description**: Get optimization recommendations
- **Response**: AI-generated recommendations for process improvement

### Future Predictions
- **GET** `/api/future-predictions`
- **Description**: Get multi-horizon predictions (5min, 15min, 30min, 60min)
- **Response**: Future predictions with confidence intervals

### Historical Data
- **GET** `/api/database/sensor-data`
- **Description**: Get historical sensor data
- **Parameters**: 
  - `start_date` (optional): YYYY-MM-DD format
  - `end_date` (optional): YYYY-MM-DD format
- **Response**: Historical data with timestamps

## Authentication Endpoints

### Login
- **POST** `/api/auth/login`
- **Description**: Authenticate user
- **Body**: `{"username": "operator", "password": "password"}`
- **Response**: JWT token and user information

### Logout
- **POST** `/api/auth/logout`
- **Description**: Logout user
- **Response**: Success confirmation

## WebSocket

### Real-time Updates
- **URL**: `ws://localhost:8000/ws`
- **Description**: Real-time data streaming
- **Message Format**: JSON with timestamp and data

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2025-09-17T10:30:00Z"
}
```

## Rate Limiting

- **Limit**: 120 requests per minute per IP
- **Headers**: 
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset time

## Examples

### Get Current Data
```bash
curl -X GET "http://localhost:8000/api/current-data" \
  -H "Authorization: Bearer <token>"
```

### Update Controls
```bash
curl -X POST "http://localhost:8000/api/control-settings" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"kex": 65.0, "sipx": 35.0}'
```

### Get Historical Data
```bash
curl -X GET "http://localhost:8000/api/database/sensor-data?start_date=2025-09-01&end_date=2025-09-17" \
  -H "Authorization: Bearer <token>"
```
