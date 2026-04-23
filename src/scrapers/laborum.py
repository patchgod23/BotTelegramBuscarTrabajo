import requests
import logging
from bs4 import BeautifulSoup
import urllib.parse
import re

def scrape_laborum(search_term):
    logging.info(f"[Laborum] Buscando '{search_term}'...")
    jobs_found = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
    }
    
    encoded_term = urllib.parse.quote_plus(search_term).replace('+', '-')
    url = f"https://www.laborum.cl/empleos-busqueda-{encoded_term}.html"
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        
        jobs = soup.find_all("a", href=True)
        
        for job in jobs:
            link = job["href"]
            if "-111" in link or re.search(r'-\d{6,}\.html$', link):
                if not link.startswith("http"):
                    full_link = "https://www.laborum.cl" + link
                else:
                    full_link = link
                
                title = job.text.strip()
                if not title:
                    header = job.find(['h2', 'h3'])
                    if header:
                        title = header.text.strip()
                
                if title and "laborum" not in title.lower():
                    jobs_found.append({
                        "title": title,
                        "url": full_link,
                        "platform": "Laborum"
                    })
    except Exception as e:
        logging.error(f"Error en scraper Laborum: {e}")
        
    return jobs_found
