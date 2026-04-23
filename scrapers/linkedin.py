import requests
import logging
from bs4 import BeautifulSoup
import urllib.parse
import re

def scrape_linkedin(search_term):
    logging.info(f"[LinkedIn] Buscando '{search_term}'...")
    jobs_found = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9",
    }
    
    encoded_term = urllib.parse.quote_plus(search_term)
    # Buscamos en todo el mundo o Chile por defecto, la URL base no requiere login para las primeras pages
    url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_term}&location=Chile&f_TPR=r604800"
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        
        # LinkedIn usa <li> con la clase base-card 
        cards = soup.find_all("div", class_="base-search-card__info")
        links = soup.find_all("a", class_="base-card__full-link")
        
        # Sometimes structure varies. Let's look for standard a href in results if cards fails
        if not links:
            links = soup.find_all("a", href=True)
            for link in links:
                href = link['href']
                if '/jobs/view/' in href:
                    title = link.text.strip()
                    # clean title
                    title = re.sub(r'[\r\n\t]+', ' ', title).strip()
                    if title:
                        jobs_found.append({
                            "title": title,
                            "url": href.split('?')[0], # Remove params
                            "platform": "LinkedIn"
                        })
        else:
            for link in links:
                title = link.text.strip()
                title = re.sub(r'[\r\n\t]+', ' ', title).strip()
                href = link['href'].split('?')[0]
                jobs_found.append({
                    "title": title,
                    "url": href,
                    "platform": "LinkedIn"
                })
                
    except Exception as e:
        logging.error(f"Error en scraper LinkedIn: {e}")
        
    return jobs_found
