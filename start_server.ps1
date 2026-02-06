
# 1. Install dependencies (just in case)
pip install -r requirements.txt

# 2. Run the server with hot reload
# Host: 0.0.0.0 allows access from external sources if needed
# Port: 8000 is the standard FastAPI port
echo "🐰 Starting VertexRabbit on Port 8000..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
