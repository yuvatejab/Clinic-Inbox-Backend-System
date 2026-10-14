
import sqlite3

import pytest

from app.data_loader import load_json
from app.database import Database
from app.seed import seed_appointments


@pytest.fixture
def database(tmp_path):
    db = Database(tmp_path / "test.db")
    db.initialize()
    return db


def test_initial_appointments_are_loaded(database):
    clinics = load_json("clinics.json")
    seed_appointments(database, clinics)

    with database.connect() as connection:
        rows = connection.execute(
            """
            SELECT clinic_id, COUNT(*) AS total
            FROM appointments
            GROUP BY clinic_id
            """
        ).fetchall()

    counts = {row["clinic_id"]: row["total"] for row in rows}

    assert counts == {"clinic_a": 6, "clinic_b": 15}


def test_seeding_is_idempotent(database):
    clinics = load_json("clinics.json")

    seed_appointments(database, clinics)
    seed_appointments(database, clinics)

    with database.connect() as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM appointments"
        ).fetchone()[0]

    assert count == 21


def test_duplicate_doctor_slot_is_rejected(database):
    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO appointments (
                appointment_id, clinic_id, doctor_id,
                patient_phone, slot_start
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "apt_test_1",
                "clinic_a",
                "dr_rao",
                "+919000000111",
                "2026-11-09T10:00:00+05:30",
            ),
        )

    with pytest.raises(sqlite3.IntegrityError):
        with database.connect() as connection:
            connection.execute(
                """
                INSERT INTO appointments (
                    appointment_id, clinic_id, doctor_id,
                    patient_phone, slot_start
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "apt_test_2",
                    "clinic_a",
                    "dr_rao",
                    "+919000000222",
                    "2026-11-09T10:00:00+05:30",
                ),
            )


def test_same_slot_is_allowed_for_another_clinic(database):
    with database.connect() as connection:
        connection.executemany(
            """
            INSERT INTO appointments (
                appointment_id, clinic_id, doctor_id,
                patient_phone, slot_start
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    "apt_clinic_a",
                    "clinic_a",
                    "dr_rao",
                    "+919000000111",
                    "2026-11-09T10:00:00+05:30",
                ),
                (
                    "apt_clinic_b",
                    "clinic_b",
                    "dr_rao",
                    "+919000000222",
                    "2026-11-09T10:00:00+05:30",
                ),
            ],
        )

        count = connection.execute(
            "SELECT COUNT(*) FROM appointments"
        ).fetchone()[0]

    assert count == 2
