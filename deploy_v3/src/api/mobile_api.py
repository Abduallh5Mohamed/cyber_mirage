"""
📱 Mobile App API & Real-time Notifications
Monitor your honeypot from anywhere!
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import asyncio
import json


# Models
class AlertModel(BaseModel):
    """Alert model for API"""
    id: str
    timestamp: datetime
    severity: str
    attacker: str
    skill_level: float
    origin: str
    detected: bool
    message: str


class StatsModel(BaseModel):
    """Statistics model"""
    total_attacks: int
    detection_rate: float
    active_sessions: int
    top_attackers: List[dict]
    recent_alerts: List[AlertModel]


class NotificationModel(BaseModel):
    """Push notification model"""
    title: str
    body: str
    priority: str
    data: dict


# Create mobile API
mobile_api = FastAPI(
    title="Cyber Mirage Mobile API",
    description="Real-time honeypot monitoring API",
    version="1.0.0"
)

# Enable CORS for mobile apps
mobile_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify mobile app origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory storage (replace with real database)
alerts_db = []
stats_db = {
    'total_attacks': 0,
    'detection_rate': 0.0,
    'active_sessions': 0,
    'top_attackers': []
}
active_websockets = []


# API Endpoints
@mobile_api.get("/")
async def root():
    """API root"""
    return {
        "message": "Cyber Mirage Mobile API",
        "version": "1.0.0",
        "endpoints": {
            "stats": "/api/stats",
            "alerts": "/api/alerts",
            "notifications": "/api/notifications",
            "websocket": "/ws/live"
        }
    }


@mobile_api.get("/api/stats", response_model=StatsModel)
async def get_stats():
    """Get current statistics"""
    recent_alerts = alerts_db[-10:] if alerts_db else []
    
    return StatsModel(
        total_attacks=stats_db['total_attacks'],
        detection_rate=stats_db['detection_rate'],
        active_sessions=stats_db['active_sessions'],
        top_attackers=stats_db['top_attackers'],
        recent_alerts=recent_alerts
    )


@mobile_api.get("/api/alerts", response_model=List[AlertModel])
async def get_alerts(
    limit: int = 50,
    severity: Optional[str] = None,
    detected_only: bool = False
):
    """Get recent alerts with filters"""
    filtered_alerts = alerts_db
    
    # Filter by severity
    if severity:
        filtered_alerts = [
            a for a in filtered_alerts 
            if a.severity.lower() == severity.lower()
        ]
    
    # Filter by detection status
    if detected_only:
        filtered_alerts = [
            a for a in filtered_alerts
            if a.detected
        ]
    
    # Return most recent
    return filtered_alerts[-limit:]


@mobile_api.get("/api/alerts/{alert_id}", response_model=AlertModel)
async def get_alert(alert_id: str):
    """Get specific alert by ID"""
    alert = next((a for a in alerts_db if a.id == alert_id), None)
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return alert


@mobile_api.post("/api/alerts/acknowledge/{alert_id}")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""
    alert = next((a for a in alerts_db if a.id == alert_id), None)
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Mark as acknowledged (in real app, update database)
    return {
        "status": "success",
        "message": f"Alert {alert_id} acknowledged"
    }


@mobile_api.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket for real-time updates
    Mobile app connects here for live data
    """
    await websocket.accept()
    active_websockets.append(websocket)
    
    try:
        # Send initial data
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Cyber Mirage",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and send updates
        while True:
            # Wait for updates (in real app, this would be event-driven)
            await asyncio.sleep(5)
            
            # Send live stats
            await websocket.send_json({
                "type": "stats_update",
                "data": stats_db,
                "timestamp": datetime.now().isoformat()
            })
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    
    finally:
        active_websockets.remove(websocket)


@mobile_api.post("/api/notifications/register")
async def register_device(device_token: str, platform: str):
    """
    Register device for push notifications
    platform: 'ios' or 'android'
    """
    # In real app, save to database
    return {
        "status": "success",
        "message": "Device registered for notifications",
        "device_token": device_token,
        "platform": platform
    }


@mobile_api.get("/api/dashboard/metrics")
async def get_dashboard_metrics():
    """Get metrics for mobile dashboard"""
    return {
        "attacks_today": stats_db['total_attacks'],
        "detection_rate": stats_db['detection_rate'],
        "active_threats": len([a for a in alerts_db if a.severity in ['HIGH', 'CRITICAL']]),
        "system_health": "healthy",
        "uptime": "99.9%",
        "last_attack": alerts_db[-1].timestamp if alerts_db else None
    }


# Helper functions for sending notifications
async def send_push_notification(notification: NotificationModel):
    """
    Send push notification to registered devices
    (Integrate with FCM for Android, APNs for iOS)
    """
    print(f"📱 Sending push notification: {notification.title}")
    
    # In real app, send to FCM/APNs
    # Example payload:
    payload = {
        "notification": {
            "title": notification.title,
            "body": notification.body,
            "priority": notification.priority
        },
        "data": notification.data
    }
    
    # Send to all registered devices
    # fcm.send(payload)
    # apns.send(payload)
    
    return {"status": "sent"}


async def broadcast_to_websockets(message: dict):
    """Broadcast message to all connected WebSocket clients"""
    for ws in active_websockets:
        try:
            await ws.send_json(message)
        except:
            active_websockets.remove(ws)


# Example: React Native / Flutter Mobile App Structure
MOBILE_APP_EXAMPLE = """
📱 Mobile App Integration Guide
================================

1. React Native Example:

```javascript
// MobileApp.js
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, Alert } from 'react-native';

const CyberMirageApp = () => {
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    // Connect to API
    fetchStats();
    connectWebSocket();
    
    // Request notification permissions
    requestNotificationPermission();
  }, []);

  const fetchStats = async () => {
    const response = await fetch('https://api.cybermirage.com/api/stats');
    const data = await response.json();
    setStats(data);
  };

  const connectWebSocket = () => {
    const websocket = new WebSocket('wss://api.cybermirage.com/ws/live');
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'stats_update') {
        setStats(data.data);
      } else if (data.type === 'new_alert') {
        setAlerts(prev => [...prev, data.alert]);
        showPushNotification(data.alert);
      }
    };
    
    setWs(websocket);
  };

  const showPushNotification = (alert) => {
    Alert.alert(
      '🚨 New Attack Detected!',
      `${alert.attacker} - ${alert.severity}`,
      [{ text: 'View', onPress: () => navigateToAlert(alert) }]
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Cyber Mirage Monitor</Text>
      
      {stats && (
        <View style={styles.statsCard}>
          <Text>Total Attacks: {stats.total_attacks}</Text>
          <Text>Detection Rate: {stats.detection_rate}%</Text>
          <Text>Active Sessions: {stats.active_sessions}</Text>
        </View>
      )}
      
      <FlatList
        data={alerts}
        renderItem={({ item }) => (
          <AlertCard alert={item} />
        )}
      />
    </View>
  );
};
```

2. Flutter Example:

```dart
// main.dart
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';

class CyberMirageApp extends StatefulWidget {
  @override
  _CyberMirageAppState createState() => _CyberMirageAppState();
}

class _CyberMirageAppState extends State<CyberMirageApp> {
  Map<String, dynamic>? stats;
  List<dynamic> alerts = [];
  WebSocketChannel? channel;

  @override
  void initState() {
    super.initState();
    fetchStats();
    connectWebSocket();
  }

  Future<void> fetchStats() async {
    final response = await http.get(
      Uri.parse('https://api.cybermirage.com/api/stats')
    );
    
    if (response.statusCode == 200) {
      setState(() {
        stats = json.decode(response.body);
      });
    }
  }

  void connectWebSocket() {
    channel = WebSocketChannel.connect(
      Uri.parse('wss://api.cybermirage.com/ws/live')
    );
    
    channel!.stream.listen((message) {
      final data = json.decode(message);
      
      if (data['type'] == 'stats_update') {
        setState(() {
          stats = data['data'];
        });
      } else if (data['type'] == 'new_alert') {
        showNotification(data['alert']);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Cyber Mirage Monitor')),
      body: Column(
        children: [
          if (stats != null) StatsCard(stats: stats!),
          Expanded(
            child: ListView.builder(
              itemCount: alerts.length,
              itemBuilder: (context, index) {
                return AlertCard(alert: alerts[index]);
              },
            ),
          ),
        ],
      ),
    );
  }
}
```

3. Push Notifications Setup:

For Android (FCM):
- Add Firebase to your project
- Get server key from Firebase Console
- Use server key to send notifications from API

For iOS (APNs):
- Generate APNs certificate
- Configure in Apple Developer Portal
- Use certificate to send notifications from API

4. API Integration:

```javascript
// api.js
const API_BASE = 'https://api.cybermirage.com';

export const getStats = async () => {
  const response = await fetch(`${API_BASE}/api/stats`);
  return response.json();
};

export const getAlerts = async (limit = 50) => {
  const response = await fetch(`${API_BASE}/api/alerts?limit=${limit}`);
  return response.json();
};

export const acknowledgeAlert = async (alertId) => {
  const response = await fetch(
    `${API_BASE}/api/alerts/acknowledge/${alertId}`,
    { method: 'POST' }
  );
  return response.json();
};
```

5. UI Components:

- Dashboard: Real-time stats with charts
- Alert List: Scrollable list of attacks
- Alert Detail: Full attack information
- Settings: Notification preferences
- Profile: User management

Features:
✅ Real-time updates via WebSocket
✅ Push notifications for critical alerts
✅ Offline support with local caching
✅ Biometric authentication
✅ Dark mode support
✅ Customizable alert filters
"""


if __name__ == "__main__":
    print("📱 Mobile API Demo")
    print("="*80)
    print("\n🚀 Starting mobile API server...")
    print("📍 API URL: http://localhost:8001")
    print("🔌 WebSocket: ws://localhost:8001/ws/live")
    print("\n📱 Mobile App Integration:")
    print(MOBILE_APP_EXAMPLE)
    
    # Run with: uvicorn mobile_api:mobile_api --host 0.0.0.0 --port 8001
