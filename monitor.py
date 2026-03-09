import os, requests, time, json, warnings, html
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# === 🎛️ CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CF_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
CF_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")

TARGET_URLS = [
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/news",
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/register-of-building-work-orders"
]

MAX_ITEMS = 15

def log(msg): 
    print(f"📝 [LOG] {msg}", flush=True)

def send_telegram(text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        log("❌ Missing Telegram Credentials")
        return
    if len(text) > 4000: text = text[:3950] + "\n\n...(truncated)"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        r = requests.post(url, json=data, timeout=30)
        return r.json()
    except Exception as e:
        log(f"✗ Telegram: {e}")
        return None

def clean_url(href, base):
    if not href: return base
    if href.startswith(('http://','https://')): return href
    return f"{base}{href}" if href.startswith('/') else f"{base}/{href}"

def scrape_nsw(url):
    try:
        log(f"🔍 Scraping: {url}")
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
        items, base = [], "https://www.nsw.gov.au"
        
        src = "NSW-ORDERS" if "register" in url else "NSW-NEWS"
        
        # NSW Government site specifically uses these patterns
        # We look for links that are inside 'nsw-card__title' or similar headings
        found_links = soup.find_all('a', href=True)
        
        seen_links = set()
        for lk in found_links:
            href = lk.get('href')
            title = lk.get_text().strip()
            
            # Filter for meaningful headlines (usually > 20 chars) 
            # and ignore common navigation links
            if len(title) > 20 and href not in seen_links:
                full_url = clean_url(href, base)
                
                # Keywords to ensure we're getting building-related content
                keywords = ['news', 'order', 'building', 'commission', 'levy', 'project', 'safety']
                if any(x in full_url.lower() or x in title.lower() for x in keywords):
                    seen_links.add(href)
                    items.append(f"• <b>[{src}]</b> {html.escape(title)}\n🔗 {full_url}")
            
            if len(items) >= MAX_ITEMS: break

        log(f"✅ Found {len(items)} items for {src}")
        return items
    except Exception as e:
        log(f"✗ Error at {url}: {e}")
        return []

def call_ai(text):
    if not CF_TOKEN or not CF_ACCOUNT_ID: 
        log("⚠️ No Cloudflare credentials, skipping AI summary.")
        return None
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/@cf/meta/llama-3-8b-instruct"
    headers = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}
    
    prompt = f"""Summarize these NSW Building Commission updates into a clean digest.
Rules: 1) Group by News and Work Orders. 2) Keep the links as provided. 3) Use emojis.
Content:
{text[:7000]}"""
    
    try:
        r = requests.post(url, headers=headers, json={"messages": [{"role": "user", "content": prompt}]}, timeout=90)
        return r.json()['result']['response'].strip()
    except Exception as e:
        log(f"✗ AI Error: {e}")
        return None

def main():
    log("🚀 NSW Scraper Started")
    all_items = []
    for u in TARGET_URLS:
        all_items.extend(scrape_nsw(u))
    
    if not all_items:
        log("⚠️ No new content found. Check URLs or selectors.")
        return

    raw_text = "\n\n".join(all_items)
    summary = call_ai(raw_text) or raw_text
    
    final_msg = f"🏢 <b>NSW Building Commission Update</b>\n📅 {time.strftime('%d %b %Y')}\n\n{summary}"
    send_telegram(final_msg)
    log("✅ Process Complete")

if __name__ == "__main__":
    main()
