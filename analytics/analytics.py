"""
Аналітика OLX-даних. Читає apartments.csv, зберігає графіки у папку analytics/.

Запуск:
    python analytics/analytics.py
    python analytics/analytics.py --input my_file.csv
"""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

OUT_DIR = Path(__file__).parent
PROJECT_DIR = OUT_DIR.parent
UA_DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]


def load(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    ua_months = {
        "січня": "January", "лютого": "February", "березня": "March",
        "квітня": "April", "травня": "May", "червня": "June",
        "липня": "July", "серпня": "August", "вересня": "September",
        "жовтня": "October", "листопада": "November", "грудня": "December",
    }
    src = df["listing_date"].str.replace(" р.", "", regex=False).str.strip()
    for ua, en in ua_months.items():
        src = src.str.replace(ua, en, regex=False)
    df["listing_date"] = pd.to_datetime(src, format="%d %B %Y", errors="coerce")

    df["weekday"] = df["listing_date"].dt.dayofweek
    df["district"] = df["district"].fillna("Невідомо")
    return df


def plot_weekday(df: pd.DataFrame) -> None:
    counts = df.groupby("weekday").size().reindex(range(7), fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(range(7), counts.values, color="#4C72B0", edgecolor="white", linewidth=0.8)
    ax.set_xticks(range(7))
    ax.set_xticklabels(UA_DAYS, fontsize=12)
    ax.set_ylabel("Кількість оголошень")
    ax.set_title("Оголошення по днях тижня")
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                str(val), ha="center", va="bottom", fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "weekday.png", dpi=150)
    plt.close(fig)
    print("  weekday.png")


def plot_price_distribution(df: pd.DataFrame) -> None:
    prices = df["price_uah"].dropna()
    prices = prices[prices.between(prices.quantile(0.02), prices.quantile(0.98))]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(prices, bins=40, color="#55A868", edgecolor="white", linewidth=0.6)
    ax.set_xlabel("Ціна (грн/міс)")
    ax.set_ylabel("Кількість оголошень")
    ax.set_title("Розподіл цін")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "price_distribution.png", dpi=150)
    plt.close(fig)
    print("  price_distribution.png")


def plot_price_by_district(df: pd.DataFrame) -> None:
    medians = (
        df[df["price_uah"].notna()]
        .groupby("district")["price_uah"]
        .median()
        .sort_values(ascending=True)
    )
    fig, ax = plt.subplots(figsize=(9, max(5, len(medians) * 0.45)))
    bars = ax.barh(medians.index, medians.values, color="#C44E52", edgecolor="white", linewidth=0.8)
    ax.set_xlabel("Медіана ціни (грн/міс)")
    ax.set_title("Медіана ціни по районах")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    for bar, val in zip(bars, medians.values):
        ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height() / 2,
                f"{val:,.0f}", va="center", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "price_by_district.png", dpi=150)
    plt.close(fig)
    print("  price_by_district.png")


def plot_listings_by_district(df: pd.DataFrame) -> None:
    counts = df["district"].value_counts().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(9, max(5, len(counts) * 0.45)))
    ax.barh(counts.index, counts.values, color="#4C72B0", edgecolor="white", linewidth=0.8)
    ax.set_xlabel("Кількість оголошень")
    ax.set_title("Оголошення по районах")
    for i, val in enumerate(counts.values):
        ax.text(val + 0.3, i, str(val), va="center", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "listings_by_district.png", dpi=150)
    plt.close(fig)
    print("  listings_by_district.png")


def plot_price_per_m2(df: pd.DataFrame) -> None:
    d = df.copy()
    d["area_num"] = d["area_m2"].str.extract(r"(\d+)").astype(float)
    d = d[d["area_num"].notna() & d["price_uah"].notna() & (d["area_num"] > 0)]
    d["price_per_m2"] = d["price_uah"] / d["area_num"]
    medians = (
        d.groupby("district")["price_per_m2"]
        .median()
        .sort_values(ascending=True)
    )
    fig, ax = plt.subplots(figsize=(9, max(5, len(medians) * 0.45)))
    bars = ax.barh(medians.index, medians.values, color="#8172B2", edgecolor="white", linewidth=0.8)
    ax.set_xlabel("Медіана ціни за м² (грн)")
    ax.set_title("Ціна за м² по районах")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    for bar, val in zip(bars, medians.values):
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
                f"{val:,.0f}", va="center", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "price_per_m2_by_district.png", dpi=150)
    plt.close(fig)
    print("  price_per_m2_by_district.png")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(PROJECT_DIR / "apartments.csv"))
    args = parser.parse_args()

    df = load(args.input)
    print(f"Завантажено {len(df)} оголошень. Генеруємо графіки...\n")

    plot_weekday(df)
    plot_price_distribution(df)
    plot_price_by_district(df)
    plot_listings_by_district(df)
    plot_price_per_m2(df)

    print(f"\nГотово. Графіки збережено у {OUT_DIR}/")


if __name__ == "__main__":
    main()
