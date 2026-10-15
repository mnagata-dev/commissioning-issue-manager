"""Disposable Phase 1 transport experiment; not a CIM integration or protocol spec."""

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

VERSION = 1
CRASH_EXIT = 73


def encode(value: object) -> bytes:
    """Return stable bytes for the experimental format."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")


def checkpoint(requested: str, current: str) -> None:
    """Terminate without Python cleanup at an explicitly requested test point."""
    if requested == current:
        os._exit(CRASH_EXIT)


class Peer:
    """Own only a dedicated experimental directory and database."""

    def __init__(self, root: Path, device_id: str) -> None:
        self.root = root
        self.device_id = device_id
        for name in ("incoming", "outgoing", "quarantine"):
            (root / name).mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(root / "experiment.sqlite3")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS records (
                entity_id TEXT PRIMARY KEY, value TEXT NOT NULL,
                revision TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS outbox (
                event_id TEXT PRIMARY KEY, body BLOB NOT NULL,
                sent INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS applied (
                event_id TEXT PRIMARY KEY, body BLOB NOT NULL
            );
            CREATE TABLE IF NOT EXISTS effects (
                event_id TEXT PRIMARY KEY
            );
        """)

    def close(self) -> None:
        """Close the experiment's SQLite connection."""
        self.db.close()

    def change(self, entity_id: str, value: str, crash: str = "") -> str:
        """Atomically save a synthetic record and its outbound event."""
        revision = self.db.execute(
            "SELECT revision FROM records WHERE entity_id = ?", (entity_id,)
        ).fetchone()
        event_id = str(uuid4())
        event = {
            "device_id": self.device_id,
            "event_id": event_id,
            "batch_id": event_id,
            "sequence": self.db.execute("SELECT COUNT(*) FROM outbox").fetchone()[0] + 1,
            "entity_id": entity_id,
            "field": "value",
            "value": value,
            "base_revision": revision[0] if revision else "",
            "schema_version": VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        with self.db:
            self.db.execute(
                "INSERT OR REPLACE INTO records VALUES (?, ?, ?)",
                (entity_id, value, event_id),
            )
            checkpoint(crash, "local_before_outbox")
            self.db.execute("INSERT INTO outbox VALUES (?, ?, 0)", (event_id, encode(event)))
        checkpoint(crash, "local_committed")
        return event_id

    def publish(self, crash: str = "") -> None:
        """Publish one immutable batch per event, then mark the local outbox."""
        for event_id, body in self.db.execute(
            "SELECT event_id, body FROM outbox WHERE sent = 0 ORDER BY rowid"
        ).fetchall():
            folder = self.root / "outgoing"
            temporary = folder / (event_id + ".part")
            payload = body + b"\n"
            with temporary.open("wb") as stream:
                stream.write(payload[:len(payload) // 2])
                stream.flush()
                os.fsync(stream.fileno())
                checkpoint(crash, "publish_partial")
                stream.write(payload[len(payload) // 2:])
                stream.flush()
                os.fsync(stream.fileno())
            target = folder / (event_id + ".jsonl")
            if target.exists() and target.read_bytes() != payload:
                raise ValueError("Immutable batch collision")
            temporary.replace(target)
            checkpoint(crash, "publish_payload")
            manifest = encode({
                "schema_version": VERSION, "batch_id": event_id,
                "size": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
                "count": 1,
            })
            manifest_path = folder / (event_id + ".manifest")
            if manifest_path.exists() and manifest_path.read_bytes() != manifest:
                raise ValueError("Immutable manifest collision")
            manifest_path.write_bytes(manifest)
            checkpoint(crash, "publish_manifest")
            with self.db:
                self.db.execute("UPDATE outbox SET sent = 1 WHERE event_id = ?", (event_id,))

    def receive(self, manifest_path: Path, crash: str = "") -> str:
        """Validate before writing; preserve bad inputs locally for inspection."""
        payload_path = manifest_path.with_suffix(".jsonl")
        if not payload_path.exists():
            return "pending_payload"
        payload = payload_path.read_bytes()
        try:
            manifest = json.loads(manifest_path.read_bytes())
            if not isinstance(manifest, dict):
                raise ValueError("Invalid manifest")
            if manifest.get("schema_version") != VERSION:
                return "pending_version"
            if manifest.get("batch_id") != manifest_path.stem:
                raise ValueError("Batch identity mismatch")
            if (manifest.get("size") != len(payload)
                    or manifest.get("sha256") != hashlib.sha256(payload).hexdigest()):
                self.quarantine(manifest_path, payload_path)
                return "pending_integrity"
            events = [json.loads(line) for line in payload.splitlines()]
            if manifest.get("count") != len(events) or len(events) != 1:
                raise ValueError("Invalid experimental batch count")
            event = events[0]
            required = {
                "device_id", "event_id", "batch_id", "sequence", "entity_id",
                "field", "value", "base_revision", "schema_version", "created_at",
            }
            if not isinstance(event, dict) or set(event) != required:
                raise ValueError("Invalid event fields")
            if event["schema_version"] != VERSION:
                return "pending_version"
            if any(not isinstance(event[key], str) for key in required - {
                "sequence", "schema_version"
            }):
                raise ValueError("Invalid event types")
            if (type(event["sequence"]) is not int or event["sequence"] < 1
                    or not event["entity_id"] or not event["device_id"]
                    or event["field"] != "value"
                    or event["batch_id"] != manifest_path.stem
                    or event["event_id"] != event["batch_id"]):
                raise ValueError("Invalid event identity or sequence")
            return self.apply(event, crash)
        except (ValueError, TypeError, KeyError, UnicodeError):
            self.quarantine(manifest_path, payload_path)
            return "quarantined"

    def quarantine(self, *paths: Path) -> None:
        """Keep evidence without deleting a potentially still arriving input."""
        for path in paths:
            body = path.read_bytes()
            name = hashlib.sha256(body).hexdigest() + path.suffix
            (self.root / "quarantine" / name).write_bytes(body)

    def apply(self, event: dict, crash: str) -> str:
        """Commit record, applied ID, and synthetic side effect together."""
        body = encode(event)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            previous = self.db.execute(
                "SELECT body FROM applied WHERE event_id = ?", (event["event_id"],)
            ).fetchone()
            if previous:
                if previous[0] != body:
                    raise ValueError("Event ID reused with different content")
                return "duplicate"
            revision = self.db.execute(
                "SELECT revision FROM records WHERE entity_id = ?", (event["entity_id"],)
            ).fetchone()
            if (revision[0] if revision else "") != event["base_revision"]:
                return "pending_dependency_or_conflict"
            self.db.execute(
                "INSERT OR REPLACE INTO records VALUES (?, ?, ?)",
                (event["entity_id"], event["value"], event["event_id"]),
            )
            checkpoint(crash, "apply_record")
            self.db.execute("INSERT INTO applied VALUES (?, ?)", (event["event_id"], body))
            self.db.execute("INSERT INTO effects VALUES (?)", (event["event_id"],))
            checkpoint(crash, "apply_before_commit")
        checkpoint(crash, "apply_committed")
        return "applied"
