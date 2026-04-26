"""
OLX.ua parser — довгострокова оренда квартир у Києві.

Запуск:
    python main.py                  # всі сторінки
    python main.py --pages 10       # перші 10 сторінок
    python main.py --output result  # базова назва файлу виводу
"""

import argparse
import random
import time

import requests
from bs4 import BeautifulSoup

from fetcher import fetch_page
from parser import get_total_pages, parse_cards
from storage import save_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="OLX.ua парсер квартир (Київ)")
    parser.add_argument("--pages", type=int, default=None, help="Кількість сторінок (default: всі)")
    parser.add_argument("--output", default="apartments", help="Базова назва файлу виводу")
    args = parser.parse_args()

    session = requests.Session()
    all_apartments = []
    seen_ids: set[str] = set()
    total_pages = 1
    page = 1

    print("Починаємо парсинг OLX.ua — оренда квартир, Київ...\n")

    while True:
        if args.pages is not None and page > args.pages:
            break
        if page > total_pages:
            break

        print(f"Сторінка {page}/{total_pages}...")
        html = fetch_page(page, session)
        if not html:
            break

        soup = BeautifulSoup(html, "lxml")

        if page == 1:
            total_pages = get_total_pages(soup)
            print(f"Всього сторінок: {total_pages}\n")

        apartments = parse_cards(soup)
        if not apartments:
            print("  Оголошень не знайдено.")
            break

        new_count = 0
        for apt in apartments:
            if apt.id and apt.id in seen_ids:
                continue
            if apt.id:
                seen_ids.add(apt.id)
            all_apartments.append(apt)
            new_count += 1

        print(f"  +{new_count} оголошень (всього: {len(all_apartments)})")

        if page >= total_pages:
            break

        page += 1
        time.sleep(random.uniform(1.5, 3.0))

    if not all_apartments:
        print("\nНічого не знайдено.")
        return

    csv_path = f"{args.output}.csv"
    save_csv(all_apartments, csv_path)

    print(f"\nГотово! Зібрано {len(all_apartments)} оголошень.")
    print(f"  CSV  : {csv_path}")

    prices = [a.price_uah for a in all_apartments if a.price_uah]
    if prices:
        print("\nЦіни (грн/міс):")
        print(f"  Мін:     {min(prices):>12,.0f}")
        print(f"  Макс:    {max(prices):>12,.0f}")
        print(f"  Середня: {sum(prices)/len(prices):>12,.0f}")


if __name__ == "__main__":
    main()
