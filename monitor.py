import os, requests, html
from bs4 import BeautifulSoup
from datetime import datetime

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# The only URLs you need
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
            
            # This 'main' tag ignores all the header/footer menu junk
            content = soup.find('main')
            if not content: continue

            for a in content.find_all('a', href=True):
                title = a.get_text().strip()
                link = a['href']
                
                # 1. Basic Filters to keep the list clean
                if len(title) < 15: continue
                if any(x in title.lower() for x in ["facebook", "linkedin", "twitter", "share", "back to"]): continue
                
                # 2. Fix relative links
                full_url = link if link.startswith("http") else f"https://www.nsw.gov.au{link}"
                
                # 3. Prevent duplicates
                if full_url not in seen_links:
                    # Label based on the page it came from
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
        # Combine everything into one message
        send_telegram(header + "\n\n".join(headlines[:25]))
        print("✅ Message sent.")
    else:
        print("🧐 No headlines found.")

if __name__ == "__main__":
    main()
