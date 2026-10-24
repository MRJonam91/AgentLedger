# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline, observed comparison of individual appends and one atomic batch."""

import argparse
import json
import sys
import tempfile
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agentledger.storage import Ledger


def benchmark(records=200):
    if not 1 <= records <= 1000:
        raise ValueError("records_must_be_between_1_and_1000")
    entries = [{"run_id": "benchmark", "kind": "benchmark", "data": {"counter": i},
                "external_key": str(i)} for i in range(records)]
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        single = Ledger(root / "single.sqlite3", create=True)
        batch = Ledger(root / "batch.sqlite3", create=True)
        start = perf_counter()
        for item in entries:
            single.append(**item)
        single_seconds = perf_counter() - start
        start = perf_counter()
        batch.append_many(entries)
        batch_seconds = perf_counter() - start
        assert single.verify()["event_count"] == batch.verify()["event_count"] == records
        return {"records": records, "single_seconds": round(single_seconds, 6),
                "batch_seconds": round(batch_seconds, 6),
                "observed_speedup": round(single_seconds / batch_seconds, 2),
                "scope": "Local synthetic observation; one run, no universal throughput guarantee"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=int, default=200)
    print(json.dumps(benchmark(parser.parse_args().records), indent=2))
