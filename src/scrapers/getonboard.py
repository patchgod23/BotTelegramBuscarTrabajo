import requests
import logging
from bs4 import BeautifulSoup
import urllib.parse

def scrape_getonboard(search_term):
    logging.info(f"[GetOnBoard] Buscando '{search_term}'...")
    jobs_found = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    encoded_term = urllib.parse.quote_plus(search_term)
    url = f"https://www.getonbrd.com/jobs?search={encoded_term}"
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        
        jobs = soup.find_all("a")
        
        for job in jobs:
            title = job.text.strip()
            link = job.get("href")
            
            if link and "/jobs/" in link and "getonbrd.com" not in link:
                full_link = "https://www.getonbrd.com" + link
                
                clean_title = title.split('\n')[0].strip() if '\n' in title else title
                
                jobs_found.append({
                    "title": clean_title,
                    "url": full_link,
                    "platform": "GetOnBoard"
                })
    except Exception as e:
        logging.error(f"Error en scraper GetOnBoard: {e}")
        
    return jobs_found
