import csv
from dataclasses import asdict, fields

from models import Apartment


def save_csv(apartments: list[Apartment], path: str) -> None:
    if not apartments:
        return
    field_names = [f.name for f in fields(Apartment)]
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        for apt in apartments:
            writer.writerow(asdict(apt))
