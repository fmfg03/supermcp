from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime

def add_health_endpoint(app: FastAPI):
    @app.get("/health")
    async def health_check():
        return JSONResponse({
            "status": "healthy",
            "service": "SuperMCP Voice System",
            "timestamp": datetime.now().isoformat(),
            "features": {
                "stt": "whisper",
                "tts": "elevenlabs+bark",
                "languages": ["es_mx", "en"],
                "monitoring": "langwatch"
            }
        })
    return app
