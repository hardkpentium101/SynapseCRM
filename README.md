# 🧠 SynapseCRM

**AI-Powered CRM for Pharmaceutical Field Representatives**

[![Demo Video](https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg)](https://drive.google.com/file/d/1I5omEUK_6HC3B09uA3Z3XxfXOAaslrQo/view?usp=sharing)
▶️ [Watch Demo Video](https://drive.google.com/file/d/1I5omEUK_6HC3B09uA3Z3XxfXOAaslrQo/view?usp=sharing)

An intelligent, conversational CRM system that transforms how healthcare professionals document field interactions. Using advanced natural language processing, SynapseCRM eliminates tedious manual data entry by automatically extracting, enriching, and organizing interaction details from casual conversation.

---

## ✨ Key Features

- **🎯 Natural Language Logging** — Log HCP interactions through chat instead of forms
- **🤖 Intelligent Entity Extraction** — Auto-extracts doctors, topics, materials, follow-ups, and sentiment
- **⚡ Real-time Form Population** — Chat responses instantly populate forms (70% faster)
- **🔍 Smart Entity Refactoring** — Resolves partial names and variations to database IDs

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-------------|
| **Frontend** | React 18, TypeScript, Redux Toolkit, Tailwind CSS, Shadcn UI |
| **Backend** | FastAPI, Python, SQLAlchemy, LangGraph |
| **AI/LLM** | Groq (Llama 3.3 70B) |
| **Database** | SQLite (dev) / PostgreSQL (prod) |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API Key

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your_api_key_here"
export DATABASE_URL="sqlite:///./crm.db"

# Start backend server
python run.py
```

Backend runs at `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at `http://localhost:5173`

---

## 📖 Usage

1. **Open the app** at `http://localhost:5173`
2. **Describe your HCP meeting** in natural language:
   ```
   "Met Dr. Sharma today, discussed OncoBoost efficacy and showed him the latest trial data. He's very interested."
   ```
3. **Review the auto-populated form** — edit if needed
4. **Save** — interaction is logged instantly

---

## 🧠 Architecture

```
┌────────────────────────────────┐
│     React 18 Frontend           │
│ (Redux Toolkit + TypeScript)    │
└────────────┬─────────────────────┘
             │ REST API
             ▼
┌────────────────────────────────┐
│      FastAPI Backend            │
│ • LangGraph Agent Pipeline      │
│ • Entity Extraction & Validation│
│ • Conversation Memory           │
└────────────┬─────────────────────┘
             │
     ┌──────┼──────────┐
     ▼      ▼          ▼
  ModelSelector LLMManager SQLite
  (Groq/Llama) (Provider) Database
```

### Core Components
- **HCPAgent** — Main orchestrator for HCP interactions
- **EntityExtractor** — Extracts structured data from chat
- **ModelSelector** — Routes tasks to optimal LLM
- **ConversationMemory** — Per-session state management

---

## 🧪 Testing

### Backend
```bash
cd backend
pytest tests/ -v
```

### Frontend
```bash
cd frontend
npm test
npm run test:coverage
```

---

## 📦 Project Structure

```
SynapseCRM/
├── backend/
│   ├── src/
│   │   ├── agent/          # AI agents (LangGraph)
│   │   ├── api/            # FastAPI routes
│   │   ├── db/             # Database models
│   │   ├── llm/            # LLM management
│   │   └── services/       # Business logic
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── features/       # Redux slices & features
│   │   ├── services/       # API integration
│   │   └── pages/          # Route pages
│   └── package.json
│
└── README.md
```

---

## 🔧 Environment Variables

### Backend (.env)
```
GROQ_API_KEY=your_groq_key
DATABASE_URL=sqlite:///./crm.db
ENVIRONMENT=development
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

---

## 📝 License

MIT License — see [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

**Made with ❤️ for pharmaceutical field representatives**
