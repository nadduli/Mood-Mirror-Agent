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

mood_agent = MoodMirrorAgent()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mood_mirror")

app = FastAPI(
    title="Mood Mirror A2A Agent",
    description="An AI agent that analyzes emotional tone and provides empathetic responses",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
        logger.info(f"Received A2A request with ID: {body.get('id')}")

        if body.get("jsonrpc") != "2.0" or "id" not in body:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": body.get("id", "unknown"),
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request: jsonrpc must be '2.0' and id is required",
                    },
                },
            )

        method = body.get("method")

        if method == "message/send":
            message_data = body["params"]["message"]
            result = await mood_agent.process_message(
                {"id": body["id"], "message": message_data}
            )
        elif method == "execute":
            messages = body["params"]["messages"]
            context_id = body["params"].get("contextId")
            result = await mood_agent.process_message(
                {
                    "id": body["id"],
                    "message": messages[-1] if messages else {},
                    "context_id": context_id,
                }
            )
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": body["id"],
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                },
            )

        response = A2AResponse(id=body["id"], result=result)

        logger.info(f"Successfully processed request {body['id']}")
        return response.dict()

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": body.get("id", "unknown") if "body" in locals() else "unknown",
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": {"details": str(e)},
                },
            },
        )


@app.get("/")
async def root():
    return {
        "message": "Mood Mirror A2A Agent",
        "status": "running",
        "version": "1.0.0",
        "telex_compatible": True,
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "mood_mirror"}


@app.get("/info")
async def agent_info():
    return {
        "name": mood_agent.name,
        "version": mood_agent.version,
        "capabilities": [
            "mood_analysis",
            "empathetic_responses",
            "emotional_mirroring",
        ],
        "endpoints": {"a2a": "/a2a/moodmirror", "health": "/health", "docs": "/docs"},
    }


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
            "authentication": "none",
        },
        "permissions": ["messages:read", "messages:write"],
        "tags": ["emotion", "ai", "wellness", "mental-health"],
    }


@app.get("/telex/manifest")
async def telex_manifest():
    """Alternative telex manifest endpoint"""
    return {
        "name": "mood-mirror-agent",
        "version": "1.0.0",
        "display_name": "Mood Mirror",
        "description": "AI agent that analyzes emotional tone and provides empathetic responses",
        "capabilities": ["emotional_analysis", "empathetic_responses"],
        "endpoints": {"a2a": "/a2a/moodmirror", "health": "/health"},
        "configuration": {"blocking": True, "timeout": 30000},
    }


@app.post("/telex/webhook")
async def telex_webhook(request: Request):
    """Handle telex.im webhook events"""
    try:
        event = await request.json()
        event_type = event.get("type")

        logger.info(f"Received telex webhook: {event_type}")

        if event_type == "skill.installed":
            logger.info(" Mood Mirror skill installed in telex.im!")
            return {"status": "success", "message": "Skill installed successfully"}
        elif event_type == "skill.uninstalled":
            logger.info("Mood Mirror skill uninstalled from telex.im")
            return {"status": "success", "message": "Skill uninstalled"}
        elif event_type == "ping":
            return {"status": "success", "message": "pong"}
        else:
            return {"status": "ignored", "event_type": event_type}

    except Exception as e:
        logger.error(f" Webhook error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
