from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel
from core_engine import engine
import json
import os

router = APIRouter()

class ChatRequest(BaseModel):
    agent_name: str
    message: str

class CreateAgentRequest(BaseModel):
    name: str
    patterns: str
    responses: str

class RawAgentRequest(BaseModel):
    name: str
    json_data: dict

@router.get("/api/agents")
async def get_agents():
    return {"agents": engine.get_agent_names()}

@router.post("/api/chat")
async def chat_with_agent(req: ChatRequest):
    response = engine.chat(req.agent_name, req.message)
    return {"response": response}

@router.post("/api/agents")
async def create_new_agent(req: CreateAgentRequest):
    pattern_list = [p.strip() for p in req.patterns.split(",") if p.strip()]
    response_list = [r.strip() for r in req.responses.split(",") if r.strip()]
    agent_id = engine.create_agent(req.name, pattern_list, response_list)
    return {"status": "success", "agent": agent_id}

@router.post("/api/agents/raw")
async def create_agent_raw(req: RawAgentRequest):
    clean_name = req.name.strip().replace(" ", "_")
    filepath = os.path.join('agents_data', f"{clean_name}.json")
    with open(filepath, "w") as f:
        json.dump(req.json_data, f, indent=4)
    engine.reload_agents()
    return {"status": "success", "agent": clean_name}

@router.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    content = await file.read()
    size_kb = round(len(content) / 1024, 2)
    return {"filename": file.filename, "size": size_kb, "status": "parsed"}

@router.post("/api/voice")
async def process_voice(audio: UploadFile = File(...)):
    content = await audio.read()
    size_kb = round(len(content) / 1024, 2)
    transcribed_text = f"Audio packet received ({size_kb} KB). Local STT engine offline."
    return {"text": transcribed_text, "status": "success"}
