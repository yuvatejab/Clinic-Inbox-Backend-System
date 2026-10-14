
from app.data_loader import load_json, load_jsonl


def test_load_clinics():
    data = load_json("clinics.json")

    assert "clinics" in data
    assert len(data["clinics"]) == 2

    clinic_ids = {
        clinic["clinic_id"]
        for clinic in data["clinics"]
    }
    assert clinic_ids == {"clinic_a", "clinic_b"}


def test_load_events_preserves_order():
    events = load_jsonl("events.jsonl")

    assert events
    assert all(isinstance(event, dict) for event in events)
    assert all("event_id" in event for event in events)


def test_load_model_outputs():
    outputs = load_jsonl("model_outputs.jsonl")

    assert outputs
    assert all("message_id" in item for item in outputs)
    assert all("attempts" in item for item in outputs)


def test_load_labels():
    labels = load_jsonl("labels.jsonl")

    assert labels
    assert all("message_id" in item for item in labels)
    assert all("expected" in item for item in labels)
