import os, requests, html
from bs4 import BeautifulSoup
from datetime import datetime

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Direct links to the actual lists
NSW_URLS = [
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/news",
    # This is the actual database where the addresses and orders live:
    "https://www.fairtrading.nsw.gov.au/help-centre/online-tools/rab-act-orders-register"
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
            
            # This identifies the middle of the page and skips the header/footer menus
            content_area = soup.find('main') or soup.find('div', id='main-content') or soup
            
            for a in content_area.find_all('a', href=True):
                title = a.get_text().strip()
                link = a['href']
                
                # 1. Skip tiny links or navigation junk like "Logout"
                if len(title) < 12 or any(x in title.lower() for x in ["logout", "my account", "login", "skip to"]):
                    continue
                
                # 2. Fix relative links to be full URLs
                full_url = link if link.startswith("http") else f"https://www.nsw.gov.au{link}"
                if "fairtrading" in url and not link.startswith("http"):
                    full_url = f"https://www.fairtrading.nsw.gov.au{link}"
                
                # 3. Prevent duplicates
                if full_url not in seen_links:
                    # Label based on the page it came from
                    label = "⚖️ ORDER" if "order" in full_url.lower() or "fairtrading" in url else "📰 NEWS"
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
        # Combine items, limiting to top 20 to avoid Telegram character limits
        send_telegram(header + "\n\n".join(headlines[:20]))
        print("✅ Report sent.")
    else:
        print("🧐 No headlines found.")

if __name__ == "__main__":
    main()
