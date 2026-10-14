# Clinic Inbox starter kit

Starter files for the Iro Health take-home assignment. The assignment brief has the full task, business rules and required API; this note only lists what is here. All data is synthetic: no real patients, clinics or phone numbers.

| File | Contents |
| --- | --- |
| `events.jsonl` | Webhook events, one JSON object per line, in the order they were delivered |
| `model_outputs.jsonl` | Recorded responses from the message-understanding model, one record per patient message |
| `clinics.json` | The two clinics: WhatsApp numbers, timezone, specialty, doctors, sessions and existing bookings |
| `red_flags.json` | Warning signs defined by our clinicians, common and per specialty |
| `labels.jsonl` | The correct outcome for a subset of messages |
| `replay.py` | Posts the events to your service |

## Replaying the events

`replay.py` needs Python 3.8 or later and no extra packages. Start your service, then:

```
python replay.py                              # posts to http://localhost:8000/webhooks/whatsapp
python replay.py --url http://localhost:3000  # if your service runs elsewhere
python replay.py --concurrent                 # also sends a few groups of events in parallel
```

Restart your service with empty state before each replay, since the events describe a few days of messages that should be processed once.
