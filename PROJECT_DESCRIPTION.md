# HCPilot - Project Description

## Overview
An AI-powered CRM system for pharmaceutical field representatives to manage Healthcare Professional (HCP) interactions through natural language chat, eliminating manual data entry.

## Key Features

### 🎯 Core Functionality
- **Natural Language Logging**: Log HCP interactions via chat ("Met Dr. Sharma today, discussed OncoBoost efficacy")
- **Smart Entity Extraction**: AI extracts doctor names, topics, attendees, sentiment, and materials from conversational input
- **Real-time Form Updates**: Chat responses automatically populate the interaction form, ready for review/save
- **Multi-entity Support**: Handles HCPs, Materials, Samples, and Follow-ups

### 🏗️ Architecture
```
Frontend (React + Redux) ←→ Backend (FastAPI) ←→ LLM (Groq)
                              ↓
                         Database (SQLite)
```

### 🧠 AI Pipeline
1. **Intent Classification**: Identifies if user wants to log interaction, search HCP, or schedule follow-up
2. **Entity Extraction**: Parses structured data from natural language
3. **Entity Refactoring**: Resolves partial names to IDs (e.g., "Dr. Sharma" → Database lookup → ID)
4. **Tool Orchestration**: Executes database operations with proper validation

### ✨ User Experience
- Users describe interactions conversationally
- System extracts and enriches data automatically
- Form is pre-populated with extracted details
- Users review, modify if needed, and save

### 🛠️ Tech Stack
- **Frontend**: React 18, TypeScript, Redux Toolkit, Tailwind CSS
- **Backend**: FastAPI, Python, SQLAlchemy, LangGraph
- **LLM**: Groq (Llama 3.3 70B)
- **Database**: SQLite with async ORM

### 📊 Impact
- Reduces interaction logging time by ~70%
- Improves data completeness through AI-assisted capture
- Enables field reps to focus on HCP relationships vs. paperwork