from dataclasses import dataclass
from typing import Optional


@dataclass
class Apartment:
    id: str
    title: str
    price_raw: str
    price_uah: Optional[float]
    negotiable: bool
    area_m2: Optional[str]
    district: Optional[str]
    city: str
    listing_date: Optional[str]
    url: str
