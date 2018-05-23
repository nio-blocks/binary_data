from struct import error
from unittest.mock import MagicMock, patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..pack_bytes_block import PackBytes


class TestPackBytes(NIOBlockTestCase):

    def test_process_signals(self):
        """Pack incoming values"""
        blk = PackBytes()
        self.configure_block(blk, {})
        blk.start()
        blk.process_signals([Signal({'key': 'foo', 'value': 42})])
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assert_last_signal_notified(Signal({'foo': b'\x00\x00\x00\x2A'}))

    def test_multiple_values(self):
        """Pack two values from one signal"""
        blk = PackBytes()
        self.configure_block(
            blk,
            {'new_attributes': [{'key': 'one', 'value': '{{ $value_1 }}'},
                                {'key': 'two', 'value': '{{ $value_2 }}'}]})
        blk.start()
        blk.process_signals([Signal({'value_1': 42, 'value_2': -42})])
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assert_last_signal_notified(Signal({'one': b'\x00\x00\x00*',
                                                 'two': b'\xff\xff\xff\xd6'}))

    def test_dynamic_data_types(self):
        """Pack incoming values according to signal evaluation"""
        blk = PackBytes()
        self.configure_block(
            blk,
            {'new_attributes': [{'format': '{{ $format }}',
                                 'endian': '{{ $endian }}',
                                 'length': '{{ $length }}',
                                 'key': '{{ $key }}'}]})
        blk.start()
        signal_list = [Signal({'format': 'unsigned_integer',
                               'endian': 'big',
                               'length': 2,
                               'key': 'uint',
                               'value': 255}),
                       Signal({'format': 'integer',
                               'endian': 'little',
                               'length': 4,
                               'key': 'int',
                               'value': -256}),
                       Signal({'format': 'float',
                               'endian': 'big',
                               'length': 8,
                               'key': 'float',
                               'value': 0.0})]
        blk.process_signals(signal_list)
        blk.stop()
        self.assert_last_signal_list_notified([
            Signal({'uint': b'\x00\xFF'}),
            Signal({'int': b'\x00\xFF\xFF\xFF'}),
            Signal({'float': b'\x00' * 8})])

    @patch(PackBytes.__module__ + '.pack')
    def test_format_not_available(self, mock_unpack):
        """Log a helpful error if the installed python version does not
        support the format specified"""
        mock_unpack.side_effect = error('bad char in struct format')
        blk = PackBytes()
        # py3.6+ is required to pack a float into 2 bytes, format char 'e'
        self.configure_block(blk, {'new_attributes': [{'format': 'float',
                                                       'key': 'foo',
                                                       'length': 'two',
                                                       'value': 42}]})
        blk.logger = MagicMock()
        blk.start()
        with self.assertRaises(error):
            blk.process_signals([Signal()])
        blk.stop()
        blk.logger.error.assert_called_once_with(
            'Python >= 3.6 is required to pack a float into 2 bytes')
        self.assert_num_signals_notified(0)
