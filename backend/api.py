"""
api.py
======
REST API route definitions for Agent Smith.

Endpoints:
  GET  /api/agents            — List all loaded agent names.
  GET  /api/agents/{name}     — Inspect a specific agent (memory + status).
  POST /api/agents            — Create an agent via form input.
  POST /api/agents/raw        — Create an agent via raw JSON upload.
  DELETE /api/agents/{name}   — Delete an agent and its data file.
  POST /api/chat              — Send a message to a named agent.
  POST /api/upload            — Upload a document (PDF / TXT / DOCX) for context.
  DELETE /api/context         — Clear the active document context.
  POST /api/voice             — Upload audio; returns transcription placeholder.
  GET  /api/health            — (Internal) Liveness probe.
"""

import io
import json
import logging
import os
import re

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, field_validator

from core_engine import AGENTS_DIR, engine

logger = logging.getLogger("AgentSmith.API")
router = APIRouter()

# ─── Supported document MIME types ───────────────────────────────────────────
SUPPORTED_DOC_TYPES = {
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

MAX_DOC_SIZE_MB = 10


# ─── Request / Response Models ────────────────────────────────────────────────

# Agent names must be filename-safe: letters, digits, spaces, hyphens, underscores.
_SAFE_NAME_RE = re.compile(r"^[\w\s\-]{1,64}$")


class ChatRequest(BaseModel):
    agent_name: str
    message: str


class CreateAgentRequest(BaseModel):
    name: str
    patterns: str   # Comma-separated trigger phrases
    responses: str  # Comma-separated reply options

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Agent name cannot be empty.")
        if not _SAFE_NAME_RE.match(v):
            raise ValueError(
                "Agent name may only contain letters, digits, spaces, hyphens, "
                "and underscores (max 64 characters)."
            )
        return v


class RawAgentRequest(BaseModel):
    name: str
    json_data: dict

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Agent name cannot be empty.")
        if not _SAFE_NAME_RE.match(v):
            raise ValueError(
                "Agent name may only contain letters, digits, spaces, hyphens, "
                "and underscores (max 64 characters)."
            )
        return v


# ─── Agents ───────────────────────────────────────────────────────────────────

@router.get("/api/agents", summary="List all loaded agents")
async def get_agents():
    """Return the names of all currently deployed agents."""
    return {"agents": engine.get_agent_names()}


@router.get("/api/agents/{name}", summary="Inspect a specific agent")
async def inspect_agent(name: str):
    """
    Return status and session memory for the given agent.
    Useful for debugging intent coverage.
    """
    agent = engine.get_agent(name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found.")
    return {
        "name": agent.name,
        "is_trained": agent.is_trained,
        "intent_count": len(agent.responses),
        "intents": list(agent.responses.keys()),
        "memory": agent.get_memory_snapshot(),
    }


@router.post("/api/agents", summary="Create an agent (form input)")
async def create_new_agent(req: CreateAgentRequest):
    """
    Parse comma-separated patterns and responses, then deploy a new agent
    (or append an intent to an existing one).
    """
    pattern_list = [p.strip() for p in req.patterns.split(",") if p.strip()]
    response_list = [r.strip() for r in req.responses.split(",") if r.strip()]

    if not pattern_list or not response_list:
        raise HTTPException(
            status_code=422,
            detail="At least one pattern and one response are required.",
        )

    agent_id = engine.create_agent(req.name, pattern_list, response_list)
    logger.info("Agent created via form: %s", agent_id)
    return {"status": "success", "agent": agent_id}


@router.post("/api/agents/raw", summary="Create an agent (raw JSON)")
async def create_agent_raw(req: RawAgentRequest):
    """
    Write raw intent JSON directly to the agents directory.
    Validates the JSON structure before persisting.
    """
    if "intents" not in req.json_data:
        raise HTTPException(
            status_code=422,
            detail="JSON must contain a top-level 'intents' key.",
        )

    clean_name = req.name.strip().replace(" ", "_")

    filepath = os.path.join(AGENTS_DIR, f"{clean_name}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(req.json_data, f, indent=4)

    engine.reload_agents()
    logger.info("Agent created via raw JSON: %s", clean_name)
    return {"status": "success", "agent": clean_name}


@router.delete("/api/agents/{name}", summary="Delete an agent")
async def delete_agent(name: str):
    """
    Permanently remove an agent's JSON file and unload it from memory.
    """
    clean_name = name.replace(" ", "_")
    filepath = os.path.join(AGENTS_DIR, f"{clean_name}.json")

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found.")

    os.remove(filepath)
    engine.reload_agents()
    logger.info("Agent deleted: %s", name)
    return {"status": "deleted", "agent": name}


# ─── Chat ─────────────────────────────────────────────────────────────────────

@router.post("/api/chat", summary="Chat with an agent")
async def chat_with_agent(req: ChatRequest):
    """
    Route a user message to the named agent's intent classifier.
    Returns the agent's response string.
    """
    if not req.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    response = engine.chat(req.agent_name, req.message)
    return {"response": response}


# ─── Document Upload ──────────────────────────────────────────────────────────

@router.post("/api/upload", summary="Upload a document for context injection")
async def upload_document(file: UploadFile = File(...)):
    """
    Parse an uploaded document (PDF, TXT, or DOCX) and store its text in
    the shared document_context so agents can reference it in responses.

    Supported formats: PDF, plain text, DOCX.
    Maximum file size: 10 MB.
    """
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)

    if size_mb > MAX_DOC_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {MAX_DOC_SIZE_MB} MB.",
        )

    extracted_text = ""
    file_lower = (file.filename or "").lower()

    # ── PDF ───────────────────────────────────────────────────────────────────
    if file_lower.endswith(".pdf"):
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
            extracted_text = "\n".join(pages).strip()
        except ImportError:
            raise HTTPException(
                status_code=501,
                detail="pdfplumber not installed. Run: pip install pdfplumber",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=422, detail=f"Could not parse PDF: {exc}"
            )

    # ── DOCX ──────────────────────────────────────────────────────────────────
    elif file_lower.endswith(".docx"):
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            extracted_text = "\n".join(
                p.text for p in doc.paragraphs if p.text
            ).strip()
        except ImportError:
            raise HTTPException(
                status_code=501,
                detail="python-docx not installed. Run: pip install python-docx",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=422, detail=f"Could not parse DOCX: {exc}"
            )

    # ── Plain text ────────────────────────────────────────────────────────────
    elif file_lower.endswith(".txt") or (file.content_type or "").startswith("text/"):
        try:
            extracted_text = content.decode("utf-8", errors="replace").strip()
        except Exception as exc:
            raise HTTPException(
                status_code=422, detail=f"Could not decode text file: {exc}"
            )

    else:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Upload PDF, TXT, or DOCX.",
        )

    if not extracted_text:
        raise HTTPException(
            status_code=422,
            detail="No text could be extracted from the file.",
        )

    engine.set_document_context(extracted_text, file.filename or "unknown")

    logger.info(
        "Document loaded — file='%s', chars=%d", file.filename, len(extracted_text)
    )
    return {
        "filename": file.filename,
        "size_kb": round(len(content) / 1024, 2),
        "chars_extracted": len(extracted_text),
        "status": "parsed",
        "preview": extracted_text[:200] + ("…" if len(extracted_text) > 200 else ""),
    }


@router.delete("/api/context", summary="Clear active document context")
async def clear_document_context():
    """Remove the currently loaded document from the agent context."""
    engine.clear_document_context()
    return {"status": "cleared"}


# ─── Voice ────────────────────────────────────────────────────────────────────

@router.post("/api/voice", summary="Upload audio for speech-to-text")
async def process_voice(audio: UploadFile = File(...)):
    """
    Accept a WebM audio blob recorded by the browser's MediaRecorder API.

    Currently returns a stub message. To enable real STT, integrate:
      - OpenAI Whisper (local): pip install openai-whisper
      - Groq Whisper API:       pip install groq

    See ARCHITECTURE.md § Voice Pipeline for integration instructions.
    """
    content = await audio.read()
    size_kb = round(len(content) / 1024, 2)

    # ── Whisper integration stub ──────────────────────────────────────────────
    # Uncomment to enable local Whisper STT:
    #
    #   import whisper, tempfile, soundfile as sf
    #   model = whisper.load_model("base")
    #   with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
    #       tmp.write(content); tmp_path = tmp.name
    #   result = model.transcribe(tmp_path)
    #   transcribed_text = result["text"]
    #   os.unlink(tmp_path)
    #
    transcribed_text = (
        f"Audio received ({size_kb} KB). "
        "Local STT engine is offline — see ARCHITECTURE.md to enable Whisper."
    )

    return {"text": transcribed_text, "status": "success"}


# ─── Health ───────────────────────────────────────────────────────────────────

@router.get("/api/health", summary="Health check / liveness probe")
async def health_check():
    """Returns server status and loaded agent count. Used by Docker HEALTHCHECK."""
    return {
        "status": "healthy",
        "agents_loaded": len(engine.get_agent_names()),
        "document_loaded": bool(engine.document_context),
        "document_filename": engine.document_filename or None,
    }
