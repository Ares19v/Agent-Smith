"""
core_engine.py
==============
The neural backbone of Agent Smith.

Manages the lifecycle of all IntentAgents:
  - Hybrid intent matching via TF-IDF Cosine Similarity & MLP Classification.
  - Session-aware conversational memory buffer.
  - Semantic Document RAG (Retrieval-Augmented Generation) context injection.
  - Optional local Ollama / Groq / OpenAI fallback integration.
  - Hot-reload of agents without server restart.
"""

import json
import os
import glob
import random
import logging
import re
import urllib.request
import urllib.error
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.metrics.pairwise import cosine_similarity
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

# Confidence threshold for intent matching
CONFIDENCE_THRESHOLD = 0.25

# Rolling window for session memory
SESSION_MEMORY_SIZE = 12

# Number of past user turns to prepend as context
CONTEXT_WINDOW = 2


def clean_text(text: str) -> str:
    """Normalize text for tokenization and similarity comparison."""
    return re.sub(r"[^\w\s]", "", text.lower()).strip()


class IntentAgent:
    """
    A single, independently-trained AI agent.

    Backed by:
      - A TF-IDF vectorizer over all training patterns.
      - Direct Cosine-Similarity pattern matching for robust 1-to-N matching.
      - An MLP Classifier for multi-class intent boundary classification.
      - Rolling session memory buffer.
    """

    def __init__(self, name: str, filepath: str):
        self.name = name
        self.filepath = filepath
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2))
        self.model: MLPClassifier | None = None
        self.responses: dict[str, list[str]] = {}
        self.patterns_map: dict[str, list[str]] = {}
        self.corpus: list[str] = []
        self.tags: list[str] = []
        self.corpus_vectors = None
        self.is_trained = False
        self.memory: list[dict] = []  # {"role": "user"|"bot", "content": str}
        self.train()

    # ── Training ──────────────────────────────────────────────────────────────

    def train(self) -> None:
        """Load the agent JSON and fit the TF-IDF + Classifier pipeline."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.corpus = []
            self.tags = []
            self.responses = {}
            self.patterns_map = {}

            for intent in data.get("intents", []):
                tag = intent.get("tag", "default")
                self.responses[tag] = intent.get("responses", ["Understood."])
                self.patterns_map[tag] = intent.get("patterns", [])
                for pattern in self.patterns_map[tag]:
                    self.corpus.append(pattern)
                    self.tags.append(tag)

            if len(self.corpus) >= 1:
                # Fit TF-IDF on corpus
                self.corpus_vectors = self.vectorizer.fit_transform(self.corpus)
                unique_tags = list(set(self.tags))

                # If 2 or more classes exist, train MLP Classifier as well
                if len(unique_tags) >= 2 and len(self.corpus) >= 3:
                    try:
                        self.model = MLPClassifier(
                            hidden_layer_sizes=(32, 16),
                            max_iter=500,
                            random_state=42,
                        )
                        self.model.fit(self.corpus_vectors, self.tags)
                    except Exception as me:
                        logger.debug("MLP Classifier skipped for '%s': %s", self.name, me)
                        self.model = None
                else:
                    self.model = None

                self.is_trained = True
                logger.info(
                    "Agent '%s' trained — %d pattern(s) across %d intent(s).",
                    self.name,
                    len(self.corpus),
                    len(self.responses),
                )
            else:
                self.is_trained = False
                logger.warning("Agent '%s' has 0 patterns.", self.name)
        except Exception as exc:
            logger.error("Failed to train agent '%s': %s", self.name, exc)
            self.is_trained = False

    # ── Inference ─────────────────────────────────────────────────────────────

    def get_response(self, text: str, document_context: str = "", document_filename: str = "") -> str:
        """
        Classify user intent using hybrid Cosine Similarity + MLP + RAG Document lookup.
        """
        if not self.is_trained or not self.corpus:
            return (
                "My neural pathways are untrained. "
                "Deploy patterns via the 'Deploy New Core' menu."
            )

        user_clean = clean_text(text)

        # ── 1. Exact Substring Match Check ────────────────────────────────────
        for tag, patterns in self.patterns_map.items():
            for pat in patterns:
                pat_clean = clean_text(pat)
                if pat_clean and (pat_clean in user_clean or user_clean in pat_clean):
                    reply = random.choice(self.responses[tag])
                    self._update_memory(text, reply)
                    return reply

        # ── 2. Vector Cosine Similarity ───────────────────────────────────────
        try:
            query_vec = self.vectorizer.transform([text])
            sims = cosine_similarity(query_vec, self.corpus_vectors)[0]
            best_idx = int(np.argmax(sims))
            best_sim = float(sims[best_idx])
            best_tag = self.tags[best_idx]

            # ── 3. MLP Classifier Check (if trained) ──────────────────────────
            mlp_tag = None
            mlp_conf = 0.0
            if self.model is not None:
                try:
                    mlp_tag = self.model.predict(query_vec)[0]
                    mlp_conf = float(np.max(self.model.predict_proba(query_vec)[0]))
                except Exception:
                    pass

            # Combine signals: either high cosine similarity or high MLP confidence
            if best_sim >= CONFIDENCE_THRESHOLD:
                reply = random.choice(self.responses[best_tag])
                logger.debug("Agent '%s' Cosine match → '%s' (sim=%.2f)", self.name, best_tag, best_sim)
                self._update_memory(text, reply)
                return reply
            elif mlp_tag and mlp_conf >= 0.40:
                reply = random.choice(self.responses[mlp_tag])
                logger.debug("Agent '%s' MLP match → '%s' (conf=%.2f)", self.name, mlp_tag, mlp_conf)
                self._update_memory(text, reply)
                return reply

        except Exception as e:
            logger.debug("Vector match error in agent '%s': %s", self.name, e)

        # ── 4. Document RAG Context Lookup (if document is attached) ───────────
        if document_context:
            rag_snippet = self._query_document_rag(text, document_context)
            if rag_snippet:
                reply = (
                    f"📄 Extracted relevant passage from [{document_filename or 'Document Context'}]:\n\n"
                    f'"{rag_snippet}"'
                )
                self._update_memory(text, reply)
                return reply

        # ── 5. Optional LLM Fallback (Ollama or Groq or OpenAI) ───────────────
        llm_reply = self._query_llm_fallback(text, document_context)
        if llm_reply:
            self._update_memory(text, llm_reply)
            return llm_reply

        # ── 6. Fallback Response ──────────────────────────────────────────────
        fallback_msg = (
            f"I could not match your request to a registered intent for {self.name}. "
            f"Try asking about: {', '.join(self.corpus[:3])}."
        )
        if document_context:
            fallback_msg += (
                f"\n\n📄 Note: Document [{document_filename}] is active. "
                "You can query specific keywords from the document."
            )

        self._update_memory(text, fallback_msg)
        return fallback_msg

    def _query_document_rag(self, query: str, doc: str) -> str | None:
        """Extract top relevant paragraph from document context via TF-IDF similarity."""
        try:
            paragraphs = [p.strip() for p in doc.split("\n") if len(p.strip()) > 30]
            if not paragraphs:
                paragraphs = [doc[i:i+400] for i in range(0, min(len(doc), 4000), 300)]

            if not paragraphs:
                return None

            doc_vec = TfidfVectorizer(lowercase=True, stop_words="english")
            doc_matrix = doc_vec.fit_transform(paragraphs)
            q_vec = doc_vec.transform([query])
            sims = cosine_similarity(q_vec, doc_matrix)[0]

            best_idx = int(np.argmax(sims))
            if float(sims[best_idx]) > 0.15:
                return paragraphs[best_idx][:400]
        except Exception:
            pass
        return None

    def _query_llm_fallback(self, query: str, doc_context: str = "") -> str | None:
        """Check for local Ollama server running on localhost:11434."""
        try:
            prompt = (
                f"You are {self.name}, a specialized AI agent in the Agent Smith platform.\n"
            )
            if doc_context:
                prompt += f"Document Context: {doc_context[:1000]}\n"
            prompt += f"User message: {query}\nProvide a concise, helpful response:"

            req_data = json.dumps({
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }).encode("utf-8")

            req = urllib.request.Request(
                "http://127.0.0.1:11434/api/generate",
                data=req_data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "").strip()
        except Exception:
            return None

    def _update_memory(self, user_msg: str, bot_msg: str) -> None:
        """Add turn to session memory."""
        self.memory.append({"role": "user", "content": user_msg})
        self.memory.append({"role": "bot", "content": bot_msg})
        if len(self.memory) > SESSION_MEMORY_SIZE * 2:
            self.memory = self.memory[-SESSION_MEMORY_SIZE * 2:]

    def get_memory_snapshot(self) -> list[dict]:
        """Return formatted session exchanges."""
        exchanges = []
        for i in range(0, len(self.memory) - 1, 2):
            if self.memory[i]["role"] == "user" and self.memory[i+1]["role"] == "bot":
                exchanges.append({
                    "user": self.memory[i]["content"],
                    "bot": self.memory[i+1]["content"]
                })
        return exchanges

    def clear_memory(self) -> None:
        self.memory.clear()


class AgentManager:
    """
    Singleton orchestrator that owns all IntentAgent instances.
    """

    def __init__(self):
        self.agents: dict[str, IntentAgent] = {}
        self.document_context: str = ""
        self.document_filename: str = ""
        self.reload_agents()

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

    def chat(self, agent_name: str, text: str) -> str:
        agent = self.agents.get(agent_name)
        if not agent:
            available = ", ".join(self.agents.keys()) or "none"
            return f"Agent '{agent_name}' is offline. Available: {available}."
        return agent.get_response(text, self.document_context, self.document_filename)

    def create_agent(
        self,
        name: str,
        patterns: list[str],
        responses: list[str],
    ) -> str:
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

    def set_document_context(self, text: str, filename: str = "") -> None:
        self.document_context = text
        self.document_filename = filename
        logger.info("Document context updated — file='%s', length=%d chars.", filename, len(text))

    def clear_document_context(self) -> None:
        self.document_context = ""
        self.document_filename = ""
        logger.info("Document context cleared.")


# Singleton
engine = AgentManager()
