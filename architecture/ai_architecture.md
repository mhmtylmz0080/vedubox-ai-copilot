# AI Architecture Overview

## Core Components

### 1. LLM Layer
- OpenAI (default)
- Future: Enterprise local model option

### 2. Retrieval Layer (RAG)
- Content chunking
- Embedding generation
- Vector database

### 3. Application Layer
- Prompt engineering
- Response validation
- Role-based access control

### 4. Security Layer
- PII masking
- Prompt injection filtering
- Backend authorization check

---

## AI Interaction Flow

User → AI Service → RAG Retrieval → LLM → Validation Layer → UI
