from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uuid

from models.a2a_models import A2ARequest, A2AResponse
from agents.mood_mirror import MoodMirrorAgent

load_dotenv()

mood_agent = MoodMirrorAgent()


app = FastAPI(
    title="Mood Mirror A2A Agent",
    description="An AI agent that analyzes emotional tone and provides empathetic responses",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/a2a/moodmirror")
async def mood_mirror_endpoint(request: Request):
    """Main A2A endpoint for Mood Mirror agent"""
    try:
        body = await request.json()
        
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
                }
            )
        
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
                }
            )
        
        response = A2AResponse(
            id=body["id"],
            result=result
        )
        
        return response.dict()
        
    except Exception as e:
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
            }
        )

@app.get("/")
async def root():
    return {
        "message": "Mood Mirror A2A Agent", 
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "mood_mirror"}

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
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Mood Mirror A2A Agent on {host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"❤️  A2A Endpoint: http://{host}:{port}/a2a/moodmirror")
    
    uvicorn.run(app, host=host, port=port)