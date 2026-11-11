"""ENUWay MVP үшін шағын, жадта сақталатын домендік сервис."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date


class BookingError(ValueError):
    """Броньдау бизнес ережесі бұзылғанда қайтарылады."""


@dataclass
class Ride:
    ride_id: int
    driver: str
    origin: str
    destination: str
    travel_date: str
    departure_time: str
    seats_available: int
    contribution_kzt: int


class RideService:
    """US-03, US-05, US-06 және US-08 талаптарын орындайды."""

    def __init__(self, rides: list[dict] | None = None) -> None:
        self._rides: dict[int, Ride] = {}
        self._bookings: set[tuple[int, str]] = set()
        for item in rides or []:
            ride = Ride(**item)
            self._rides[ride.ride_id] = ride

    def list_rides(self, origin: str = "", destination: str = "", travel_date: str = "") -> list[dict]:
        """Берілген бағыт пен күнге сәйкес сапарларды қайтарады."""
        origin_key = origin.strip().casefold()
        destination_key = destination.strip().casefold()
        result = []
        for ride in self._rides.values():
            if origin_key and origin_key not in ride.origin.casefold():
                continue
            if destination_key and destination_key not in ride.destination.casefold():
                continue
            if travel_date and ride.travel_date != travel_date:
                continue
            result.append(asdict(ride))
        return sorted(result, key=lambda item: (item["travel_date"], item["departure_time"]))

    def create_ride(self, payload: dict) -> dict:
        """1-4 орын шегін және міндетті өрістерді тексеріп сапар жасайды."""
        required = ["driver", "origin", "destination", "travel_date", "departure_time"]
        missing = [field for field in required if not str(payload.get(field, "")).strip()]
        if missing:
            raise ValueError(f"Міндетті өрістер толтырылмаған: {', '.join(missing)}")

        seats = int(payload.get("seats_available", 0))
        if seats < 1 or seats > 4:
            raise ValueError("Бос орын саны 1 мен 4 аралығында болуы керек")

        contribution = int(payload.get("contribution_kzt", 0))
        if contribution < 0 or contribution > 5000:
            raise ValueError("Шығын үлесі 0 мен 5000 теңге аралығында болуы керек")

        travel_date = str(payload["travel_date"])
        date.fromisoformat(travel_date)
        next_id = max(self._rides, default=0) + 1
        ride = Ride(
            ride_id=next_id,
            driver=str(payload["driver"]).strip(),
            origin=str(payload["origin"]).strip(),
            destination=str(payload["destination"]).strip(),
            travel_date=travel_date,
            departure_time=str(payload["departure_time"]).strip(),
            seats_available=seats,
            contribution_kzt=contribution,
        )
        self._rides[next_id] = ride
        return asdict(ride)

    def book(self, ride_id: int, passenger: str, verified: bool) -> dict:
        """Тексерілген жолаушыға бір орынды артық броньсыз бекітеді."""
        if not verified:
            raise BookingError("Тек ENU аккаунты тексерілген пайдаланушы броньдай алады")
        passenger = passenger.strip()
        if not passenger:
            raise BookingError("Жолаушы аты көрсетілуі керек")
        ride = self._rides.get(ride_id)
        if ride is None:
            raise BookingError("Сапар табылмады")
        key = (ride_id, passenger.casefold())
        if key in self._bookings:
            raise BookingError("Бұл жолаушы сапарға бұрын қосылған")
        if ride.seats_available <= 0:
            raise BookingError("Бос орын жоқ")
        ride.seats_available -= 1
        self._bookings.add(key)
        return {"status": "confirmed", "ride_id": ride_id, "seats_available": ride.seats_available}

