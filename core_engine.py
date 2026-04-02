import json
import os
import glob
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
import numpy as np
import warnings

warnings.filterwarnings('ignore')

AGENTS_DIR = 'agents_data'
os.makedirs(AGENTS_DIR, exist_ok=True)

class IntentAgent:
    def __init__(self, name, filepath):
        self.name = name
        self.filepath = filepath
        # Upgraded to TF-IDF to filter out common 'noise' words
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
        # Deeper neural network for better pattern recognition
        self.model = MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=1000, random_state=42)
        self.responses = {}
        self.is_trained = False
        self.memory = [] # Active session memory
        self.train()

    def train(self):
        try:
            with open(self.filepath, 'r') as f: data = json.load(f)
            corpus, tags = [], []
            for intent in data.get('intents', []):
                self.responses[intent['tag']] = intent['responses']
                for p in intent['patterns']:
                    corpus.append(p)
                    tags.append(intent['tag'])
            
            # An MLP needs at least a few samples to not crash
            if len(corpus) > 1:
                X = self.vectorizer.fit_transform(corpus)
                self.model.fit(X, tags)
                self.is_trained = True
            else:
                print(f"[{self.name}] Awaiting more training patterns.")
        except Exception as e:
            print(f"Failed to train {self.name}: {e}")

    def get_response(self, text, document_context=""):
        self.memory.append({"role": "user", "content": text})
        if len(self.memory) > 10: self.memory.pop(0) # Keep last 10 messages

        if not self.is_trained:
            return "My neural pathways are untrained. Deploy more patterns via the Create menu."
        
        try:
            X = self.vectorizer.transform([text])
            pred = self.model.predict(X)[0]
            conf = np.max(self.model.predict_proba(X)[0])
            
            # Confidence threshold
            if conf > 0.30: 
                reply = random.choice(self.responses[pred])
            else:
                # --- DYNAMIC FALLBACK ---
                # When the intent isn't recognized, you can seamlessly pipe this into an LLM.
                # E.g., client = Groq(api_key="your_key"); client.chat.completions.create(...)
                reply = "I couldn't match that to a strict intent. (LLM Fallback Offline)"
            
            self.memory.append({"role": "bot", "content": reply})
            return reply
        except Exception as e:
            return f"Error processing request: {e}"

class AgentManager:
    def __init__(self):
        self.agents = {}
        self.document_context = "" # Stores text from uploaded files
        self.reload_agents()
        
    def reload_agents(self):
        self.agents.clear()
        for path in glob.glob(f"{AGENTS_DIR}/*.json"):
            name = os.path.basename(path).replace('.json', '').replace('_', ' ')
            self.agents[name] = IntentAgent(name, path)
            
    def get_agent_names(self):
        return list(self.agents.keys())
        
    def chat(self, agent_name, text):
        if agent_name not in self.agents: return "Agent offline."
        return self.agents[agent_name].get_response(text, self.document_context)

    def create_agent(self, name, patterns, responses):
        clean_name = name.strip().replace(" ", "_")
        filepath = os.path.join(AGENTS_DIR, f"{clean_name}.json")
        
        # Check if file exists to append, otherwise create new
        if os.path.exists(filepath):
            with open(filepath, 'r') as f: data = json.load(f)
        else:
            data = {"intents": []}
            
        tag_name = f"intent_{len(data['intents'])}"
        data['intents'].append({
            "tag": tag_name,
            "patterns": patterns,
            "responses": responses
        })
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
            
        self.reload_agents()
        return clean_name

engine = AgentManager()
