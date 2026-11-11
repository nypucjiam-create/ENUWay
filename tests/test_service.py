from datetime import date, timedelta

import pytest

from src.enuway.service import BookingError, RideService


@pytest.fixture
def service():
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    return RideService(
        [
            {
                "ride_id": 1,
                "driver": "Альфараби",
                "origin": "Сарыарқа",
                "destination": "ЕҰУ",
                "travel_date": tomorrow,
                "departure_time": "08:00",
                "seats_available": 1,
                "contribution_kzt": 700,
            }
        ]
    )


def test_search_filters_by_route(service):
    assert len(service.list_rides(origin="сары", destination="ЕҰУ")) == 1
    assert service.list_rides(origin="Алматы") == []


def test_create_ride_enforces_seat_range(service):
    with pytest.raises(ValueError, match="1 мен 4"):
        service.create_ride(
            {
                "driver": "Нурай",
                "origin": "Есіл",
                "destination": "ЕҰУ",
                "travel_date": "2026-11-14",
                "departure_time": "08:10",
                "seats_available": 5,
            }
        )


def test_create_ride_requires_fields(service):
    with pytest.raises(ValueError, match="Міндетті"):
        service.create_ride({"driver": "Нурай", "seats_available": 2})


def test_verified_passenger_can_book_last_seat(service):
    result = service.book(1, "Нурислам", verified=True)
    assert result["status"] == "confirmed"
    assert result["seats_available"] == 0


def test_unverified_passenger_is_rejected(service):
    with pytest.raises(BookingError, match="ENU аккаунты"):
        service.book(1, "Нурислам", verified=False)


def test_overbooking_is_rejected(service):
    service.book(1, "Нурислам", verified=True)
    with pytest.raises(BookingError, match="Бос орын жоқ"):
        service.book(1, "Нурай", verified=True)


def test_duplicate_booking_is_rejected(service):
    service.book(1, "Нурислам", verified=True)
    with pytest.raises(BookingError):
        service.book(1, "Нурислам", verified=True)

