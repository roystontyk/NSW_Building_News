import os, requests, time, sys, html
from bs4 import BeautifulSoup
from datetime import datetime

# === 🎛️ CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Critical NSW Building Commission URLs
NSW_URLS = [
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/news",
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/register-of-building-work-orders",
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/undertakings-building-and-construction",
    "https://www.fairtrading.nsw.gov.au/help-centre/online-tools/rab-act-orders-register"
]

def log(msg): 
    print(f"📝 {msg}", flush=True)

def send_telegram(text):
    if not text: return
    log("📤 Sending to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Split message if it exceeds Telegram's 4096 character limit
    for i in range(0, len(text), 4000):
        part = text[i:i+4000]
        requests.post(url, json={"chat_id": CHAT_ID, "text": part, "parse_mode": "HTML"}, timeout=30)

def get_nsw_data():
    log("🔍 Deep Scanning NSW Building Commission & Registers...")
    items = []
    
    # Keywords that indicate a legal work order or warning
    ORDER_KEYWORDS = ["prohibition order", "rectification order", "stop work order", "enforceable undertaking", "warning notice"]

    for url in NSW_URLS:
        try:
            r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
            soup = BeautifulSoup(r.content, "html.parser")
            
            # Focus on the main content area to ignore navigation menus
            main_content = soup.find('main') or soup.find('div', id='main-content') or soup
            
            # --- METHOD 1: Scan for Order Keywords in Blocks (for Registers) ---
            # This captures orders inside tables, cards, or accordions
            for block in main_content.find_all(['div', 'tr', 'li', 'article']):
                block_text = block.get_text(separator=" ").strip().lower()
                
                if any(k in block_text for k in ORDER_KEYWORDS):
                    a_tag = block.find('a', href=True)
                    if a_tag:
                        # Extract the most descriptive part of the text
                        raw_title = block.get_text(separator=" ").split('\n')[0].strip()
                        clean_title = (raw_title[:110] + '..') if len(raw_title) > 110 else raw_title
                        
                        href = a_tag['href']
                        full_url = href if href.startswith("http") else f"https://www.nsw.gov.au{href}"
                        
                        # Determine Label
                        label = "⚖️ ORDER"
                        if "undertaking" in block_text: label = "✍️ UNDERTAKING"
                        if "warning" in block_text: label = "⚠️ WARNING"
                        
                        items.append(f"• <b>[{label}]</b> {html.escape(clean_title)}\n🔗 {full_url}")

            # --- METHOD 2: Standard Link Scraping (for News) ---
            for a in main_content.find_all('a', href=True):
                title = a.get_text().strip()
                href = a['href']
                
                # Filter out obvious junk (Navigation and short text)
                junk = ["logout", "login", "account", "skip to", "holiday", "keyboard_arrow"]
                if any(x in title.lower() for x in junk) or len(title) < 22:
                    continue

                if "/news/" in href or "building-commission" in href:
                    full_url = href if href.startswith("http") else f"https://www.nsw.gov.au{href}"
                    # Avoid duplicates found by Method 1
                    if not any(full_url in item for item in items):
                        items.append(f"• <b>[📰 NEWS]</b> {html.escape(title)}\n🔗 {full_url}")

        except Exception as e:
            log(f"⚠️ Error scraping {url}: {e}")
            
    # Remove exact duplicates while preserving order
    return list(dict.fromkeys(items))

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID:
        log("❌ Missing Telegram Secrets (Check Repo Settings)")
        return

    log("🚀 Starting Monitor")
    nsw_updates = get_nsw_data()
    
    if nsw_updates:
        header = f"🏢 <b>NSW Building Commission Update</b>\n📅 {datetime.now().strftime('%d %b %Y')}\n\n"
        # Combine items, limiting to the 15 most recent/relevant
        body = "\n\n".join(nsw_updates[:15])
        send_telegram(header + body)
        log(f"✅ Report sent with {len(nsw_updates)} items.")
    else:
        log("🧐 No updates found. Page structure might have changed.")

if __name__ == "__main__":
    main()
