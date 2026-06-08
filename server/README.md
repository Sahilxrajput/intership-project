# ⚡ CodeX Execution Engine

A production-grade, secure code execution backend built with **FastAPI** and **Docker**.  
Each code submission runs in an isolated, resource-limited Docker container — no shared state, no escape.

---

## 🏗️ Architecture

```
POST /api/v1/execute
       │
       ▼
 FastAPI (Uvicorn)
       │
       ▼
 DockerExecutionService
       │
       ├── Write code to tempdir
       ├── (Optional) Compile step  ──► Compile error response
       ├── Run container with limits
       │     ├── mem_limit: 128m
       │     ├── cpu_quota: 50% of 1 core
       │     ├── pids_limit: 50
       │     └── network_disabled: true
       └── Return stdout / stderr / exit_code / time
```

---

## 🌐 Supported Languages

| Language   | Docker Image          | Compile Step |
|------------|-----------------------|--------------|
| Python     | `python:3.11-alpine`  | ❌           |
| JavaScript | `node:18-alpine`      | ❌           |
| Java       | `openjdk:17-alpine`   | ✅ javac     |
| C++        | `gcc:13-bookworm`     | ✅ g++       |

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Docker daemon running

### Run with Docker Compose
```bash
git clone <repo>
cd code-exec-backend

docker compose up --build
```

API is live at: `http://localhost:8000`  
Swagger docs: `http://localhost:8000/docs`

### Run locally (dev mode)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## 📡 API Endpoints

### `POST /api/v1/execute`

**Request body:**
```json
{
  "language": "python",
  "code": "name = input()\nprint(f'Hello, {name}!')",
  "stdin": "World",
  "timeout": 10
}
```

**Response:**
```json
{
  "status": "success",
  "stdout": "Hello, World!",
  "stderr": "",
  "exit_code": 0,
  "execution_time_ms": 342.5,
  "language": "python",
  "message": null
}
```

**Status values:** `success` | `error` | `timeout` | `compile_error`

### `GET /api/v1/health`
Returns API + Docker daemon health status.

---

## 🔒 Security Model

| Protection | How |
|---|---|
| Process isolation | Each run = new Docker container |
| Memory limit | 128 MB RAM, no swap |
| CPU limit | 50% of one core |
| Process limit | Max 50 PIDs |
| Network isolation | `network_disabled: true` |
| Timeout | Configurable 1–30s, container killed on breach |
| Auto-cleanup | Container removed after execution |

---

## 📁 Project Structure

```
code-exec-backend/
├── app/
│   ├── main.py                  # FastAPI app + middleware
│   ├── routers/
│   │   ├── execute.py           # POST /execute endpoint
│   │   └── health.py            # GET /health endpoint
│   ├── services/
│   │   └── docker_service.py    # Core Docker execution logic
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response models
│   └── utils/
│       └── logger.py            # Structured logging
├── Dockerfile                   # Multi-stage build
├── docker-compose.yml           # One-command deployment
└── requirements.txt
```

---

## 🧪 Example cURL Requests

**Python:**
```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{"language":"python","code":"print(sum(range(1,101)))","timeout":5}'
```

**Java:**
```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "language": "java",
    "code": "public class Solution { public static void main(String[] args) { System.out.println(\"Hello from Java!\"); } }"
  }'
```

---

## 🔧 Extending

To add a new language (e.g., Go):
1. Add entry to `LANGUAGE_CONFIG` in `docker_service.py`
2. Add `"go"` to the `Language` enum in `schemas.py`
3. That's it — no other changes needed
