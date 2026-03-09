import os, requests, time, sys, html
from bs4 import BeautifulSoup
from datetime import datetime

# === 🎛️ CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# The URLs that matter. Added the Fair Trading PDF register specifically.
NSW_URLS = [
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/news",
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/register-of-building-work-orders",
    "https://www.fairtrading.nsw.gov.au/help-centre/online-tools/rab-act-orders-register",
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/undertakings-building-and-construction"
]

def log(msg): 
    print(f"📝 {msg}", flush=True)

def send_telegram(text):
    if not text: return
    log("📤 Sending to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    # Split long messages to avoid 4096 char limit
    for i in range(0, len(text), 4000):
        part = text[i:i+4000]
        requests.post(url, json={"chat_id": CHAT_ID, "text": part, "parse_mode": "HTML"}, timeout=30)

def get_nsw_data():
    log("🔍 Scraping NSW Building Commission & Work Order Registers...")
    results = {}
    
    # These keywords help us identify the specific legal documents you need
    LEGAL_KEYWORDS = ["prohibition", "rectification", "stop work", "undertaking", "warning", "rab act"]

    for url in NSW_URLS:
        try:
            r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
            soup = BeautifulSoup(r.content, "html.parser")
            
            # Target the main content area
            main_content = soup.find('main') or soup.find('div', id='main-content') or soup
            
            # Find all links on the page
            for a in main_content.find_all('a', href=True):
                title = a.get_text().strip()
                href = a['href']
                
                # Normalize link
                if not href.startswith("http"):
                    href = f"https://www.nsw.gov.au{href}"
                
                # Junk Filter
                if any(x in title.lower() for x in ["logout", "login", "account", "skip to", "back", "back to"]):
                    continue
                if "readspeaker" in href or "search?" in href:
                    continue

                # 1. SPECIAL LOGIC FOR REGISTERS: Capture PDF links and specific addresses
                is_legal_doc = any(k in href.lower() or k in title.lower() for k in LEGAL_KEYWORDS)
                is_pdf = href.endswith(".pdf")
                
                if is_legal_doc:
                    label = "⚖️ ORDER"
                    if "undertaking" in href.lower() or "undertaking" in title.lower(): label = "✍️ UNDERTAKING"
                    if "warning" in title.lower(): label = "⚠️ WARNING"
                    
                    # If the title is empty (common for PDFs), try to get it from the surrounding text
                    if not title or len(title) < 5:
                        parent_text = a.find_parent().get_text().strip()
                        title = parent_text.split("\n")[0][:100]

                    results[href] = f"• <b>[{label}]</b> {html.escape(title)}\n🔗 {href}"

                # 2. LOGIC FOR NEWS:
                elif "/news/" in href and len(title) > 30:
                    results[href] = f"• <b>[📰 NEWS]</b> {html.escape(title)}\n🔗 {href}"

        except Exception as e:
            log(f"⚠️ Error on {url}: {e}")

    return list(results.values())

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID:
        log("❌ Missing Secrets")
        return

    nsw_updates = get_nsw_data()
    
    if nsw_updates:
        # Sort so Orders/Undertakings are always first
        nsw_updates.sort(key=lambda x: ("ORDER" in x or "UNDERTAKING" in x or "WARNING" in x), reverse=True)
        
        header = f"🏢 <b>NSW Building Commission Update</b>\n📅 {datetime.now().strftime('%d %b %Y')}\n\n"
        send_telegram(header + "\n\n".join(nsw_updates[:25]))
        log("✅ Report sent.")
    else:
        log("🧐 No updates found.")

if __name__ == "__main__":
    main()
