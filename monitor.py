import os, requests, time, sys, html
from bs4 import BeautifulSoup
from datetime import datetime

# === 🎛️ CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

NSW_URLS = [
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/news",
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/register-of-building-work-orders",
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/undertakings-building-and-construction"
]

def log(msg): 
    print(f"📝 {msg}", flush=True)

def send_telegram(text):
    if not text: return
    log("📤 Sending to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=30)

def clean_title(text):
    """Removes UI junk from the scraped titles."""
    junk = ["keyboard_arrow", "filter results", "back", "show results", "read more", "view details"]
    clean = text.lower()
    for j in junk:
        clean = clean.replace(j, "")
    # Remove dates often stuck to titles (e.g., '18 february 2026')
    for month in ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]:
        if month in clean:
            clean = clean.split(month)[-1].strip()
    return clean.strip().capitalize()

def get_nsw_data():
    log("🔍 Deep Scanning NSW Building Commission...")
    results = {} # Use dict to store Link: Label+Title to prevent duplicates
    
    ORDER_KEYWORDS = ["prohibition", "rectification", "stop work", "undertaking", "warning notice"]

    for url in NSW_URLS:
        try:
            r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
            soup = BeautifulSoup(r.content, "html.parser")
            
            # Lock onto the central content
            main_content = soup.find('main') or soup.find('div', id='main-content') or soup
            
            # --- METHOD 1: Card & List Scanning (For Orders & Undertakings) ---
            # NSW uses 'nsw-card' or 'nsw-list-item' usually
            for block in main_content.find_all(['div', 'tr', 'li', 'a']):
                href_tag = block if block.name == 'a' else block.find('a', href=True)
                if not href_tag or not href_tag.get('href'): continue
                
                full_text = block.get_text(separator=" ").strip()
                href = href_tag['href']
                if not href.startswith("http"): href = f"https://www.nsw.gov.au{href}"
                
                # Skip read-speaker or search utility links
                if "readspeaker" in href or "search?" in href: continue

                label = ""
                lower_text = full_text.lower()
                
                if "prohibition" in lower_text or "stop work" in lower_text: label = "⚖️ ORDER"
                elif "rectification" in lower_text: label = "🛠️ RECTIFICATION"
                elif "undertaking" in lower_text: label = "✍️ UNDERTAKING"
                elif "warning" in lower_text: label = "⚠️ WARNING"
                elif "/news/" in href and len(full_text) > 30: label = "📰 NEWS"

                if label:
                    # Clean the title: prioritize the text inside the <a> tag
                    title = clean_title(href_tag.get_text().strip() or full_text.split('\n')[0])
                    if len(title) > 15: # Ignore tiny fragments
                        results[href] = f"• <b>[{label}]</b> {html.escape(title)}\n🔗 {href}"

        except Exception as e:
            log(f"⚠️ Error on {url}: {e}")

    return list(results.values())

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID:
        log("❌ Missing Secrets")
        return

    nsw_updates = get_nsw_data()
    
    if nsw_updates:
        header = f"🏢 <b>NSW Building Commission Update</b>\n📅 {datetime.now().strftime('%d %b %Y')}\n\n"
        # Separate the items. We sort to put Warnings and Orders at the top.
        nsw_updates.sort(key=lambda x: ("ORDER" in x or "WARNING" in x), reverse=True)
        
        send_telegram(header + "\n\n".join(nsw_updates[:20]))
        log(f"✅ Report sent with {len(nsw_updates)} unique items.")
    else:
        log("🧐 No updates found.")

if __name__ == "__main__":
    main()
