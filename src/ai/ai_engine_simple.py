#!/usr/bin/env python3
"""
Lightweight AI Engine Server - Basic async version
Works with minimal dependencies
"""

import os
import sys
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Environment
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')

class SimpleAIEngine:
    def __init__(self):
        self.running = False
        self.attack_count = 0
        logger.info("Simple AI Engine initialized")
    
    async def process_event(self, event: Dict):
        """Basic event processing"""
        self.attack_count += 1
        source_ip = event.get('source_ip', 'unknown')
        logger.info(f"Processed attack #{self.attack_count} from {source_ip}")
    
    async def health_server(self):
        """Simple HTTP health check"""
        try:
            # Use http.server for simplicity
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import threading
            
            class HealthHandler(BaseHTTPRequestHandler):
                server_instance = self
                
                def do_GET(self):
                    if self.path == '/health':
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        status = {
                            'status': 'healthy',
                            'attacks_processed': self.server.server_instance.attack_count,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        self.wfile.write(json.dumps(status).encode())
                    elif self.path == '/metrics':
                        self.send_response(200)
                        self.send_header('Content-type', 'text/plain')
                        self.end_headers()
                        metrics = f"""ai_engine_attacks_total {self.server.server_instance.attack_count}
ai_engine_status 1
"""
                        self.wfile.write(metrics.encode())
                    else:
                        self.send_response(404)
                        self.end_headers()
                
                def log_message(self, format, *args):
                    pass  # Suppress default logging
            
            def run_server():
                httpd = HTTPServer(('0.0.0.0', 8001), HealthHandler)
                httpd.server_instance = self
                logger.info("Health server started on port 8001")
                httpd.serve_forever()
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            while self.running:
                await asyncio.sleep(10)
                
        except Exception as e:
            logger.error(f"Health server error: {e}")
    
    async def run(self):
        """Main loop"""
        self.running = True
        logger.info("=" * 60)
        logger.info("Cyber Mirage Simple AI Engine v5.0")
        logger.info(f"Redis: {REDIS_HOST}:{REDIS_PORT}")
        logger.info(f"PostgreSQL: {POSTGRES_HOST}")
        logger.info("=" * 60)
        
        try:
            await self.health_server()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.running = False

async def main():
    engine = SimpleAIEngine()
    await engine.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        sys.exit(1)
