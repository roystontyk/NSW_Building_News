import os, requests, time, sys, html
from bs4 import BeautifulSoup
from datetime import datetime

# === 🎛️ CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

VIC_URLS = ["https://www.consumer.vic.gov.au/latest-news", "https://cms9.consumer.vic.gov.au/RSS.aspx?RssType=newsalerts"]
NSW_URLS = ["https://www.nsw.gov.au/departments-and-agencies/building-commission/news", "https://www.nsw.gov.au/departments-and-agencies/building-commission/register-of-building-work-orders"]
ABS_API = "https://api.abs.gov.au/indicators/v1/indicators"

def log(msg): 
    print(f"📝 {msg}", flush=True)

def send_telegram(text):
    if not text: return
    log("📤 Sending to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=30)
    if r.status_code != 200: log(f"❌ Telegram Error: {r.text}")

def get_abs():
    log("📊 Checking ABS...")
    try:
        r = requests.get(ABS_API, timeout=20)
        data = r.json().get('data', [])
        found = []
        watchlist = ["Building", "Construction", "Lending", "CPI", "Property"]
        for item in data:
            name = item.get('indicator_name', '')
            if any(k in name for k in watchlist):
                link = f"https://www.abs.gov.au/statistics/indicators/{item.get('id', '')}"
                found.append(f"• <b>[ABS]</b> {html.escape(name)}\n🔗 {link}")
        return found[:5]
    except Exception as e:
        log(f"ABS Failed: {e}")
        return []

def get_nsw():
    log("🔍 Checking NSW...")
    items = []
    for url in NSW_URLS:
        try:
            r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
            soup = BeautifulSoup(r.content, "html.parser")
            # Target the main container specifically
            main = soup.find('main') or soup
            for a in main.find_all('a', href=True):
                title = a.get_text().strip()
                href = a['href']
                if len(title) < 25 or any(x in title.lower() for x in ["logout", "login", "account"]): continue
                
                # Broaden the filter slightly to ensure we catch items
                if any(x in href for x in ["building-commission", "news", "work-orders", "notice"]):
                    full_url = href if href.startswith("http") else f"https://www.nsw.gov.au{href}"
                    label = "⚖️ ORDER" if "order" in href else "📰 NSW"
                    items.append(f"• <b>[{label}]</b> {html.escape(title)}\n🔗 {full_url}")
        except Exception as e: log(f"NSW Error on {url}: {e}")
    return list(dict.fromkeys(items))[:10] # Unique items

def get_vic():
    log("🔍 Checking VIC...")
    items = []
    for url in VIC_URLS:
        try:
            r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
            # Use html.parser as fallback if lxml isn't installed
            soup = BeautifulSoup(r.content, "html.parser")
            for a in soup.find_all(['a', 'link']):
                # Handle both RSS <link> and HTML <a>
                href = a.get('href') or a.get_text()
                title = a.get_text().strip()
                if href and "/news/" in href and len(title) > 30:
                    full_url = href if href.startswith("http") else f"https://www.consumer.vic.gov.au{href}"
                    items.append(f"• <b>[VIC]</b> {html.escape(title)}\n🔗 {full_url.replace('cms9.', 'www.')}")
        except Exception as e: log(f"VIC Error: {e}")
    return list(dict.fromkeys(items))[:10]

def main():
    log("🚀 Starting Master Monitor")
    results = []
    
    abs_list = get_abs()
    if abs_list: results.append("<b>📊 ABS UPDATES</b>\n" + "\n\n".join(abs_list))
    
    nsw_list = get_nsw()
    if nsw_list: results.append("<b>🏢 NSW BUILDING COMMISSION</b>\n" + "\n\n".join(nsw_list))
    
    vic_list = get_vic()
    if vic_list: results.append("<b>🛍️ VIC CONSUMER AFFAIRS</b>\n" + "\n\n".join(vic_list))

    if results:
        msg = f"🚀 <b>Property & Construction Digest</b>\n📅 {datetime.now().strftime('%d %b %Y')}\n\n" + "\n\n---\n\n".join(results)
        send_telegram(msg)
        log("✅ Done!")
    else:
        log("🧐 Nothing new found.")

if __name__ == "__main__":
    main()
