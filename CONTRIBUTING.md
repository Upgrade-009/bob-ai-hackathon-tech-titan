# Contributing Guidelines - Team Tech Titans

Thank you for participating in the **IBM Bob AI Innovation Hackathon Round 1** development for **Problem Statement L1: Container Congestion Predictor & Port Operations Optimiser**.

## Code Guidelines

1. **Source Code Location**: All application source code must reside inside `src/`.
   - `src/backend/`: FastAPI services, algorithms, database models, CSV datasets, and MCP server.
   - `src/frontend/`: Pure HTML, CSS, and Vanilla JavaScript UI files.
2. **Template Compliance**: Do NOT remove or rename required top-level directories:
   - `submission.yaml`, `README.md`, `src/`, `docs/`, `demo/`, `presentation/`, `.gitignore`, `.github/workflows/validate.yml`
3. **Dependencies**: Use standard Python 3.11+ dependencies specified in `src/backend/requirements.txt`.
4. **No Hardcoded Secrets**: Never commit real API keys, passwords, or tokens. Use `.env.example` as a template.
5. **Testing**: Run local python syntax checks and test suite before committing code:
   ```bash
   python -m py_compile src/backend/*.py src/backend/services/*.py
   ```
