import os, requests, html
from bs4 import BeautifulSoup
from datetime import datetime

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# The URLs we scrape for live headlines
NSW_URLS = [
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/news",
    "https://www.nsw.gov.au/departments-and-agencies/building-commission/register-of-building-work-orders"
]

def send_telegram(text):
    if not text: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    # Post the message
    requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=30)

def get_nsw_data():
    print("🔍 Fetching live headlines...")
    results = []
    seen_links = set()

    for url in NSW_URLS:
        try:
            r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
            soup = BeautifulSoup(r.content, "html.parser")
            
            # Focus on the main content to avoid menu/footer junk
            content = soup.find('main')
            if not content: continue

            for a in content.find_all('a', href=True):
                title = a.get_text().strip()
                link = a['href']
                
                # 1. CLEANING: Skip navigation junk and short fragments
                lower_title = title.lower()
                junk = ["logout", "login", "top of page", "skip to", "back to", "facebook", "linkedin", "twitter"]
                if any(x in lower_title for x in junk) or len(title) < 15:
                    continue
                
                # 2. FIX LINKS: Ensure they are absolute URLs
                full_url = link if link.startswith("http") else f"https://www.nsw.gov.au{link}"
                
                # 3. PREVENT DUPLICATES: Only add if we haven't seen this URL yet
                if full_url not in seen_links:
                    label = "⚖️ ORDER/REG" if "register" in url else "📰 NEWS"
                    results.append(f"• <b>[{label}]</b> {html.escape(title)}\n🔗 {full_url}")
                    seen_links.add(full_url)

        except Exception as e:
            print(f"Error on {url}: {e}")
            
    return results

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Missing Telegram Secrets!")
        return

    headlines = get_nsw_data()
    
    # 🏢 HEADER
    header = f"🏢 <b>NSW Building Commission Update</b>\n📅 {datetime.now().strftime('%d %b %Y')}\n\n"
    
    # 📝 SCRAPED CONTENT
    if headlines:
        body = "\n\n".join(headlines[:15]) # Top 15 items
    else:
        body = "🧐 <i>No new headlines found today. Check the direct links below for manual verification.</i>"

    # 🔗 PERMANENT RESOURCE LINKS (Your Requested Update)
    footer = (
        "\n\n---\n"
        "<b>📂 PERMANENT REGISTERS (Direct Access):</b>\n\n"
        "⚖️ <b>Building Work Orders (RAB Act):</b>\n"
        "https://www.fairtrading.nsw.gov.au/help-centre/online-tools/rab-act-orders-register\n\n"
        "✍️ <b>Enforceable Undertakings Register:</b>\n"
        "https://www.nsw.gov.au/departments-and-agencies/fair-trading/how-we-regulate/enforceable-undertakings-register\n\n"
        "📢 <b>Latest Media Warnings:</b>\n"
        "https://www.nsw.gov.au/departments-and-agencies/building-commission/news"
    )

    # COMBINE AND SEND
    send_telegram(header + body + footer)
    print("✅ Final message with footer links sent.")

if __name__ == "__main__":
    main()
