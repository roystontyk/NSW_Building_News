import os, requests, html
from bs4 import BeautifulSoup
from datetime import datetime

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# UPDATED: Direct URLs to the actual lists
NSW_URLS = [
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/news",
    # The actual order register often lives on this Fair Trading URL:
    "https://www.fairtrading.nsw.gov.au/help-centre/online-tools/rab-act-orders-register"
]

def send_telegram(text):
    if not text: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    # Added error logging for the post request
    response = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=30)
    if response.status_code != 200:
        print(f"❌ Telegram Error: {response.text}")

def get_nsw_data():
    print("🔍 Fetching headlines...")
    results = []
    seen_links = set()

    for url in NSW_URLS:
        try:
            r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
            soup = BeautifulSoup(r.content, "html.parser")
            
            # Use a broader search: find all 'a' tags, then filter by their location or class
            for a in soup.find_all('a', href=True):
                title = a.get_text().strip()
                link = a['href']
                
                # REFINED FILTERS:
                # 1. Ignore links with no text or very short junk text
                if len(title) < 10: continue
                
                # 2. Kill social media and navigational junk
                junk_keywords = ["facebook", "linkedin", "twitter", "share", "back to", "view menu", "skip to"]
                if any(x in title.lower() for x in junk_keywords): continue
                
                # 3. Fix relative links
                full_url = link if link.startswith("http") else f"https://www.nsw.gov.au{link}"
                if "fairtrading" in url and not full_url.startswith("http"):
                    full_url = f"https://www.fairtrading.nsw.gov.au{link}"
                
                # 4. Filter for relevant keywords to avoid grabbing random site links
                relevant = ["order", "news", "warning", "rectification", "prohibition", "building", "undertaking"]
                if not any(k in title.lower() or k in full_url.lower() for k in relevant):
                    continue

                # 5. Prevent duplicates
                if full_url not in seen_links:
                    label = "⚖️ ORDER" if "order" in full_url.lower() or "register" in url else "📰 NEWS"
                    results.append(f"• <b>[{label}]</b> {html.escape(title)}\n🔗 {full_url}")
                    seen_links.add(full_url)

        except Exception as e:
            print(f"Error on {url}: {e}")
            
    return results

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Missing Secrets!")
        return

    headlines = get_nsw_data()
    
    if headlines:
        header = f"🏢 <b>NSW Building Commission Update</b>\n📅 {datetime.now().strftime('%d %b %Y')}\n\n"
        # Combine items, limiting to top 20 to avoid Telegram message size limits
        send_telegram(header + "\n\n".join(headlines[:20]))
        print(f"✅ Message sent with {len(headlines[:20])} items.")
    else:
        print("🧐 No headlines found.")

if __name__ == "__main__":
    main()
