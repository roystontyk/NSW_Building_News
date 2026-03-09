import os, requests, time, json, warnings, html
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# === 🎛️ CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CF_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
CF_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")

# ✅ NSW BUILDING COMMISSION SOURCES
TARGET_URLS = [
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/news",
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/register-of-building-work-orders"
]

MAX_ITEMS = 15

def log(msg): print(f"📝 [LOG] {msg}", flush=True)

def send_telegram(text):
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
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
        items, base = [], "https://www.nsw.gov.au"
        
        # 1. Scraping News Section
        if "/news" in url:
            src = "NSW-NEWS"
            # NSW Gov uses nsw-card or views-row for news items
            for card in soup.select('.nsw-card, .views-row'):
                link_tag = card.find('a', href=True)
                if link_tag:
                    title = link_tag.get_text().strip()
                    href = link_tag['href']
                    full_url = clean_url(href, base)
                    if len(title) > 20:
                        items.append(f"📰 [{src}] {html.escape(title)}\n🔗 {full_url}")
                if len(items) >= MAX_ITEMS: break

        # 2. Scraping Work Orders Register (Table or List)
        elif "/register-of-building-work-orders" in url:
            src = "NSW-ORDERS"
            # Often these registers are in table rows or specific card lists
            for row in soup.select('tr, .nsw-list-item'):
                link_tag = row.find('a', href=True)
                if link_tag:
                    text = link_tag.get_text().strip()
                    href = link_tag['href']
                    full_url = clean_url(href, base)
                    if "order" in text.lower() or "building" in text.lower():
                        items.append(f"⚖️ [{src}] {html.escape(text)}\n🔗 {full_url}")
                if len(items) >= MAX_ITEMS: break

        return items
    except Exception as e:
        log(f"✗ Error at {url}: {e}")
        return []

def call_ai(text):
    if not CF_TOKEN or not CF_ACCOUNT_ID: return None
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/@cf/meta/llama-3-8b-instruct"
    headers = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}
    
    prompt = f"""NSW Building Commission updates. Focus on news, reforms, and building work orders.
Rules: 1) Link EVERY item 2) Labels [NSW-NEWS], [NSW-ORDERS] 3) Bullets+emojis 4) Short summaries.
Content:
{text[:7000]}
Format:
🏙️ <b>NSW Building News</b>
• [Summary] 🔗 [URL]
⚖️ <b>Work Orders Register</b>
• [Summary] 🔗 [URL]"""
    
    try:
        r = requests.post(url, headers=headers, json={"messages": [{"role": "user", "content": prompt}], "max_tokens": 1000}, timeout=90)
        return r.json()['result']['response'].strip()
    except Exception as e:
        log(f"✗ AI: {e}")
        return None

def main():
    log("🚀 NSW Scraper Started")
    all_content = []
    for u in TARGET_URLS:
        all_content.extend(scrape_nsw(u))
    
    if not all_content:
        log("⚠️ No new content found.")
        return

    # Join the content for AI processing
    raw_text = "\n\n".join(all_content)
    summary = call_ai(raw_text) or raw_text[:3500]
    
    final_msg = f"🏢 <b>NSW Building Commission Update</b>\n📅 {time.strftime('%d %b %Y')}\n\n{summary}"
    send_telegram(final_msg)
    log("✅ Finished")

if __name__ == "__main__":
    main()
