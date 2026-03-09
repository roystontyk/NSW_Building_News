import os, requests, time, html
from bs4 import BeautifulSoup
from datetime import datetime

# === 🎛️ CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Targeted NSW URLs
NSW_SOURCES = {
    "NEWS": "https://www.nsw.gov.au/departments-and-agencies/building-commission/news",
    "ORDERS": "https://www.nsw.gov.au/departments-and-agencies/building-commission/register-of-building-work-orders",
    "UNDERTAKINGS": "https://www.nsw.gov.au/departments-and-agencies/fair-trading/how-we-regulate/enforceable-undertakings-register"
}

def log(msg): 
    print(f"🏢 [NSW-LOG] {msg}", flush=True)

def send_telegram(text):
    if not text: return
    log("📤 Sending to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    r = requests.post(url, json=payload, timeout=30)
    return r.status_code == 200

def scrape_nsw():
    all_items = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for category, url in NSW_SOURCES.items():
        log(f"🔍 Checking {category}...")
        try:
            r = requests.get(url, headers=headers, timeout=20)
            soup = BeautifulSoup(r.content, "html.parser")
            
            # Find links
            for a in soup.find_all('a', href=True):
                title = a.get_text().strip()
                link = a['href']
                
                # 1. JUNK FILTERS
                if any(x in title.lower() for x in ["logout", "login", "my account", "skip to", "menu", "privacy"]):
                    continue
                if len(title) < 20: 
                    continue
                
                # 2. URL CLEANUP
                full_url = link if link.startswith("http") else f"https://www.nsw.gov.au{link}"
                
                # 3. SMART LABELING
                label = f"📰 {category}"
                if "warning" in title.lower(): label = "⚠️ WARNING"
                if "prohibition" in title.lower(): label = "🚫 PROHIBITION"
                if "stop work" in title.lower(): label = "🛑 STOP WORK"
                if "rectification" in title.lower(): label = "🔧 RECTIFY"

                all_items.append(f"• <b>[{label}]</b> {html.escape(title)}\n🔗 {full_url}")
        except Exception as e:
            log(f"⚠️ Failed {category}: {e}")
            
    # Return unique items only
    return list(dict.fromkeys(all_items))

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID:
        log("❌ Missing Secrets!")
        return

    log("🚀 NSW Building Commission Monitor Started")
    updates = scrape_nsw()
    
    if updates:
        # Create the message
        header = f"🏢 <b>NSW Building Commission Update</b>\n"
        header += f"📅 <i>{datetime.now().strftime('%d %b %Y')}</i>\n\n"
        
        # Join items (Telegram limit check included)
        body = "\n\n".join(updates[:15]) # Get top 15 unique items
        send_telegram(header + body)
        log(f"✅ Sent {len(updates[:15])} items.")
    else:
        log("🧐 No updates found.")

if __name__ == "__main__":
    main()
