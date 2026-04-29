"""
core_engine.py
==============
The neural backbone of Agent Smith.

Manages the lifecycle of all IntentAgents:
  - Dynamic training via TF-IDF + MLP classifier.
  - Session-aware conversational memory.
  - Document context injection for file-grounded responses.
  - Hot-reload of agents without server restart.
"""

import json
import os
import glob
import random
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
import numpy as np
import warnings

warnings.filterwarnings('ignore')

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("AgentSmith.CoreEngine")

# ─── Constants ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_DIR = os.path.join(BASE_DIR, "agents_data")
os.makedirs(AGENTS_DIR, exist_ok=True)

# Confidence below which we fall back (tune between 0.25–0.45)
CONFIDENCE_THRESHOLD = 0.30

# Rolling window for session memory
SESSION_MEMORY_SIZE = 10

# Number of past user turns to prepend as context for better intent matching
CONTEXT_WINDOW = 2


class IntentAgent:
    """
    A single, independently-trained AI agent.

    Each agent is backed by:
      - A TF-IDF vectorizer (filters English stop-words).
      - A two-layer MLP classifier (32 → 16 hidden units).
      - A rolling session memory for conversational continuity.
    """

    def __init__(self, name: str, filepath: str):
        self.name = name
        self.filepath = filepath
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words="english")
        self.model = MLPClassifier(
            hidden_layer_sizes=(32, 16),
            max_iter=1000,
            random_state=42,
        )
        self.responses: dict[str, list[str]] = {}
        self.is_trained = False
        self.memory: list[dict] = []  # {"role": "user"|"bot", "content": str}
        self.train()

    # ── Training ──────────────────────────────────────────────────────────────

    def train(self) -> None:
        """Load the agent JSON and fit the TF-IDF + MLP pipeline."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            corpus: list[str] = []
            tags: list[str] = []

            for intent in data.get("intents", []):
                self.responses[intent["tag"]] = intent["responses"]
                for pattern in intent["patterns"]:
                    corpus.append(pattern)
                    tags.append(intent["tag"])

            if len(corpus) > 1:
                X = self.vectorizer.fit_transform(corpus)
                self.model.fit(X, tags)
                self.is_trained = True
                logger.info(
                    "Agent '%s' trained — %d patterns across %d intents.",
                    self.name,
                    len(corpus),
                    len(self.responses),
                )
            else:
                logger.warning(
                    "Agent '%s' needs more training patterns (found %d).",
                    self.name,
                    len(corpus),
                )
        except Exception as exc:
            logger.error("Failed to train agent '%s': %s", self.name, exc)

    # ── Inference ─────────────────────────────────────────────────────────────

    def get_response(self, text: str, document_context: str = "") -> str:
        """
        Classify the user's intent and return an appropriate response.

        Args:
            text:             Raw user message.
            document_context: Text extracted from an uploaded document.

        Returns:
            A string response from the matched intent, or a fallback message.
        """
        if not self.is_trained:
            return (
                "My neural pathways are untrained. "
                "Deploy more patterns via the Create menu."
            )

        # ── Build context-enriched query ──────────────────────────────────────
        # Prepend the last N user turns so the classifier sees conversational
        # continuity (e.g., pronoun resolution, follow-up questions).
        recent_turns = [
            m["content"]
            for m in self.memory
            if m["role"] == "user"
        ][-CONTEXT_WINDOW:]
        enriched_query = " ".join(recent_turns + [text]) if recent_turns else text

        # Append document keywords if context is loaded
        if document_context:
            # Use only the first 500 chars to avoid diluting the TF-IDF space
            enriched_query += " " + document_context[:500]

        # ── Session memory update ─────────────────────────────────────────────
        self.memory.append({"role": "user", "content": text})
        if len(self.memory) > SESSION_MEMORY_SIZE:
            self.memory.pop(0)

        # ── Classification ────────────────────────────────────────────────────
        try:
            X = self.vectorizer.transform([enriched_query])
            pred = self.model.predict(X)[0]
            conf = float(np.max(self.model.predict_proba(X)[0]))

            if conf >= CONFIDENCE_THRESHOLD:
                reply = random.choice(self.responses[pred])
            else:
                # ── LLM Fallback Hook ─────────────────────────────────────────
                # Confidence too low for a strict intent match.
                # To enable an LLM fallback, uncomment and configure one of:
                #
                #   Groq (cloud, fast):
                #     from groq import Groq
                #     client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                #     completion = client.chat.completions.create(
                #         model="llama3-8b-8192",
                #         messages=[{"role": "user", "content": text}]
                #     )
                #     reply = completion.choices[0].message.content
                #
                #   Ollama (local, private):
                #     import requests
                #     r = requests.post("http://localhost:11434/api/generate",
                #         json={"model": "llama3", "prompt": text, "stream": False})
                #     reply = r.json()["response"]
                #
                reply = (
                    "I couldn't confidently match that to a known intent. "
                    "(LLM fallback is offline — see core_engine.py to enable.)"
                )
                if document_context:
                    reply += (
                        f"\n\n📄 Note: A document ({len(document_context):,} chars) "
                        "is loaded in context. Try asking something specific about it."
                    )

            logger.debug(
                "Agent '%s' → intent='%s', conf=%.2f", self.name, pred, conf
            )

            self.memory.append({"role": "bot", "content": reply})
            return reply

        except Exception as exc:
            logger.error("Inference error in agent '%s': %s", self.name, exc)
            return f"Internal error during inference: {exc}"

    def get_memory_snapshot(self) -> list[dict]:
        """Return a copy of the current session memory."""
        return list(self.memory)

    def clear_memory(self) -> None:
        """Wipe the session memory (e.g., on agent switch)."""
        self.memory.clear()
        logger.debug("Session memory cleared for agent '%s'.", self.name)


class AgentManager:
    """
    Singleton orchestrator that owns all IntentAgent instances.

    Responsibilities:
      - Scan the agents directory on startup.
      - Hot-reload agents after create/update operations.
      - Route chat requests to the correct agent.
      - Maintain a single shared document context across all agents.
    """

    def __init__(self):
        self.agents: dict[str, IntentAgent] = {}
        self.document_context: str = ""
        self.document_filename: str = ""
        self.reload_agents()

    # ── Agent Lifecycle ───────────────────────────────────────────────────────

    def reload_agents(self) -> None:
        """Re-scan the agents directory and (re)train all agents."""
        self.agents.clear()
        pattern = os.path.join(AGENTS_DIR, "*.json")
        found = glob.glob(pattern)
        for path in found:
            name = (
                os.path.basename(path)
                .replace(".json", "")
                .replace("_", " ")
            )
            self.agents[name] = IntentAgent(name, path)
        logger.info(
            "AgentManager ready — %d agent(s) loaded: %s",
            len(self.agents),
            list(self.agents.keys()),
        )

    def get_agent_names(self) -> list[str]:
        return list(self.agents.keys())

    def get_agent(self, name: str) -> IntentAgent | None:
        return self.agents.get(name)

    # ── Conversation ──────────────────────────────────────────────────────────

    def chat(self, agent_name: str, text: str) -> str:
        """Route a message to the named agent and return its response."""
        agent = self.agents.get(agent_name)
        if not agent:
            available = ", ".join(self.agents.keys()) or "none"
            return f"Agent '{agent_name}' is offline. Available: {available}."
        return agent.get_response(text, self.document_context)

    # ── Agent Creation ────────────────────────────────────────────────────────

    def create_agent(
        self,
        name: str,
        patterns: list[str],
        responses: list[str],
    ) -> str:
        """
        Create or extend an agent with a new intent block.

        If the agent JSON already exists, the new intent is appended.
        Triggers a full hot-reload so changes are immediately live.

        Returns:
            The sanitised agent identifier (file-safe name).
        """
        clean_name = name.strip().replace(" ", "_")
        filepath = os.path.join(AGENTS_DIR, f"{clean_name}.json")

        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"intents": []}

        tag_name = f"intent_{len(data['intents'])}"
        data["intents"].append(
            {
                "tag": tag_name,
                "patterns": patterns,
                "responses": responses,
            }
        )

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        logger.info(
            "Agent '%s' updated — appended tag '%s' with %d patterns.",
            clean_name,
            tag_name,
            len(patterns),
        )
        self.reload_agents()
        return clean_name

    # ── Document Context ──────────────────────────────────────────────────────

    def set_document_context(self, text: str, filename: str = "") -> None:
        """Store parsed document text for injection into agent responses."""
        self.document_context = text
        self.document_filename = filename
        logger.info(
            "Document context updated — file='%s', length=%d chars.",
            filename,
            len(text),
        )

    def clear_document_context(self) -> None:
        """Remove the current document context."""
        self.document_context = ""
        self.document_filename = ""
        logger.info("Document context cleared.")


# ─── Module-level singleton ───────────────────────────────────────────────────
engine = AgentManager()
