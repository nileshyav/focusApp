"""
Application Entrypoint.
Imports FastAPI app from app.main and launches Uvicorn server.
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
