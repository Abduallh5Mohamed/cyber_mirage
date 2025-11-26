"""
🚀 FastAPI Production Server with Monitoring
Full production-ready API with security, monitoring, and error handling
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from contextlib import asynccontextmanager
import structlog
import time
import sys
import os
from typing import Optional
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.environment.comprehensive_env import ComprehensiveHoneynetEnv
from stable_baselines3 import PPO
import numpy as np

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics - Initialize only once
REQUEST_COUNT = None
REQUEST_DURATION = None
ATTACK_DETECTED = None
ATTACK_DURATION = None
MODEL_INFERENCE = None
ERRORS_TOTAL = None

def init_metrics():
    """Initialize metrics only if not already initialized"""
    global REQUEST_COUNT, REQUEST_DURATION, ATTACK_DETECTED, ATTACK_DURATION, MODEL_INFERENCE, ERRORS_TOTAL
    
    if REQUEST_COUNT is None:
        try:
            REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
            REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
            ATTACK_DETECTED = Counter('attacks_detected_total', 'Total attacks detected', ['attacker_type'])
            ATTACK_DURATION = Histogram('attack_duration_seconds', 'Attack session duration', ['attacker_type'])
            MODEL_INFERENCE = Histogram('model_inference_seconds', 'Model inference time')
            ERRORS_TOTAL = Counter('errors_total', 'Total errors', ['error_type'])
        except Exception as e:
            logger.error(f"Metrics already initialized: {e}")

# Global state
app_state = {
    "model": None,
    "env": None,
    "startup_time": None
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Cyber Mirage API...")
    app_state["startup_time"] = time.time()
    
    # Initialize metrics
    init_metrics()
    
    try:
        # Load environment
        logger.info("Loading environment...")
        app_state["env"] = ComprehensiveHoneynetEnv()
        logger.info("✅ Environment loaded", attacker_types=len(app_state["env"].ATTACKER_PROFILES))
        
        # Load model (if exists)
        model_path = "data/models/ppo_comprehensive_final.zip"
        if os.path.exists(model_path):
            logger.info("Loading trained model...", path=model_path)
            app_state["model"] = PPO.load(model_path, env=app_state["env"])
            logger.info("✅ Model loaded successfully")
        else:
            logger.warning("⚠️  No trained model found, using random policy", path=model_path)
        
        logger.info("✅ Cyber Mirage API started successfully")
        
    except Exception as e:
        logger.error("❌ Failed to start application", error=str(e), traceback=traceback.format_exc())
        ERRORS_TOTAL.labels(error_type="startup_error").inc()
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Cyber Mirage API...")
    app_state.clear()
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Cyber Mirage API",
    description="AI-Powered Adaptive Honeypot System",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")
    
    logger.info(
        "Request started",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else "unknown"
    )
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        logger.info(
            "Request completed",
            request_id=request_id,
            status_code=response.status_code,
            duration=f"{duration:.3f}s"
        )
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration:.3f}"
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            "Request failed",
            request_id=request_id,
            error=str(e),
            duration=f"{duration:.3f}s",
            traceback=traceback.format_exc()
        )
        ERRORS_TOTAL.labels(error_type="request_error").inc()
        raise


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    ERRORS_TOTAL.labels(error_type=f"http_{exc.status_code}").inc()
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        path=str(request.url),
        traceback=traceback.format_exc()
    )
    ERRORS_TOTAL.labels(error_type="unhandled_exception").inc()
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": str(request.url)
        }
    )


# Health check
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    try:
        env_ok = app_state.get("env") is not None
        model_ok = app_state.get("model") is not None
        uptime = time.time() - app_state.get("startup_time", time.time())
        
        status = "healthy" if env_ok else "degraded"
        
        return {
            "status": status,
            "uptime_seconds": uptime,
            "environment_loaded": env_ok,
            "model_loaded": model_ok,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        ERRORS_TOTAL.labels(error_type="health_check_error").inc()
        raise HTTPException(status_code=503, detail="Service unavailable")


# Readiness check
@app.get("/ready", tags=["System"])
async def readiness_check():
    """Readiness check for Kubernetes"""
    if app_state.get("env") is None:
        raise HTTPException(status_code=503, detail="Environment not ready")
    
    return {"status": "ready"}


# Metrics endpoint
@app.get("/metrics", tags=["System"])
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


# API endpoints
@app.get("/", tags=["Info"])
async def root():
    """API information"""
    return {
        "name": "Cyber Mirage API",
        "version": "1.0.0",
        "description": "AI-Powered Adaptive Honeypot System",
        "attacker_types": len(app_state["env"].ATTACKER_PROFILES) if app_state.get("env") else 0,
        "model_loaded": app_state.get("model") is not None
    }


@app.get("/attackers", tags=["Intelligence"])
async def list_attackers():
    """List all attacker profiles"""
    try:
        if not app_state.get("env"):
            raise HTTPException(status_code=503, detail="Environment not loaded")
        
        attackers = []
        for name, profile in app_state["env"].ATTACKER_PROFILES.items():
            attackers.append({
                "name": name,
                "skill": profile["skill"],
                "stealth": profile["stealth"],
                "persistence": profile["persistence"],
                "origin": profile["origin"],
                "description": profile.get("desc", "")
            })
        
        return {
            "total": len(attackers),
            "attackers": sorted(attackers, key=lambda x: x["skill"], reverse=True)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to list attackers", error=str(e))
        ERRORS_TOTAL.labels(error_type="list_attackers_error").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/simulate", tags=["Simulation"])
async def simulate_attack(attacker_name: Optional[str] = None, max_steps: int = 100):
    """Simulate an attack"""
    start_time = time.time()
    
    try:
        if not app_state.get("env"):
            raise HTTPException(status_code=503, detail="Environment not loaded")
        
        env = app_state["env"]
        model = app_state.get("model")
        
        # Reset environment
        obs, info = env.reset()
        
        # Force specific attacker if requested
        if attacker_name:
            if attacker_name not in env.ATTACKER_PROFILES:
                raise HTTPException(status_code=404, detail=f"Attacker '{attacker_name}' not found")
            env.current_attacker = attacker_name
            profile = env.ATTACKER_PROFILES[attacker_name]
            env.attacker_skill = profile["skill"]
            env.attacker_stealth = profile["stealth"]
            env.attacker_persistence = profile["persistence"]
        
        # Run simulation
        total_reward = 0
        steps = 0
        done = False
        
        while not done and steps < max_steps:
            # Get action
            if model:
                inference_start = time.time()
                action, _ = model.predict(obs, deterministic=True)
                MODEL_INFERENCE.observe(time.time() - inference_start)
            else:
                action = env.action_space.sample()
            
            # Step
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            steps += 1
            done = terminated or truncated
        
        duration = time.time() - start_time
        
        # Metrics
        ATTACK_DETECTED.labels(attacker_type=info['attacker']).inc()
        ATTACK_DURATION.labels(attacker_type=info['attacker']).observe(duration)
        
        logger.info(
            "Simulation completed",
            attacker=info['attacker'],
            skill=info['skill'],
            steps=steps,
            reward=total_reward,
            detected=info['detected']
        )
        
        return {
            "attacker": info['attacker'],
            "skill": info['skill'],
            "origin": info['origin'],
            "description": info['description'],
            "steps": steps,
            "total_reward": float(total_reward),
            "detected": info['detected'],
            "data_collected": float(obs[2]),
            "suspicion": float(obs[1]),
            "mitre_tactics": info['mitre_tactics'],
            "zero_days": int(obs[10]),
            "duration_seconds": duration
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Simulation failed", error=str(e), traceback=traceback.format_exc())
        ERRORS_TOTAL.labels(error_type="simulation_error").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", tags=["Statistics"])
async def get_statistics():
    """Get system statistics"""
    try:
        if not app_state.get("env"):
            raise HTTPException(status_code=503, detail="Environment not loaded")
        
        env = app_state["env"]
        
        # Calculate stats
        profiles = env.ATTACKER_PROFILES
        skills = [p["skill"] for p in profiles.values()]
        
        return {
            "total_attackers": len(profiles),
            "skill_distribution": {
                "min": float(min(skills)),
                "max": float(max(skills)),
                "mean": float(np.mean(skills)),
                "median": float(np.median(skills))
            },
            "model_loaded": app_state.get("model") is not None,
            "uptime_seconds": time.time() - app_state.get("startup_time", time.time())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get statistics", error=str(e))
        ERRORS_TOTAL.labels(error_type="stats_error").inc()
        raise HTTPException(status_code=500, detail=str(e))


# Run server
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
        access_log=True,
        reload=False,  # Set to True for development
        workers=1  # Use single worker to avoid metric duplication
    )
