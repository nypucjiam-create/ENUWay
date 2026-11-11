from src.enuway.app import create_app
from src.enuway.service import RideService


def client():
    app = create_app(RideService())
    app.config.update(TESTING=True)
    return app.test_client()


def test_health_endpoint():
    response = client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_create_search_and_book_flow():
    web = client()
    created = web.post(
        "/api/rides",
        json={
            "driver": "Альфараби",
            "origin": "Сарыарқа",
            "destination": "ЕҰУ",
            "travel_date": "2026-11-14",
            "departure_time": "08:00",
            "seats_available": 2,
            "contribution_kzt": 700,
        },
    )
    assert created.status_code == 201
    ride_id = created.get_json()["ride_id"]

    found = web.get("/api/rides?origin=Сарыарқа&destination=ЕҰУ&date=2026-11-14")
    assert found.status_code == 200
    assert len(found.get_json()) == 1

    booked = web.post(
        f"/api/rides/{ride_id}/book",
        json={"passenger": "Нурай", "verified": True},
    )
    assert booked.status_code == 201
    assert booked.get_json()["seats_available"] == 1

