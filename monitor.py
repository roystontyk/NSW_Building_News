import os, requests, html
from bs4 import BeautifulSoup
from datetime import datetime

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ✅ FIXED: No trailing spaces in URLs
NSW_URLS = [
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/news",
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/register-of-building-work-orders"
]

def send_telegram(text):
    if not text: 
        return
    # ✅ FIXED: No spaces in bot URL
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=30)

def get_nsw_data():
    print("🔍 Fetching headlines...")
    results = []
    seen_links = set()

    for url in NSW_URLS:
        try:
            r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
            soup = BeautifulSoup(r.content, "html.parser")
            
            # This 'main' tag ignores all the header/footer menu junk
            content = soup.find('main')
            if not content: 
                print(f"⚠️ No <main> tag found on {url}")
                continue

            # ✅ DETECT PAGE TYPE
            is_register = "register" in url
            
            if is_register:
                print(f"📋 Parsing Register page...")
                # Register page uses tables or definition lists
                # Look for table rows, list items, or links in the main content
                for elem in content.find_all(['tr', 'li', 'dt', 'dd']):
                    a = elem.find('a', href=True)
                    if a:
                        title = a.get_text().strip()
                        link = a['href']
                        
                        # Filter junk
                        if len(title) < 10: 
                            continue
                        if any(x in title.lower() for x in ["facebook", "linkedin", "twitter", "share", "back to", "top of page", "skip"]): 
                            continue
                        
                        # Fix relative links
                        full_url = link if link.startswith("http") else f"https://www.nsw.gov.au{link}"
                        
                        # Prevent duplicates
                        if full_url not in seen_links and "nsw.gov.au" in full_url:
                            results.append(f"• <b>[⚖️ ORDER]</b> {html.escape(title)}\n🔗 {full_url}")
                            seen_links.add(full_url)
                
                # Fallback: grab all links in main that look like order titles
                if len(results) == 0:
                    print("🔍 Fallback: scanning all links in register page...")
                    for a in content.find_all('a', href=True):
                        title = a.get_text().strip()
                        link = a['href']
                        
                        if len(title) < 15: 
                            continue
                        if any(x in title.lower() for x in ["facebook", "linkedin", "twitter", "share", "back to", "home", "contact", "menu"]): 
                            continue
                        
                        full_url = link if link.startswith("http") else f"https://www.nsw.gov.au{link}"
                        
                        if full_url not in seen_links and "register" in full_url and "nsw.gov.au" in full_url:
                            results.append(f"• <b>[⚖️ ORDER]</b> {html.escape(title)}\n🔗 {full_url}")
                            seen_links.add(full_url)
            
            else:
                # News page - original logic
                print(f"📰 Parsing News page...")
                for a in content.find_all('a', href=True):
                    title = a.get_text().strip()
                    link = a['href']
                    
                    # Basic Filters to keep the list clean
                    if len(title) < 15: 
                        continue
                    if any(x in title.lower() for x in ["facebook", "linkedin", "twitter", "
