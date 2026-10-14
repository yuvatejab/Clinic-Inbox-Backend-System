#!/usr/bin/env python3
"""Replay the Clinic Inbox webhook events against your service.

Usage:
  python replay.py                               # posts to http://localhost:8000
  python replay.py --url http://localhost:3000   # a different address
  python replay.py --concurrent                  # also sends a few groups of events in parallel
  python replay.py --delay 0.2                   # pause (seconds) between deliveries

Each line of events.jsonl is POSTed, in file order, as the JSON body of a
request to <url>/webhooks/whatsapp. Requires Python 3.8+ and nothing else.
"""
import argparse
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter

# Event ids that --concurrent sends at the same moment, one list per group.
CONCURRENT_GROUPS = [["evt_0015"], ["evt_0029", "evt_0030"]]


def post(endpoint, body, timeout):
    request = urllib.request.Request(
        endpoint, data=body, method="POST", headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status
    except urllib.error.HTTPError as err:
        return err.code
    except Exception as err:  # connection refused, timeout, ...
        return "{}: {}".format(type(err).__name__, err)


def post_in_parallel(endpoint, bodies, timeout):
    results = [None] * len(bodies)
    barrier = threading.Barrier(len(bodies))

    def worker(i):
        barrier.wait()
        results[i] = post(endpoint, bodies[i], timeout)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(len(bodies))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return results


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="Replay Clinic Inbox webhook events.")
    parser.add_argument("--url", default="http://localhost:8000", help="base URL of your service")
    parser.add_argument("--file", default=os.path.join(here, "events.jsonl"), help="events file")
    parser.add_argument("--concurrent", action="store_true", help="send the concurrent groups in parallel")
    parser.add_argument("--delay", type=float, default=0.0, help="seconds to wait between deliveries")
    parser.add_argument("--timeout", type=float, default=30.0, help="per-request timeout in seconds")
    args = parser.parse_args(argv)

    endpoint = args.url.rstrip("/") + "/webhooks/whatsapp"
    with open(args.file, encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    event_ids = [json.loads(line)["event_id"] for line in lines]

    group_of = {}
    for index, group in enumerate(CONCURRENT_GROUPS):
        for event_id in group:
            group_of[event_id] = index

    print("Replaying {} deliveries to {}{}".format(
        len(lines), endpoint, " (concurrent groups in parallel)" if args.concurrent else ""))

    codes = Counter()
    problems = []
    i = 0
    while i < len(lines):
        group = group_of.get(event_ids[i]) if args.concurrent else None
        if group is not None:
            j = i
            while j < len(lines) and group_of.get(event_ids[j]) == group:
                j += 1
            batch = list(range(i, j))
            results = post_in_parallel(endpoint, [lines[k].encode("utf-8") for k in batch], args.timeout)
        else:
            batch = [i]
            results = [post(endpoint, lines[i].encode("utf-8"), args.timeout)]

        for k, result in zip(batch, results):
            codes[result] += 1
            tag = "  (parallel)" if len(batch) > 1 else ""
            print("  {}  ->  {}{}".format(event_ids[k], result, tag))
            if not (isinstance(result, int) and 200 <= result < 300):
                problems.append((event_ids[k], result))

        i = batch[-1] + 1
        if args.delay:
            time.sleep(args.delay)

    print()
    print("Responses: " + ", ".join("{} x{}".format(code, n) for code, n in sorted(codes.items(), key=lambda kv: str(kv[0]))))
    if problems:
        print("Not 2xx: " + ", ".join("{} ({})".format(eid, result) for eid, result in problems))
    return 0


if __name__ == "__main__":
    sys.exit(main())
