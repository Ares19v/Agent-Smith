# Agent Smith: Multi-Agent Intent System

A professional, modular AI Orchestrator built with **FastAPI** and **Machine Learning**. This system allows for the dynamic creation, deployment, and management of custom AI agents with intent-based recognition.

## 🚀 Features
- **Modular Architecture**: Isolated Core Engine, API, and Frontend logic.
- **Dynamic Agent Deployment**: Create agents via UI or raw JSON mode.
- **Neural Intent Matching**: Uses TF-IDF vectorization and MLP Neural Networks for local NLP.
- **Multimedia Support**: Integrated Voice-to-Text bridge and Document parsing.
- **Premium UI**: Dark-themed interface with spring-physics "glide" animations.

## 📦 Installation
1. **Clone the repo**:
   \\\ash
   git clone https://github.com/Ares19v/Agent-Smith.git
   \\\
2. **Install dependencies**:
   \\\ash
   pip install -r requirements.txt
   \\\
3. **Run the server**:
   \\\ash
   python -m uvicorn app:app --reload
   \\\

## 📂 Project Structure
- \pp.py\: FastAPI entry point.
- \pi.py\: Route handlers for Chat, Voice, and Uploads.
- \core_engine.py\: Neural Network logic and Agent management.
- \static/\: Clean CSS and Modular JS.
- \gents_data/\: Local storage for Agent JSON profiles.