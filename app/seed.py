"""This module loads the supplied clinic configuration and inserts the original appointments"""

import sqlite3
from typing import Any

from app.database import Database


def seed_appointments(
    database: Database,
    clinic_data: dict[str, Any],
) -> None:
    """Insert the initial appointments without duplicating them."""

    with database.connect() as connection:
        for clinic in clinic_data["clinics"]:
            clinic_id = clinic["clinic_id"]

            for booking in clinic["existing_bookings"]:
                connection.execute(
                    """
                    INSERT INTO appointments (
                        appointment_id,
                        clinic_id,
                        doctor_id,
                        patient_phone,
                        slot_start
                    )
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(appointment_id) DO NOTHING
                    """,
                    (
                        booking["appointment_id"],
                        clinic_id,
                        booking["doctor_id"],
                        booking["patient_phone"],
                        booking["slot_start"],
                    ),
                )
