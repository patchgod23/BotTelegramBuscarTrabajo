import json
import time
import schedule
import requests
import os
import logging
from dotenv import load_dotenv

# Relative imports from src
try:
    from .database import init_db, is_job_seen, mark_job_seen
    from .ranking import calculate_ranking
    from .scrapers.getonboard import scrape_getonboard
    from .scrapers.laborum import scrape_laborum
    from .scrapers.linkedin import scrape_linkedin
    from .scrapers.computrabajo import scrape_computrabajo
except ImportError:
    # If running as script
    from database import init_db, is_job_seen, mark_job_seen
    from ranking import calculate_ranking
    from scrapers.getonboard import scrape_getonboard
    from scrapers.laborum import scrape_laborum
    from scrapers.linkedin import scrape_linkedin
    from scrapers.computrabajo import scrape_computrabajo

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

# Cargar variables de entorno - .env está en la raíz
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def load_config():
    # config.json está en la raíz
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error cargando config.json: {e}")
        return None

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        logging.warning("Configuración de Telegram incompleta (.env).")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Error enviando mensaje a Telegram: {e}")

def process_job(job, keywords, exclude_terms):
    title = job["title"]
    url = job["url"]
    platform = job["platform"]

    if is_job_seen(url):
        return False

    title_lower = title.lower()
    if any(ex.lower() in title_lower for ex in exclude_terms):
        mark_job_seen(url, title, platform)
        return False

    rank = calculate_ranking(title, keywords)

    if rank > 3:
        mensaje = (
            f"🏢 <b>Nuevo trabajo en {platform}</b>\n"
            f"🔹 <i>{title}</i>\n"
            f"⭐ <b>Ranking: {rank}</b> pts\n\n"
            f"🔗 <a href='{url}'>Ver oferta</a>"
        )
        logging.info(f"Enviando: {title} (Ranking: {rank})")
        send_telegram(mensaje)
        time.sleep(1.5)
        mark_job_seen(url, title, platform)
        return True
    
    mark_job_seen(url, title, platform)
    return False

def buscar_trabajos():
    logging.info("Iniciando búsqueda de trabajos...")
    
    config = load_config()
    if not config:
        return

    keywords = config.get("KEYWORDS", {})
    search_terms = config.get("SEARCH_TERMS", ["python"])
    exclude_terms = config.get("EXCLUDE_TERMS", [])

    all_jobs = []
    scrapers = [
        scrape_getonboard,
        scrape_laborum,
        scrape_linkedin,
        scrape_computrabajo
    ]

    for term in search_terms:
        for scraper in scrapers:
            try:
                all_jobs.extend(scraper(term))
            except Exception as e:
                logging.error(f"Error en scraper {scraper.__name__} para '{term}': {e}")

    nuevos_procesados = 0
    mensajes_enviados = 0

    for job in all_jobs:
        nuevos_procesados += 1
        if process_job(job, keywords, exclude_terms):
            mensajes_enviados += 1

    logging.info(f"Búsqueda finalizada. Procesados: {nuevos_procesados}, Enviados: {mensajes_enviados}")

def main():
    init_db()
    
    config = load_config()
    if not config:
        logging.error("No se pudo cargar la configuración. Saliendo.")
        return

    minutos = config.get("SCHEDULE_MINUTES", 30)
    logging.info(f"🚀 Bot iniciado. Frecuencia: {minutos} minutos.")
    
    buscar_trabajos()

    schedule.every(minutos).minutes.do(buscar_trabajos)

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Bot detenido por el usuario.")
            break
        except Exception as e:
            logging.error(f"Error inesperado en el loop principal: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
