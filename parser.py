import re
import sys
from datetime import datetime, timedelta, timezone
from typing import Optional

from bs4 import BeautifulSoup

from config import OLX_ORIGIN
from models import Apartment

_UA_MONTHS = {
    "січня": 1, "лютого": 2, "березня": 3, "квітня": 4,
    "травня": 5, "червня": 6, "липня": 7, "серпня": 8,
    "вересня": 9, "жовтня": 10, "листопада": 11, "грудня": 12,
}


def _normalize_date(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return raw
    today = datetime.now(timezone.utc).date()
    if raw.startswith("Сьогодні"):
        return f"{today.day} {_month_name(today.month)} {today.year} р."
    if raw.startswith("Вчора"):
        yesterday = today - timedelta(days=1)
        return f"{yesterday.day} {_month_name(yesterday.month)} {yesterday.year} р."
    return raw


_UA_MONTH_NAMES = {v: k for k, v in _UA_MONTHS.items()}


def _month_name(month: int) -> str:
    return _UA_MONTH_NAMES[month]


def parse_price(raw: str) -> tuple[Optional[float], bool]:
    negotiable = "Договірна" in raw or "договірна" in raw
    m = re.match(r"[\d\s\xa0.,]+", raw.replace("\xa0", " "))
    if not m:
        return None, negotiable
    num_str = m.group(0).strip()
    num_str = num_str.replace(" ", "").replace(",", ".")
    parts = num_str.split(".")
    if len(parts) > 2:
        num_str = "".join(parts[:-1]) + "." + parts[-1]
    try:
        return float(num_str), negotiable
    except ValueError:
        return None, negotiable


def parse_location(raw: str) -> tuple[str, Optional[str], Optional[str]]:
    """Повертає (місто, район, дата)."""
    parts = raw.split(" - ", 1)
    location_part = parts[0].strip()
    date_part = _normalize_date(parts[1].strip() if len(parts) > 1 else None)

    if "," in location_part:
        city, district = location_part.split(",", 1)
        return city.strip(), district.strip(), date_part
    return location_part, None, date_part


def get_total_pages(soup: BeautifulSoup) -> int:
    page_links = soup.find_all("a", href=re.compile(r"[?&]page=\d+"))
    pages = []
    for a in page_links:
        m = re.search(r"[?&]page=(\d+)", a["href"])
        if m:
            pages.append(int(m.group(1)))
    return max(pages) if pages else 1


def parse_cards(soup: BeautifulSoup) -> list[Apartment]:
    cards = soup.find_all(attrs={"data-cy": "l-card"})
    apartments = []

    for card in cards:
        try:
            ad_id = card.get("id", "")

            title_el = card.find(attrs={"data-testid": "ad-card-title"})
            title_tag = title_el.find(["h4", "h6"]) if title_el else None
            title = (
                title_tag.get_text(strip=True)
                if title_tag
                else (title_el.get_text(strip=True) if title_el else "")
            )

            price_el = card.find(attrs={"data-testid": "ad-price"})
            price_raw = price_el.get_text(strip=True) if price_el else ""
            price_uah, negotiable = parse_price(price_raw)

            location_el = card.find(attrs={"data-testid": "location-date"})
            location_raw = location_el.get_text(strip=True) if location_el else ""
            city, district, posted_at = parse_location(location_raw)

            area_m2: Optional[str] = None
            for span in card.find_all("span"):
                text = span.get_text(strip=True)
                if "м²" in text:
                    area_m2 = text
                    break

            link = card.find("a", href=True)
            url = ""
            if link:
                href = link["href"]
                url = href if href.startswith("http") else OLX_ORIGIN + href

            apartments.append(Apartment(
                id=ad_id,
                title=title,
                price_raw=price_raw,
                price_uah=price_uah,
                negotiable=negotiable,
                area_m2=area_m2,
                district=district,
                city=city,
                listing_date=posted_at,
                url=url,
            ))
        except Exception as e:
            print(f"  Помилка картки {card.get('id', '?')}: {e}", file=sys.stderr)

    return apartments
