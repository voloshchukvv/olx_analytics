import sys
from typing import Optional

import requests

from config import BASE_URL, HEADERS


def fetch_page(page: int, session: requests.Session) -> Optional[str]:
    params: dict = {"currency": "UAH"}
    if page > 1:
        params["page"] = page
    try:
        resp = session.get(BASE_URL, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"  Помилка завантаження сторінки {page}: {e}", file=sys.stderr)
        return None
