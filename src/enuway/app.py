"""ENUWay MVP HTTP интерфейсі."""

from __future__ import annotations

import os

from flask import Flask, jsonify, request

from .service import BookingError, RideService


SEED_RIDES = [
    {
        "ride_id": 1,
        "driver": "Альфараби",
        "origin": "Сарыарқа",
        "destination": "ЕҰУ",
        "travel_date": "2026-11-13",
        "departure_time": "08:00",
        "seats_available": 3,
        "contribution_kzt": 700,
    },
    {
        "ride_id": 2,
        "driver": "Нурай",
        "origin": "Есіл",
        "destination": "ЕҰУ",
        "travel_date": "2026-11-13",
        "departure_time": "08:20",
        "seats_available": 2,
        "contribution_kzt": 600,
    },
]


def create_app(service: RideService | None = None) -> Flask:
    app = Flask(__name__)
    ride_service = service or RideService(SEED_RIDES)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "ENUWay"})

    @app.get("/api/rides")
    def list_rides():
        return jsonify(
            ride_service.list_rides(
                request.args.get("origin", ""),
                request.args.get("destination", ""),
                request.args.get("date", ""),
            )
        )

    @app.post("/api/rides")
    def create_ride():
        try:
            return jsonify(ride_service.create_ride(request.get_json(silent=True) or {})), 201
        except (TypeError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/rides/<int:ride_id>/book")
    def book(ride_id: int):
        payload = request.get_json(silent=True) or {}
        try:
            result = ride_service.book(
                ride_id,
                str(payload.get("passenger", "")),
                bool(payload.get("verified", False)),
            )
            return jsonify(result), 201
        except BookingError as exc:
            return jsonify({"error": str(exc)}), 409

    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    create_app().run(host="0.0.0.0", port=port)

