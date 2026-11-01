"""Original offline lab, NOT DeepSeek's implementation or a production runtime.

The caller supplies an already-authorized admission decision. There is no LLM,
policy engine, asynchronous Agent loop, external sender or semantic watchdog.
One coordinator owns writes; SQLite persists logical work independently of a
worker assignment. Outbox retries are at-least-once attempts, not exactly-once
external delivery. A real receiver needs its own idempotency mechanism.
"""
from dataclasses import dataclass
import sqlite3
import time


class StaleAssignment(RuntimeError):
    pass


@dataclass(frozen=True)
class Assignment:
    ticket_id: int
    generation: int


class Coordinator:
    def __init__(self, path, now=time.time):
        self.now = now
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys = ON')
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY, status TEXT NOT NULL DEFAULT 'queued',
                generation INTEGER NOT NULL DEFAULT 0, lease_until REAL,
                revision INTEGER NOT NULL DEFAULT 0, claimed_revision INTEGER,
                last_report TEXT
            );
            CREATE TABLE IF NOT EXISTS events (
                source TEXT, event_id TEXT, thread TEXT NOT NULL, text TEXT NOT NULL,
                PRIMARY KEY (source, event_id)
            );
            CREATE TABLE IF NOT EXISTS inputs (
                ticket_id INTEGER REFERENCES tickets(id), source TEXT, event_id TEXT,
                PRIMARY KEY (ticket_id, source, event_id),
                FOREIGN KEY (source, event_id) REFERENCES events(source, event_id)
            );
            CREATE TABLE IF NOT EXISTS subscriptions (
                source TEXT, thread TEXT, ticket_id INTEGER REFERENCES tickets(id),
                PRIMARY KEY (source, thread, ticket_id)
            );
            CREATE TABLE IF NOT EXISTS outbox (
                message_id TEXT PRIMARY KEY, ticket_id INTEGER REFERENCES tickets(id),
                kind TEXT NOT NULL, text TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0, acknowledged INTEGER NOT NULL DEFAULT 0
            );
        ''')

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def subscribe(self, ticket_id, source, thread):
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO subscriptions VALUES (?, ?, ?)',
                            (source, thread, ticket_id))

    def receive(self, source, event_id, thread, text, *, start_new=False):
        """start_new is a simulated *authorized* decision, never inferred here.

        Existing subscriptions deliver context, not broader authority. A thread
        can feed several independent tickets; receiving a follow-up need not
        create new work. A duplicate event keeps its original routing decision.
        """
        with self.db:
            inserted = self.db.execute('INSERT OR IGNORE INTO events VALUES (?, ?, ?, ?)',
                                      (source, event_id, thread, text)).rowcount
            if not inserted:
                return [r[0] for r in self.db.execute(
                    'SELECT ticket_id FROM inputs WHERE source=? AND event_id=? ORDER BY ticket_id',
                    (source, event_id))]
            targets = [r[0] for r in self.db.execute(
                'SELECT ticket_id FROM subscriptions WHERE source=? AND thread=? ORDER BY ticket_id',
                (source, thread))]
            if start_new:
                ticket_id = self.db.execute('INSERT INTO tickets DEFAULT VALUES').lastrowid
                self.db.execute('INSERT INTO subscriptions VALUES (?, ?, ?)',
                                (source, thread, ticket_id))
                targets.append(ticket_id)
            for ticket_id in targets:
                self.db.execute('INSERT INTO inputs VALUES (?, ?, ?)', (ticket_id, source, event_id))
                self.db.execute('''UPDATE tickets SET revision=revision+1,
                    status=CASE WHEN status IN ('ready', 'attention') THEN 'queued' ELSE status END
                    WHERE id=?''', (ticket_id,))
            return targets

    def context(self, ticket_id):
        row = self.db.execute('SELECT * FROM tickets WHERE id=?', (ticket_id,)).fetchone()
        if row is None:
            raise KeyError(ticket_id)
        result = dict(row)
        result['inputs'] = [dict(r) for r in self.db.execute('''
            SELECT e.source, e.event_id, e.thread, e.text FROM inputs i
            JOIN events e ON e.source=i.source AND e.event_id=i.event_id
            WHERE i.ticket_id=? ORDER BY i.rowid''', (ticket_id,))]
        return result

    def claim(self, ticket_id, lease_seconds=10):
        if lease_seconds <= 0:
            raise ValueError('lease_seconds must be positive')
        with self.db:
            changed = self.db.execute('''UPDATE tickets SET status='running',
                generation=generation+1, lease_until=?, claimed_revision=revision
                WHERE id=? AND status='queued' ''', (self.now() + lease_seconds, ticket_id)).rowcount
            if changed != 1:
                raise StaleAssignment('ticket is not queued')
            generation = self.db.execute('SELECT generation FROM tickets WHERE id=?', (ticket_id,)).fetchone()[0]
            return Assignment(ticket_id, generation)

    def recover_expired(self):
        """External timeout monitor only; no judgement about semantic progress."""
        with self.db:
            return self.db.execute('''UPDATE tickets SET status='queued', lease_until=NULL
                WHERE status='running' AND lease_until<=?''', (self.now(),)).rowcount

    def report(self, assignment, kind, text):
        if kind not in ('progress', 'result', 'attention'):
            raise ValueError('unsupported report kind')
        message_id = f'ticket:{assignment.ticket_id}:generation:{assignment.generation}:{kind}'
        with self.db:
            row = self.db.execute('SELECT * FROM tickets WHERE id=?', (assignment.ticket_id,)).fetchone()
            if row is None or row['generation'] != assignment.generation:
                raise StaleAssignment('assignment generation no longer owns the ticket')
            previous = self.db.execute('SELECT text FROM outbox WHERE message_id=?', (message_id,)).fetchone()
            if previous is not None:
                if previous['text'] != text:
                    raise ValueError('an idempotency key cannot name a different payload')
                return message_id
            if row['status'] != 'running' or row['lease_until'] <= self.now():
                raise StaleAssignment('assignment lease is not live')
            if kind == 'progress':
                return None  # No external message, no extension of a worker's lease.
            # Inputs arriving during execution remain pending for another turn.
            state = 'queued' if row['revision'] > row['claimed_revision'] else (
                'ready' if kind == 'result' else 'attention')
            self.db.execute('UPDATE tickets SET status=?, lease_until=NULL, last_report=? WHERE id=?',
                            (state, text, assignment.ticket_id))
            self.db.execute('INSERT INTO outbox(message_id, ticket_id, kind, text) VALUES (?, ?, ?, ?)',
                            (message_id, assignment.ticket_id, kind, text))
            return message_id

    def pending_messages(self):
        return [dict(r) for r in self.db.execute(
            'SELECT * FROM outbox WHERE acknowledged=0 ORDER BY rowid')]

    def delivery_attempt(self, message_id):
        """Record a local attempt. This method sends nothing."""
        with self.db:
            changed = self.db.execute('''UPDATE outbox SET attempts=attempts+1
                WHERE message_id=? AND acknowledged=0''', (message_id,)).rowcount
            if changed != 1:
                raise KeyError('no pending message with this id')
            return dict(self.db.execute('SELECT * FROM outbox WHERE message_id=?', (message_id,)).fetchone())

    def acknowledge(self, message_id):
        with self.db:
            self.db.execute('UPDATE outbox SET acknowledged=1 WHERE message_id=?', (message_id,))
