#!/usr/bin/env python3
"""
AI Engine Server - Neural Deception & Multi-Agent Intelligence
Serves ML models for attack prediction and adaptive deception
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/logs/ai_engine.log')
    ]
)
logger = logging.getLogger(__name__)

# Environment configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', 'changeme123')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'cyber_mirage')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'cybermirage')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'SecurePass123!')

class AIEngineServer:
    """Main AI Engine Server"""
    
    def __init__(self):
        self.running = False
        self.redis_client = None
        self.db_connection = None
        logger.info("AI Engine Server initialized")
    
    async def connect_redis(self):
        """Connect to Redis"""
        try:
            import redis.asyncio as aioredis
            self.redis_client = await aioredis.from_url(
                f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}",
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return False
    
    async def connect_database(self):
        """Connect to PostgreSQL"""
        try:
            import asyncpg
            self.db_connection = await asyncpg.connect(
                host=POSTGRES_HOST,
                database=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD
            )
            logger.info(f"Connected to PostgreSQL at {POSTGRES_HOST}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            return False
    
    async def process_attack_event(self, event: Dict):
        """Process incoming attack event with ML prediction"""
        try:
            # Increment attack counter for metrics
            if hasattr(self, 'attack_count'):
                self.attack_count += 1
            
            # Simple threat scoring (placeholder for real ML model)
            threat_score = 0.5
            
            # Extract features
            source_ip = event.get('source_ip', 'unknown')
            attack_type = event.get('attack_type', 'unknown')
            
            # Update threat intelligence
            if self.redis_client:
                key = f"threat:{source_ip}"
                await self.redis_client.hincrby(key, 'count', 1)
                await self.redis_client.hset(key, 'last_seen', datetime.utcnow().isoformat())
                await self.redis_client.expire(key, 86400)  # 24 hours
            
            logger.info(f"Processed attack from {source_ip} - Type: {attack_type} - Score: {threat_score}")
            return threat_score
        
        except Exception as e:
            logger.error(f"Error processing attack event: {e}")
            if hasattr(self, 'redis_errors'):
                self.redis_errors += 1
            return 0.0
    
    async def monitor_attacks(self):
        """Monitor attack queue from Redis"""
        logger.info("Starting attack monitoring...")
        
        while self.running:
            try:
                if self.redis_client:
                    # Check for new attacks in queue
                    attack_data = await self.redis_client.lpop('attack_queue')
                    
                    if attack_data:
                        import json
                        event = json.loads(attack_data)
                        await self.process_attack_event(event)
                    else:
                        await asyncio.sleep(1)
                else:
                    await asyncio.sleep(5)
                    
            except Exception as e:
                logger.error(f"Error in attack monitoring: {e}")
                await asyncio.sleep(5)
    
    async def health_check_server(self):
        """HTTP server with health check and Prometheus metrics"""
        try:
            from aiohttp import web
            
            # Metrics counters
            self.attack_count = 0
            self.redis_errors = 0
            self.db_errors = 0
            
            async def health(request):
                status = {
                    'status': 'healthy',
                    'redis': self.redis_client is not None,
                    'database': self.db_connection is not None,
                    'timestamp': datetime.utcnow().isoformat()
                }
                return web.json_response(status)
            
            async def metrics(request):
                """Prometheus-compatible metrics endpoint"""
                metrics_text = f"""# HELP ai_engine_attacks_total Total number of processed attacks
# TYPE ai_engine_attacks_total counter
ai_engine_attacks_total {self.attack_count}

# HELP ai_engine_redis_errors_total Total Redis errors
# TYPE ai_engine_redis_errors_total counter
ai_engine_redis_errors_total {self.redis_errors}

# HELP ai_engine_db_errors_total Total database errors
# TYPE ai_engine_db_errors_total counter
ai_engine_db_errors_total {self.db_errors}

# HELP ai_engine_redis_connected Redis connection status (1=connected, 0=disconnected)
# TYPE ai_engine_redis_connected gauge
ai_engine_redis_connected {1 if self.redis_client else 0}

# HELP ai_engine_db_connected Database connection status (1=connected, 0=disconnected)
# TYPE ai_engine_db_connected gauge
ai_engine_db_connected {1 if self.db_connection else 0}
"""
                return web.Response(text=metrics_text, content_type='text/plain')
            
            app = web.Application()
            app.router.add_get('/health', health)
            app.router.add_get('/metrics', metrics)
            
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', 8001)
            await site.start()
            
            logger.info("Health check and metrics server started on port 8001")
            
            while self.running:
                await asyncio.sleep(10)
                
        except Exception as e:
            logger.error(f"Health check server error: {e}")
    
    async def run(self):
        """Main server loop"""
        self.running = True
        logger.info("Starting AI Engine Server...")
        
        # Connect to services
        await self.connect_redis()
        await self.connect_database()
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self.monitor_attacks()),
            asyncio.create_task(self.health_check_server())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Shutting down AI Engine Server...")
            self.running = False
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            self.running = False
        finally:
            # Cleanup
            if self.redis_client:
                await self.redis_client.close()
            if self.db_connection:
                await self.db_connection.close()

async def main():
    """Entry point"""
    logger.info("=" * 60)
    logger.info("Cyber Mirage AI Engine Server v5.0")
    logger.info("Neural Deception & Multi-Agent Intelligence")
    logger.info("=" * 60)
    
    server = AIEngineServer()
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
