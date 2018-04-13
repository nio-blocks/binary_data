from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..pack_bytes_block import PackBytes


class TestPackBytes(NIOBlockTestCase):

    def test_process_signals(self):
        """Pack incoming values"""
        blk = PackBytes()
        self.configure_block(blk, {'format': '{{ $type }}',
                                   'order': '{{ $endian }}',
                                   'data': '{{ $value }}'})
        blk.start()
        blk.process_signals([Signal({'type': 'i', 'endian': '', 'value': 42})])
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assert_last_signal_notified(Signal({'data': b'\x2A\x00\x00\x00'}))
