#!/usr/bin/env bash
set -e

echo "======================================================================"
echo "  REST API Design and Documentation Kit - Capstone 48"
echo "======================================================================"

# 1. Verify Python availability
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found in PATH."
    echo "Please install Python 3.11+ using your package manager."
    exit 1
fi

# 2. Create virtual environment if absent
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment in .venv..."
    python3 -m venv .venv
fi

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Install / Verify dependencies
echo "[*] Checking dependencies..."
pip install -r requirements.txt --quiet

# 5. Initialize & Seed database idempotently
echo "[*] Initializing and seeding database..."
python scripts/seed_database.py

# 6. Launch FastAPI server
echo "======================================================================"
echo "[*] Starting FastAPI application with Uvicorn..."
echo "[*] Local Server URL:    http://127.0.0.1:8000"
echo "[*] Swagger UI (Docs):   http://127.0.0.1:8000/docs"
echo "[*] ReDoc UI:            http://127.0.0.1:8000/redoc"
echo "[*] OpenAPI JSON:        http://127.0.0.1:8000/openapi.json"
echo "[*] Press Ctrl+C to stop the server anytime."
echo "======================================================================"

uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
