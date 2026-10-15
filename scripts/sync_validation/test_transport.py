"""Local fault scenarios. Run with python3 -B -m unittest discover here."""

import hashlib
import json
import platform
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from transport import CRASH_EXIT, Peer, encode


class TransportTests(unittest.TestCase):
    """Use fresh independent A/B databases for every scenario."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="cim-sync-validation-")
        self.root = Path(self.temporary.name)
        self.a = Peer(self.root / "pc_a", "A")
        self.b = Peer(self.root / "pc_b", "B")

    def tearDown(self) -> None:
        self.a.close()
        self.b.close()
        self.temporary.cleanup()

    def deliver(self, event_id: str, suffix: str) -> Path:
        """Copy a selected file, allowing arbitrary arrival order and delay."""
        source = self.a.root / "outgoing" / (event_id + suffix)
        destination = self.b.root / "incoming" / source.name
        shutil.copyfile(source, destination)
        return destination

    def transfer(self, event_id: str) -> Path:
        self.deliver(event_id, ".jsonl")
        return self.deliver(event_id, ".manifest")

    def state(self, peer: Peer) -> tuple:
        """Include synthetic side effects so duplicates cannot hide."""
        return tuple(peer.db.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall()
                     for table in ("records", "applied", "effects"))

    def assert_received(self, count: int, value: str) -> None:
        self.assertEqual(self.b.db.execute("SELECT COUNT(*) FROM applied").fetchone()[0], count)
        self.assertEqual(self.b.db.execute("SELECT COUNT(*) FROM effects").fetchone()[0], count)
        self.assertEqual(self.b.db.execute("SELECT value FROM records").fetchone()[0], value)

    def crash(self, peer: Peer, expression: str) -> None:
        """Run a real child process which exits inside an open transaction."""
        code = (
            "from pathlib import Path; from transport import Peer; "
            f"p = Peer(Path({str(peer.root)!r}), {peer.device_id!r}); {expression}"
        )
        result = subprocess.run(
            [sys.executable, "-B", "-c", code],
            cwd=Path(__file__).parent, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, CRASH_EXIT, result.stderr)

    def test_t01_delivery_both_directions(self) -> None:
        started = time.perf_counter()
        event_id = self.a.change("sample", "one")
        saved = time.perf_counter()
        self.a.publish()
        published = time.perf_counter()
        manifest = self.transfer(event_id)
        detected = time.perf_counter()
        self.assertEqual(self.b.receive(manifest), "applied")
        self.assert_received(1, "one")
        print(json.dumps({"T01_ms": {
            "local_save": (saved - started) * 1000,
            "publish": (published - saved) * 1000,
            "copy_detect": (detected - published) * 1000,
            "apply": (time.perf_counter() - detected) * 1000,
        }}))
        reverse = self.b.change("other", "reverse")
        self.b.publish()
        for suffix in (".jsonl", ".manifest"):
            shutil.copyfile(self.b.root / "outgoing" / (reverse + suffix),
                            self.a.root / "incoming" / (reverse + suffix))
        self.assertEqual(self.a.receive(self.a.root / "incoming" / (reverse + ".manifest")),
                         "applied")
        self.assertEqual(self.a.db.execute("SELECT value FROM records WHERE entity_id='other'")
                         .fetchone()[0], "reverse")

    def test_t05_duplicate_after_restart(self) -> None:
        event_id = self.a.change("sample", "one")
        self.a.publish()
        manifest = self.transfer(event_id)
        self.assertEqual(self.b.receive(manifest), "applied")
        before = self.state(self.b)
        self.b.close()
        self.b = Peer(self.root / "pc_b", "B")
        for _ in range(3):
            self.assertEqual(self.b.receive(self.transfer(event_id)), "duplicate")
        self.assertEqual(self.state(self.b), before)
        self.assert_received(1, "one")

    def test_t06_partial_and_arrival_orders(self) -> None:
        event_id = self.a.change("sample", "one")
        self.a.publish()
        manifest = self.deliver(event_id, ".manifest")
        self.assertEqual(self.b.receive(manifest), "pending_payload")
        payload = manifest.with_suffix(".jsonl")
        complete = (self.a.root / "outgoing" / payload.name).read_bytes()
        payload.write_bytes(complete[:len(complete) // 2])
        self.assertEqual(self.b.receive(manifest), "pending_integrity")
        self.assertEqual(self.state(self.b), ([], [], []))
        self.deliver(event_id, ".jsonl")
        self.assertEqual(self.b.receive(manifest), "applied")
        self.assert_received(1, "one")

    def test_t07_dependency_reversal(self) -> None:
        first = self.a.change("sample", "one")
        second = self.a.change("sample", "two")
        self.a.publish()
        later = self.transfer(second)
        self.assertEqual(self.b.receive(later), "pending_dependency_or_conflict")
        self.assertEqual(self.state(self.b), ([], [], []))
        self.assertEqual(self.b.receive(self.transfer(first)), "applied")
        self.assertEqual(self.b.receive(later), "applied")
        self.assertEqual(self.b.receive(self.transfer(first)), "duplicate")
        self.assert_received(2, "two")

    def test_t08_paused_copy_and_resume(self) -> None:
        ids = [self.a.change("sample", str(index)) for index in range(5)]
        self.a.close()
        self.a = Peer(self.root / "pc_a", "A")
        self.assertEqual(self.a.db.execute("SELECT COUNT(*) FROM outbox WHERE sent=0")
                         .fetchone()[0], 5)
        self.assertEqual(self.state(self.b), ([], [], []))
        self.a.publish()
        manifests = [self.transfer(event_id) for event_id in reversed(ids)]
        for _ in ids:
            for manifest in manifests:
                self.b.receive(manifest)
        self.assert_received(5, "4")
        self.assertEqual(self.a.db.execute("SELECT entity_id,value,revision FROM records")
                         .fetchall(), self.b.db.execute("SELECT * FROM records").fetchall())

    def test_t09_local_transaction_interruptions(self) -> None:
        self.crash(self.a, "p.change('sample', 'one', 'local_before_outbox')")
        self.assertEqual(self.a.db.execute("SELECT * FROM records").fetchall(), [])
        self.assertEqual(self.a.db.execute("SELECT * FROM outbox").fetchall(), [])
        self.crash(self.a, "p.change('sample', 'one', 'local_committed')")
        self.assertEqual(self.a.db.execute("SELECT COUNT(*) FROM outbox WHERE sent=0")
                         .fetchone()[0], 1)
        self.a.publish()
        event_id = self.a.db.execute("SELECT event_id FROM outbox").fetchone()[0]
        self.assertEqual(self.b.receive(self.transfer(event_id)), "applied")
        self.assert_received(1, "one")

    def test_t09_publish_interruptions(self) -> None:
        for point in ("publish_partial", "publish_payload", "publish_manifest"):
            with self.subTest(point=point):
                sender = Peer(self.root / point / "a", "A")
                receiver = Peer(self.root / point / "b", "B")
                try:
                    event_id = sender.change("sample", "one")
                    self.crash(sender, f"p.publish({point!r})")
                    self.assertEqual(sender.db.execute("SELECT sent FROM outbox")
                                     .fetchone()[0], 0)
                    if point == "publish_partial":
                        self.assertFalse(list((sender.root / "outgoing").glob("*.manifest")))
                        self.assertFalse(list((sender.root / "outgoing").glob("*.jsonl")))
                    sender.publish()
                    for suffix in (".jsonl", ".manifest"):
                        shutil.copyfile(sender.root / "outgoing" / (event_id + suffix),
                                        receiver.root / "incoming" / (event_id + suffix))
                    manifest = receiver.root / "incoming" / (event_id + ".manifest")
                    self.assertEqual(receiver.receive(manifest), "applied")
                    self.assertEqual(receiver.receive(manifest), "duplicate")
                    self.assertEqual(receiver.db.execute("SELECT COUNT(*) FROM effects")
                                     .fetchone()[0], 1)
                    self.assertEqual(receiver.db.execute("SELECT value FROM records")
                                     .fetchone()[0], "one")
                    self.assertEqual(sender.db.execute("SELECT sent FROM outbox")
                                     .fetchone()[0], 1)
                finally:
                    sender.close()
                    receiver.close()

    def test_t09_apply_interruptions(self) -> None:
        event_id = self.a.change("sample", "one")
        self.a.publish()
        manifest = self.transfer(event_id)
        for point in ("apply_record", "apply_before_commit"):
            self.crash(self.b, f"p.receive(Path({str(manifest)!r}), {point!r})")
            self.assertEqual(self.state(self.b), ([], [], []))
        self.crash(self.b, f"p.receive(Path({str(manifest)!r}), 'apply_committed')")
        self.assertEqual(self.b.receive(manifest), "duplicate")
        self.assert_received(1, "one")

    def rewrite(self, manifest: Path, payload: bytes) -> None:
        """Create malformed but checksum-consistent fixtures."""
        manifest.with_suffix(".jsonl").write_bytes(payload)
        metadata = json.loads(manifest.read_bytes())
        metadata.update(size=len(payload), sha256=hashlib.sha256(payload).hexdigest())
        manifest.write_bytes(encode(metadata))

    def test_t10_bad_inputs_and_recovery(self) -> None:
        event_id = self.a.change("sample", "one")
        self.a.publish()
        manifest = self.transfer(event_id)
        original = manifest.with_suffix(".jsonl").read_bytes()
        event = json.loads(original)
        fixtures = [b"{broken\n", encode([]), encode({"value": "missing fields"}),
                    encode(dict(event, sequence="1")), encode(dict(event, field="unknown"))]
        for payload in fixtures:
            with self.subTest(payload=payload):
                self.transfer(event_id)
                self.rewrite(manifest, payload)
                self.assertEqual(self.b.receive(manifest), "quarantined")
                self.assertEqual(self.state(self.b), ([], [], []))
        self.transfer(event_id)
        manifest.write_bytes(b"{invalid")
        self.assertEqual(self.b.receive(manifest), "quarantined")
        self.transfer(event_id)
        self.rewrite(manifest, encode(dict(event, schema_version=999)))
        self.assertEqual(self.b.receive(manifest), "pending_version")
        self.transfer(event_id)
        metadata = json.loads(manifest.read_bytes())
        manifest.write_bytes(encode(dict(metadata, schema_version=999)))
        self.assertEqual(self.b.receive(manifest), "pending_version")
        self.transfer(event_id)
        manifest.with_suffix(".jsonl").write_bytes(original.replace(b"one", b"bad"))
        self.assertEqual(self.b.receive(manifest), "pending_integrity")
        self.assertEqual(self.state(self.b), ([], [], []))
        self.assertTrue(list((self.b.root / "quarantine").iterdir()))
        self.assertEqual(self.b.receive(self.transfer(event_id)), "applied")
        before = self.state(self.b)
        self.rewrite(manifest, encode(dict(event, value="changed under same ID")))
        self.assertEqual(self.b.receive(manifest), "quarantined")
        self.assertEqual(self.state(self.b), before)
        self.assert_received(1, "one")


if __name__ == "__main__":
    print(json.dumps({"python": sys.version, "platform": platform.platform(),
                      "sqlite": sqlite3.sqlite_version}))
    unittest.main(verbosity=2)
