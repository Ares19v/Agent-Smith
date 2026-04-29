# Agent Smith — Architecture Deep Dive

This document details the internal architecture and design decisions behind Agent Smith.

## 1. Core Engine (`core_engine.py`)

The neural backbone of the system. It manages the lifecycle of `IntentAgent` objects.

### `IntentAgent`
- **NLP Pipeline**: Uses `scikit-learn`'s `TfidfVectorizer` to convert text into token frequency vectors, filtering out common English stop-words.
- **Neural Network**: A Multi-Layer Perceptron (`MLPClassifier`) with two hidden layers (32 and 16 units) trained on the TF-IDF vectors. It outputs probabilities for different intent tags.
- **Session Memory**: Maintains a rolling window of recent conversational turns to provide context for the intent classifier and for LLM fallbacks.

### `AgentManager`
- A singleton class that holds all loaded agents.
- Automatically scans the `agents_data/` directory for JSON files and instantiates an `IntentAgent` for each.
- Handles hot-reloading when an agent is created or updated.
- Manages the global `document_context` for RAG-like capabilities.

## 2. API Layer (`api.py`)

A FastAPI router that exposes the core engine functionalities over REST endpoints.

- **Agent Management**: Endpoints to list, inspect, create, and delete agents.
- **Chat**: Receives user messages and routes them to the requested agent.
- **Document Context**: Endpoints to upload and parse documents (PDF, DOCX, TXT) and inject them into the `AgentManager`'s context.

## 3. Frontend Application

The user interface consists of a Single Page Application (SPA) shell (`index.html`) driven by vanilla JavaScript (`static/main.js`) and styled with vanilla CSS (`static/style.css`).

- Communicates with the FastAPI backend asynchronously using `fetch`.
- Features an agent selector, chat window, document upload interface, and a microphone stub for voice input.

## 4. Extensions & Fallbacks

- **LLM Fallback**: When the MLP classifier's confidence score falls below `CONFIDENCE_THRESHOLD`, the system can optionally route the request to an external LLM (e.g., Groq, OpenAI) or a local model (Ollama) to handle out-of-domain queries gracefully.
- **Voice Pipeline**: The frontend can record WebM audio and send it to the `/api/voice` endpoint. This is ready to be hooked up to a local or cloud-based Whisper speech-to-text model.
