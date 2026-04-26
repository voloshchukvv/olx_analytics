# OLX Kyiv Apartment Rental Parser

A pet project for scraping and analyzing long-term apartment rental listings in Kyiv from [OLX.ua](https://www.olx.ua).

## What it does

Collects apartment listings from OLX, saves them to CSV, and generates charts to explore the rental market.

## Project structure

```
olx_parser/
├── config.py       — URLs and request headers
├── models.py       — Apartment dataclass
├── fetcher.py      — HTTP layer
├── parser.py       — HTML parsing
├── storage.py      — CSV export
├── main.py         — CLI entrypoint
└── analytics/
    └── analytics.py — chart generation
```

## Usage

**Scrape listings:**
```bash
python main.py                  # all pages
python main.py --pages 10       # first 10 pages only
python main.py --output result  # custom output filename
```

**Generate charts:**
```bash
python analytics/analytics.py
python analytics/analytics.py --input my_file.csv
```

## Analytics

Five charts are saved to `analytics/`:

| Chart | Description |
|---|---|
| `listings_by_district.png` | Number of listings per district |
| `price_by_district.png` | Median rent price per district |
| `price_distribution.png` | Overall price distribution (2–98 percentile) |
| `price_per_m2_by_district.png` | Median price per m² per district |
| `weekday.png` | Listings count by day of week |

### Note on the weekday chart

The weekday distribution chart can be misleading if data was collected in a single scrape session. For example, scraping on a Sunday will make Sunday appear dominant — not because landlords post more on Sundays, but simply because most listings were active on that day.

To get meaningful weekday insights, collect data **regularly over several weeks**. With a continuous dataset, the distribution will even out and reflect actual posting patterns.

## Requirements

```bash
pip install -r requirements.txt
```

## Tech stack

- `requests` + `BeautifulSoup` — scraping
- `pandas` + `matplotlib` — analytics and charts
