import os, requests, html
from bs4 import BeautifulSoup
from datetime import datetime

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

NSW_URLS = [
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/news",
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/register-of-building-work-orders"
]

def send_telegram(text):
    if not text: return
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
            
            # Lock onto 'main' to avoid header/footer menus
            content = soup.find('main')
            if not content: continue

            for a in content.find_all('a', href=True):
                title = a.get_text().strip()
                link = a['href']
                
                # 1. CLEANING JUNK: Skip logout, login, and tiny menu links
                lower_title = title.lower()
                junk = ["logout", "my account", "login", "skip to", "back to", "department", "facebook", "linkedin", "twitter"]
                if any(x in lower_title for x in junk) or len(title) < 15:
                    continue
                
                # 2. FIX LINKS
                full_url = link if link.startswith("http") else f"https://www.nsw.gov.au{link}"
                
                # 3. RELEVANCE: Only grab links that look like articles or orders
                # This stops it from grabbing "Building Commission" (the page title link)
                path = full_url.lower()
                is_relevant = any(x in path for x in ["/news/", "/register-of-building-work-orders/", "order-", "rectification"])
                
                if is_relevant and full_url not in seen_links:
                    # Final check: Don't grab the page we are currently on
                    if full_url.strip('/') == url.strip('/'):
                        continue
                        
                    label = "⚖️ ORDER" if "register" in url else "📰 NEWS"
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
        # Combine items, limiting to top 20
        send_telegram(header + "\n\n".join(headlines[:20]))
        print(f"✅ Sent {len(headlines)} items.")
    else:
        print("🧐 No new headlines found.")

if __name__ == "__main__":
    main()
