from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from coordinator import Coordinator, StaleAssignment


class CoordinationInvariants(unittest.TestCase):
    def setUp(self):
        self.folder = TemporaryDirectory(prefix='superagent-test-', dir=Path(__file__).resolve().parent)
        self.path = Path(self.folder.name) / 'state.sqlite3'
        self.clock = [10.0]
        self.runtime = Coordinator(self.path, now=lambda: self.clock[0])

    def tearDown(self):
        self.runtime.close()
        self.folder.cleanup()

    def reopen(self):
        self.runtime.close()
        self.runtime = Coordinator(self.path, now=lambda: self.clock[0])

    def ticket(self, source='chat', event='one', thread='topic', text='authorized work'):
        return self.runtime.receive(source, event, thread, text, start_new=True)[0]

    def test_duplicate_event_survives_real_database_reopen(self):
        ticket_id = self.ticket()
        self.reopen()
        self.assertEqual(self.runtime.receive('chat', 'one', 'topic', 'changed replay', start_new=True), [ticket_id])
        self.assertEqual(self.runtime.db.execute('SELECT COUNT(*) FROM tickets').fetchone()[0], 1)
        self.assertEqual(self.runtime.context(ticket_id)['inputs'][0]['text'], 'authorized work')

    def test_same_event_id_on_other_source_is_independent(self):
        first = self.ticket()
        other = self.ticket(source='github')
        self.assertNotEqual(first, other)
        self.assertEqual([x['source'] for x in self.runtime.context(first)['inputs']], ['chat'])
        self.assertEqual([x['source'] for x in self.runtime.context(other)['inputs']], ['github'])

    def test_subscribed_followup_is_context_not_new_work(self):
        first = self.ticket()
        other = self.ticket(event='two', thread='unrelated')
        routed = self.runtime.receive('chat', 'followup', 'topic', 'additional evidence')
        self.assertEqual(routed, [first])
        self.assertEqual(len(self.runtime.context(first)['inputs']), 2)
        self.assertEqual(len(self.runtime.context(other)['inputs']), 1)
        self.assertEqual(self.runtime.db.execute('SELECT COUNT(*) FROM tickets').fetchone()[0], 2)

    def test_unadmitted_event_does_not_start_work_when_replayed(self):
        self.assertEqual(self.runtime.receive('chat', 'noise', 'topic', 'ordinary chat'), [])
        self.assertEqual(self.runtime.receive('chat', 'noise', 'topic', 'ordinary chat', start_new=True), [])
        self.assertEqual(self.runtime.db.execute('SELECT COUNT(*) FROM tickets').fetchone()[0], 0)

    def test_expiry_and_reassignment_preserve_inputs_and_fence_old_worker(self):
        ticket_id = self.ticket()
        old = self.runtime.claim(ticket_id, lease_seconds=2)
        self.clock[0] = 12
        with self.assertRaises(StaleAssignment):
            self.runtime.report(old, 'result', 'expired')
        self.assertEqual(self.runtime.recover_expired(), 1)
        self.reopen()
        self.assertEqual(self.runtime.context(ticket_id)['status'], 'queued')
        self.assertEqual(len(self.runtime.context(ticket_id)['inputs']), 1)
        current = self.runtime.claim(ticket_id)
        self.assertGreater(current.generation, old.generation)
        with self.assertRaises(StaleAssignment):
            self.runtime.report(old, 'result', 'late write')
        self.runtime.report(current, 'result', 'current write')
        self.assertEqual(self.runtime.context(ticket_id)['last_report'], 'current write')

    def test_progress_is_silent_and_does_not_extend_lease(self):
        ticket_id = self.ticket()
        assignment = self.runtime.claim(ticket_id, lease_seconds=2)
        self.clock[0] = 11
        self.assertIsNone(self.runtime.report(assignment, 'progress', 'still working'))
        self.assertEqual(self.runtime.pending_messages(), [])
        self.clock[0] = 12
        self.assertEqual(self.runtime.recover_expired(), 1)

    def test_result_outbox_is_durable_and_retries_keep_message_id(self):
        ticket_id = self.ticket()
        assignment = self.runtime.claim(ticket_id)
        message_id = self.runtime.report(assignment, 'result', 'reviewable result')
        self.assertEqual(self.runtime.report(assignment, 'result', 'reviewable result'), message_id)
        self.runtime.delivery_attempt(message_id)
        self.reopen()
        attempt = self.runtime.delivery_attempt(message_id)
        self.assertEqual(attempt['message_id'], message_id)
        self.assertEqual(attempt['attempts'], 2)
        self.assertEqual(len(self.runtime.pending_messages()), 1)
        self.runtime.acknowledge(message_id)
        self.assertEqual(self.runtime.pending_messages(), [])

    def test_attention_is_actionable_and_ticket_outlives_assignment(self):
        ticket_id = self.ticket()
        assignment = self.runtime.claim(ticket_id)
        self.runtime.report(assignment, 'attention', 'need one decision')
        self.reopen()
        self.assertEqual(self.runtime.context(ticket_id)['status'], 'attention')
        self.assertIsNone(self.runtime.context(ticket_id)['lease_until'])
        self.assertEqual(self.runtime.pending_messages()[0]['kind'], 'attention')
        self.runtime.receive('chat', 'answer', 'topic', 'authorized follow-up')
        self.assertEqual(self.runtime.context(ticket_id)['status'], 'queued')
        self.assertGreater(self.runtime.claim(ticket_id).generation, assignment.generation)

    def test_new_input_during_execution_is_not_lost_on_result(self):
        ticket_id = self.ticket()
        assignment = self.runtime.claim(ticket_id)
        self.runtime.receive('chat', 'followup', 'topic', 'more work in this scope')
        self.runtime.report(assignment, 'result', 'first input processed')
        self.assertEqual(self.runtime.context(ticket_id)['status'], 'queued')
        self.assertEqual(len(self.runtime.context(ticket_id)['inputs']), 2)

    def test_reusing_message_key_for_changed_payload_is_rejected(self):
        assignment = self.runtime.claim(self.ticket())
        self.runtime.report(assignment, 'result', 'original result')
        with self.assertRaises(ValueError):
            self.runtime.report(assignment, 'result', 'different result')
        self.assertEqual(self.runtime.pending_messages()[0]['text'], 'original result')


if __name__ == '__main__':
    unittest.main()
