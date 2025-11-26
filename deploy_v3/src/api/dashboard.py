"""
📊 Real-time Dashboard with Live Metrics
WebSocket-based real-time monitoring
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List, Dict
import asyncio
import json
from datetime import datetime
import random


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


# Dashboard HTML
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>🎯 Cyber Mirage - Live Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255,255,255,0.18);
        }
        .stat-value {
            font-size: 3em;
            font-weight: bold;
            text-align: center;
            margin: 10px 0;
        }
        .stat-label {
            text-align: center;
            opacity: 0.8;
            font-size: 1.1em;
        }
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
        }
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin: 5px;
        }
        .status.online { background: #10b981; }
        .status.warning { background: #f59e0b; }
        .status.error { background: #ef4444; }
        #attackLog {
            max-height: 400px;
            overflow-y: auto;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 15px;
        }
        .attack-entry {
            padding: 10px;
            margin: 5px 0;
            background: rgba(255,255,255,0.1);
            border-radius: 5px;
            border-left: 4px solid #ef4444;
        }
        .attack-time { opacity: 0.7; font-size: 0.9em; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .pulse { animation: pulse 2s infinite; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Cyber Mirage - Live Dashboard</h1>
        
        <div class="grid">
            <div class="card">
                <div class="stat-label">Total Attacks Detected</div>
                <div class="stat-value" id="totalAttacks">0</div>
                <span class="status online">LIVE</span>
            </div>
            
            <div class="card">
                <div class="stat-label">Active Sessions</div>
                <div class="stat-value" id="activeSessions">0</div>
                <span class="status online">ACTIVE</span>
            </div>
            
            <div class="card">
                <div class="stat-label">Detection Rate</div>
                <div class="stat-value" id="detectionRate">0%</div>
            </div>
            
            <div class="card">
                <div class="stat-label">Average Skill Level</div>
                <div class="stat-value" id="avgSkill">0%</div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card" style="grid-column: span 2;">
                <h3>📈 Attacks Over Time</h3>
                <div class="chart-container">
                    <canvas id="attacksChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h3>🎯 Attacker Types</h3>
                <div class="chart-container">
                    <canvas id="typesChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>🚨 Recent Attacks</h3>
            <div id="attackLog"></div>
        </div>
    </div>

    <script>
        // WebSocket connection
        const ws = new WebSocket(`ws://${window.location.host}/ws/dashboard`);
        
        // Initialize charts
        const attacksCtx = document.getElementById('attacksChart').getContext('2d');
        const attacksChart = new Chart(attacksCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Attacks',
                    data: [],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.1)' } },
                    x: { grid: { color: 'rgba(255,255,255,0.1)' } }
                },
                plugins: {
                    legend: { labels: { color: 'white' } }
                }
            }
        });
        
        const typesCtx = document.getElementById('typesChart').getContext('2d');
        const typesChart = new Chart(typesCtx, {
            type: 'doughnut',
            data: {
                labels: ['APT', 'Ransomware', 'Script Kiddie', 'Other'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: ['#ef4444', '#f59e0b', '#10b981', '#3b82f6']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: 'white' } }
                }
            }
        });
        
        // Handle WebSocket messages
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            // Update stats
            document.getElementById('totalAttacks').textContent = data.total_attacks || 0;
            document.getElementById('activeSessions').textContent = data.active_sessions || 0;
            document.getElementById('detectionRate').textContent = 
                (data.detection_rate || 0).toFixed(1) + '%';
            document.getElementById('avgSkill').textContent = 
                (data.avg_skill || 0).toFixed(1) + '%';
            
            // Update attacks chart
            if (data.attack_timeline) {
                attacksChart.data.labels = data.attack_timeline.labels;
                attacksChart.data.datasets[0].data = data.attack_timeline.data;
                attacksChart.update();
            }
            
            // Update types chart
            if (data.attacker_types) {
                typesChart.data.datasets[0].data = [
                    data.attacker_types.apt || 0,
                    data.attacker_types.ransomware || 0,
                    data.attacker_types.script_kiddie || 0,
                    data.attacker_types.other || 0
                ];
                typesChart.update();
            }
            
            // Update attack log
            if (data.recent_attack) {
                addAttackEntry(data.recent_attack);
            }
        };
        
        function addAttackEntry(attack) {
            const log = document.getElementById('attackLog');
            const entry = document.createElement('div');
            entry.className = 'attack-entry';
            entry.innerHTML = `
                <div><strong>🎯 ${attack.attacker}</strong> (${attack.skill}% skill)</div>
                <div>Origin: ${attack.origin} | Detected: ${attack.detected ? '✅' : '❌'}</div>
                <div class="attack-time">${new Date().toLocaleTimeString()}</div>
            `;
            log.insertBefore(entry, log.firstChild);
            
            // Keep only last 10 entries
            while (log.children.length > 10) {
                log.removeChild(log.lastChild);
            }
        }
        
        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
        
        ws.onclose = function() {
            console.log('WebSocket connection closed');
            setTimeout(() => location.reload(), 5000);
        };
    </script>
</body>
</html>
"""


def create_dashboard_app() -> FastAPI:
    """Create FastAPI app with real-time dashboard"""
    
    app = FastAPI(title="Cyber Mirage Dashboard")
    manager = ConnectionManager()
    
    @app.get("/")
    async def get_dashboard():
        """Serve dashboard HTML"""
        return HTMLResponse(content=DASHBOARD_HTML)
    
    @app.websocket("/ws/dashboard")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time updates"""
        await manager.connect(websocket)
        
        try:
            # Send initial data
            await websocket.send_json({
                "total_attacks": 0,
                "active_sessions": 0,
                "detection_rate": 0,
                "avg_skill": 0
            })
            
            # Keep connection alive and send updates
            while True:
                # Simulate data (replace with real data)
                data = {
                    "total_attacks": random.randint(100, 1000),
                    "active_sessions": random.randint(1, 10),
                    "detection_rate": random.uniform(60, 95),
                    "avg_skill": random.uniform(30, 80),
                    "attack_timeline": {
                        "labels": ["1m", "2m", "3m", "4m", "5m"],
                        "data": [random.randint(5, 50) for _ in range(5)]
                    },
                    "attacker_types": {
                        "apt": random.randint(10, 30),
                        "ransomware": random.randint(20, 40),
                        "script_kiddie": random.randint(30, 60),
                        "other": random.randint(10, 20)
                    },
                    "recent_attack": {
                        "attacker": random.choice(["APT28", "Lazarus", "Conti", "Script Kiddie"]),
                        "skill": random.randint(20, 95),
                        "origin": random.choice(["Russia", "China", "Iran", "Unknown"]),
                        "detected": random.choice([True, False])
                    }
                }
                
                await websocket.send_json(data)
                await asyncio.sleep(2)  # Update every 2 seconds
                
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    
    return app


# Run dashboard
if __name__ == "__main__":
    import uvicorn
    
    app = create_dashboard_app()
    
    print("🎯 Starting Real-time Dashboard...")
    print("📊 Access dashboard at: http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
