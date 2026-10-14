"""This file owns database connections, schema creation and database initialization."""

import sqlite3
from pathlib import Path


class Database:
    """Manage SQLite connections and initialize the database schema."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path,
            timeout=10,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        """Create tables if they do not already exist."""
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL UNIQUE,
                    clinic_id TEXT,
                    patient_phone TEXT NOT NULL,
                    message_text TEXT NOT NULL,
                    message_timestamp TEXT NOT NULL,
                    outcome TEXT,
                    decision_json TEXT,
                    FOREIGN KEY (event_id)
                        REFERENCES events(event_id)
                );

                CREATE TABLE IF NOT EXISTS appointments (
                    appointment_id TEXT PRIMARY KEY,
                    clinic_id TEXT NOT NULL,
                    doctor_id TEXT NOT NULL,
                    patient_phone TEXT NOT NULL,
                    slot_start TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'scheduled'
                        CHECK (
                            status IN (
                                'scheduled',
                                'cancelled'
                            )
                        ),
                    UNIQUE (clinic_id, doctor_id, slot_start)
                );

                CREATE INDEX IF NOT EXISTS
                    idx_appointments_patient
                ON appointments (
                    clinic_id,
                    patient_phone,
                    status,
                    slot_start
                );

                CREATE INDEX IF NOT EXISTS
                    idx_appointments_doctor
                ON appointments (
                    clinic_id,
                    doctor_id,
                    slot_start,
                    status
                );
                """
            )
