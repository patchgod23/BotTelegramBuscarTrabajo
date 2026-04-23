from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, List
import os
import threading
import schedule
import time
import logging
try:
    from src.database import init_db, get_jobs
    from src.main import buscar_trabajos, load_config, save_config
except ImportError:
    try:
        from database import init_db, get_jobs
        from main import buscar_trabajos, load_config, save_config
    except ImportError:
        from .database import init_db, get_jobs
        from .main import buscar_trabajos, load_config, save_config

app = FastAPI(title="Job Search Bot Dashboard")

# Ensure data and static directories exist
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Initialize Database
init_db()

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/api/jobs")
async def fetch_jobs(
    platform: Optional[str] = None,
    limit: int = 50
):
    jobs = get_jobs(platform=platform, limit=limit)
    return jobs

@app.post("/api/scrape")
async def trigger_scrape(background_tasks: BackgroundTasks):
    background_tasks.add_task(buscar_trabajos)
    return {"message": "Búsqueda iniciada en segundo plano."}

@app.get("/api/config")
async def get_bot_config():
    return load_config()

@app.post("/api/config")
async def update_bot_config(new_config: dict):
    if save_config(new_config):
        return {"message": "Configuración actualizada con éxito."}
    return {"message": "Error al guardar la configuración."}, 500

# Background Bot Logic
def run_scheduler():
    config = load_config()
    if not config:
        logging.error("No se pudo cargar la configuración para el scheduler.")
        return

    minutos = config.get("SCHEDULE_MINUTES", 30)
    logging.info(f"Scheduler iniciado cada {minutos} minutos.")
    
    schedule.every(minutos).minutes.do(buscar_trabajos)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()
