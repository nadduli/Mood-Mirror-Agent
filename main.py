from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uuid
import logging
import json

from models.a2a_models import A2ARequest, A2AResponse
from agents.mood_mirror import MoodMirrorAgent

# Load environment variables
load_dotenv()

# Initialize agent
mood_agent = MoodMirrorAgent()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mood_mirror")

# Create FastAPI app
app = FastAPI(
    title="Mood Mirror A2A Agent",
    description="An AI agent that analyzes emotional tone and provides empathetic responses",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware - CRITICAL for A2A validation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including POST, OPTIONS
    allow_headers=["*"],  # Allow all headers
)

# FIX: Use @app.api_route to accept both POST and OPTIONS for CORS preflight
@app.api_route("/a2a/moodmirror", methods=["POST", "OPTIONS"])
async def mood_mirror_endpoint(request: Request):
    """Main A2A endpoint for Mood Mirror agent"""
    
    # Handle OPTIONS request for CORS preflight
    if request.method == "OPTIONS":
        return JSONResponse(
            content={"status": "ok"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    
    try:
        # Parse request body
        body = await request.json()
        logger.info(f"📨 Received A2A request with ID: {body.get('id')}")
        
        # Validate JSON-RPC 2.0
        if body.get("jsonrpc") != "2.0" or "id" not in body:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": body.get("id", "unknown"),
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request: jsonrpc must be '2.0' and id is required"
                    }
                },
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        # Process based on method
        method = body.get("method")
        
        if method == "message/send":
            message_data = body["params"]["message"]
            result = await mood_agent.process_message({
                "id": body["id"],
                "message": message_data
            })
        elif method == "execute":
            messages = body["params"]["messages"]
            context_id = body["params"].get("contextId")
            result = await mood_agent.process_message({
                "id": body["id"],
                "message": messages[-1] if messages else {},
                "context_id": context_id
            })
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": body["id"],
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                },
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        # Return A2A response
        response = A2AResponse(
            id=body["id"],
            result=result
        )
        
        logger.info(f"✅ Successfully processed request {body['id']}")
        return JSONResponse(
            content=response.dict(),
            headers={"Access-Control-Allow-Origin": "*"}
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": body.get("id", "unknown") if 'body' in locals() else "unknown",
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": {"details": str(e)}
                }
            },
            headers={"Access-Control-Allow-Origin": "*"}
        )

@app.get("/")
async def root():
    return {
        "message": "Mood Mirror A2A Agent", 
        "status": "running",
        "version": "1.0.0",
        "telex_compatible": True,
        "a2a_endpoint": "/a2a/moodmirror"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "agent": "mood_mirror",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/info")
async def agent_info():
    return {
        "name": mood_agent.name,
        "version": mood_agent.version,
        "capabilities": ["mood_analysis", "empathetic_responses", "emotional_mirroring"],
        "endpoints": {
            "a2a": "/a2a/moodmirror",
            "health": "/health",
            "docs": "/docs"
        },
        "a2a_protocol": "json-rpc-2.0"
    }

# Telex.im integration endpoints
@app.get("/.well-known/telex/skill.json")
async def telex_skill_manifest():
    """Telex.im skill discovery endpoint"""
    return {
        "name": "mood-mirror",
        "version": "1.0.0",
        "displayName": "Mood Mirror",
        "description": "Analyzes emotional tone and provides empathetic responses",
        "type": "a2a",
        "a2a": {
            "endpoint": "/a2a/moodmirror",
            "methods": ["message/send", "execute"],
            "authentication": "none"
        },
        "permissions": ["messages:read", "messages:write"],
        "tags": ["emotion", "ai", "wellness", "mental-health"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
