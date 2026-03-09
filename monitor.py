def get_nsw_data():
    log("🔍 Checking NSW Building Commission (Precise Mode)...")
    items = []
    for url in NSW_URLS:
        try:
            r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
            soup = BeautifulSoup(r.content, "html.parser")
            
            # 1. Focus ONLY on the main content area to avoid the top/bottom menus
            content_area = soup.find('main') or soup.find('div', id='main-content') or soup
            
            for a in content_area.find_all('a', href=True):
                title = a.get_text().strip()
                link = a['href']
                
                # 2. Strict Filter: Ignore navigation, holidays, and social links
                junk_keywords = [
                    "logout", "login", "account", "skip to", "holiday", 
                    "keyboard_arrow", "living in nsw", "education", 
                    "health", "aboriginal", "transport", "environment"
                ]
                if any(x in title.lower() for x in junk_keywords): continue
                if len(title) < 25: continue

                # 3. Path Validation: Only accept links related to the Commission or News
                # This stops it from grabbing general "NSW Government" links
                if not any(x in link for x in ["building-commission", "news", "work-orders"]):
                    continue
                
                full_url = link if link.startswith("http") else f"https://www.nsw.gov.au{link}"
                
                # Labeling
                label = "📰 NSW-NEWS"
                if "order" in link or "register-of-building" in link: label = "⚖️ ORDER"
                if "warning" in title.lower(): label = "⚠️ WARNING"
                
                items.append(f"• <b>[{label}]</b> {html.escape(title)}\n🔗 {full_url}")
        except Exception as e:
            log(f"⚠️ NSW URL Error {url}: {e}")
            continue
            
    # Remove duplicates while keeping order
    unique_items = []
    seen = set()
    for item in items:
        if item not in seen:
            unique_items.append(item)
            seen.add(item)
            
    return unique_items
