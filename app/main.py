import sys
import os

# Add the project root to sys.path to allow imports from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import router, get_predictor, load_datasets_global
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models and data on startup
    try:
        print("Initializing application...")
        get_predictor() # This triggers model loading
        load_datasets_global() # This loads data
        print("Initialization complete.")
    except Exception as e:
        print(f"Error during startup: {e}")
    yield

app = FastAPI(
    title="Water Level Prediction System",
    description="API for predicting water level and turbidity category based on sensor data.",
    version="3.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
# We mount 'app/templates' to '/static' so that index.html can access css/js via /static/style.css
app.mount("/static", StaticFiles(directory="app/templates"), name="static")

app.include_router(router)

@app.get("/")
async def root():
    return FileResponse('app/templates/index.html')

def start_server():
    print('Starting Server...')
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=True,
    )

if __name__ == "__main__":
    start_server()