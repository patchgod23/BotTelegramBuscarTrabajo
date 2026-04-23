import requests
import logging
from bs4 import BeautifulSoup
import urllib.parse
import re

def scrape_computrabajo(search_term):
    logging.info(f"[Computrabajo] Buscando '{search_term}'...")
    jobs_found = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-CL,es;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://cl.computrabajo.com/"
    }
    
    # Computrabajo format: cl.computrabajo.com/trabajos-de-python
    # For multiple words: trabajos-de-backend-developer
    formatted_term = urllib.parse.quote_plus(search_term).replace('+', '-')
    url = f"https://cl.computrabajo.com/trabajos-de-{formatted_term}?pubdate=7"
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Computrabajo uses articles with class 'box_offer' or similar. 
        # Inside there's an <a> tag with class 'js-o-link'
        links = soup.find_all("a", class_="js-o-link")
        
        if not links: # fallback
            # Look for typical job links 
            links = soup.find_all("a", href=re.compile(r'/ofertas-de-trabajo/'))
            
        for link in links:
            title = link.text.strip()
            href = link.get("href")
            if href:
                if not href.startswith("http"):
                    href = "https://cl.computrabajo.com" + href
                
                # Check for uniqueness if there are duplicate links on the page
                jobs_found.append({
                    "title": title,
                    "url": href,
                    "platform": "Computrabajo"
                })
                
    except Exception as e:
        logging.error(f"Error en scraper Computrabajo: {e}")
        
    return jobs_found
