# Step-by-Step Setup & Verification Guide

This guide can be executed by anyone on a fresh system with Python 3.11+.

## 1. System Requirements & Prerequisites
- Operating System: Windows 10/11, macOS, or Linux
- Python: Version 3.11 or higher (`python --version`)
- Web Browser: Google Chrome, Edge, Firefox, or Safari

## 2. Installation Commands

Step 1: Clone or navigate to the repository directory:
```bash
cd D:\hakka\bob-ai-hackathon-tech-titans
```

Step 2: Install Python dependencies:
```bash
cd src/backend
pip install -r requirements.txt
```

## 3. Environment Variables Configuration (Optional)
If you wish to test with IBM watsonx.ai, copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your `WATSONX_API_KEY` and `WATSONX_PROJECT_ID`. If omitted, the application seamlessly uses local deterministic AI logic.

## 4. Startup Commands

Start the application backend server:
```bash
python -m uvicorn src.backend.main:app --reload --port 8000
```

Output should confirm:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Database initialized successfully.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## 5. Browser URL & API Health Check
- Open your browser to: **`http://127.0.0.1:8000/`**
- Test API Health Check: **`http://127.0.0.1:8000/api/health`**
  Response:
  ```json
  {
    "status": "healthy",
    "service": "Port Operations Optimiser API",
    "version": "1.0.0",
    "database": "SQLite Connected"
  }
  ```

## 6. MCP Server Testing (IBM Bob Integration)
To verify the Model Context Protocol tools:
```bash
python src/backend/mcp_server.py get_port_status
python src/backend/mcp_server.py recommend_alternate_route V102
```

## 7. Troubleshooting
- **Port 8000 already in use**: Start on port 8080: `python -m uvicorn src.backend.main:app --port 8080`
- **Database lock issues**: Delete `src/backend/data/port_operations.db` and restart server; the database will re-initialize automatically from CSVs.
