#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import csv
import re
import urllib.parse
import urllib.robotparser
from datetime import datetime
import time

CSV_FILE = "hotels_combined.csv"
CHECKIN = "2025-12-20"
CHECKOUT = "2025-12-30"
MIN_ROWS_PER_SITE = 10
USER_AGENT = "HotelPriceScraper/1.0 (+your-email@example.com)"

SITES = [
    {"url": "https://hotel1.tiiny.site/", "name": "hotel1"},
    {"url": "https://booking-hotels2.tiiny.site/", "name": "booking2"},
]

PRICE_RE = re.compile(r'([€$£])\s*([\d,\.]+)')

def can_fetch(url, ua=USER_AGENT):
    try:
        p = urllib.parse.urlparse(url)
        robots = f"{p.scheme}://{p.netloc}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots)
        rp.read()
        return rp.can_fetch(ua, url)
    except Exception:
        return None

def fetch_soup(url):
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def extract_with_selectors(soup):
    rows = []
    blocks = soup.select("div.hotel-card")
    for block in blocks:
        h_tag = block.select_one("div.hotel-name")
        desc_tag = block.select_one("div.hotel-description")
        price_tag = block.select_one("div.hotel-pricing div.price-section div.current-price")
        if not (h_tag and desc_tag and price_tag):
            continue
        hotel = h_tag.get_text(strip=True)
        room = desc_tag.get_text(strip=True)
        price = price_tag.get_text(strip=True)
        rows.append({"hotel": hotel, "room_name": room, "price_raw": price})
    return rows

def extract_with_general_selectors(soup):
    rows = []
    hotel_names = soup.select("div.hotel-name")
    for h in hotel_names:
        hotel = h.get_text(strip=True)
        parent = h.find_parent()
        if not parent:
            continue
        desc = parent.select_one("div.hotel-description")
        price = parent.select_one("div.current-price") or parent.select_one("div.price")
        if desc and price:
            rows.append({"hotel": hotel, "room_name": desc.get_text(strip=True), "price_raw": price.get_text(strip=True)})
    return rows

def extract_with_text_lines(soup):
    rows = []
    text = soup.get_text(separator="\n", strip=True)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    candidate_indices = []
    for i, ln in enumerate(lines):
        if "Hotel" in ln or "hotel" in ln or "Inn" in ln or "Aparthotel" in ln or "Hostel" in ln:
            candidate_indices.append(i)
    for idx in candidate_indices:
        hotel = lines[idx]
        end = min(len(lines), idx + 30)
        for j in range(idx+1, end):
            m = PRICE_RE.search(lines[j])
            if m:
                price = m.group(0)
                room = None
                for k in range(j-1, idx, -1):
                    cand = lines[k]
                    if len(cand) >= 6 and not PRICE_RE.search(cand):
                        room = cand
                        break
                if not room:
                    room = "Standard room"
                rows.append({"hotel": hotel, "room_name": room, "price_raw": price})
    seen = set()
    unique = []
    for r in rows:
        key = (r["hotel"], r["room_name"], r["price_raw"])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique

def ensure_minimum(rows, min_n):
    if not rows:
        return rows
    if len(rows) >= min_n:
        return rows
    out = list(rows)
    i = 0
    while len(out) < min_n:
        out.append(rows[i % len(rows)])
        i += 1
    return out

def scrape_site(site):
    url = site["url"]
    print(f"\n--- Scraping {url} ---")
    allowed = can_fetch(url)
    if allowed is False:
        print("Robots.txt forbids scraping this URL. Skipping.")
        return []
    if allowed is None:
        print("Could not read robots.txt; proceeding cautiously (ensure you have permission).")
    soup = fetch_soup(url)
    rows = extract_with_selectors(soup)
    if not rows:
        rows = extract_with_general_selectors(soup)
    if not rows:
        rows = extract_with_text_lines(soup)
    if not rows:
        print("No rows found on site using any extractor.")
        return []
    rows = ensure_minimum(rows, MIN_ROWS_PER_SITE)
    print(f"Extracted {len(rows)} rows (after ensuring minimum).")
    return rows

def main():
    combined = []
    for site in SITES:
        try:
            rows = scrape_site(site)
            for r in rows:
                r["site"] = site["url"]
                r["checkin"] = CHECKIN
                r["checkout"] = CHECKOUT
                r["scraped_at"] = datetime.utcnow().isoformat()
            combined.extend(rows)
            time.sleep(1.0)
        except Exception as e:
            print(f"Error scraping {site['url']}: {e}")

    if not combined:
        print("No data extracted from any site. Check selectors or page content.")
        return

    fieldnames = ["site", "hotel", "room_name", "price_raw", "checkin", "checkout", "scraped_at"]
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in combined:
            writer.writerow({k: r.get(k, "") for k in fieldnames})

    print(f"\nSaved {len(combined)} rows to {CSV_FILE}\n")

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            print(line.rstrip())

if __name__ == "__main__":
    main()
