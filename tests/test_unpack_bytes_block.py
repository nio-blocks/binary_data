from struct import error
from unittest.mock import MagicMock, patch
from nio import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..unpack_bytes_block import UnpackBytes


class TestUnpackBytes(NIOBlockTestCase):

    def test_integers(self):
        """Unpack an incoming integer"""
        blk = UnpackBytes()
        self.configure_block(blk, {})
        blk.start()
        blk.process_signals([
            Signal({'key': 'foo', 'value': bytes(7) + b'\x42'}),
            Signal({'key': 'bar', 'value': b'\x00\x00\x00\x42'}),
            Signal({'key': 'baz', 'value': b'\x00\x42'})])
        blk.stop()
        self.assert_num_signals_notified(3)
        self.assert_signal_list_notified([
            Signal({'foo': 66}),
            Signal({'bar': 66}),
            Signal({'baz': 66})])

    def test_dynamic_data_types(self):
        """Unpack incoming bytes according to signal evaluation"""
        blk = UnpackBytes()
        self.configure_block(blk, {'format': '{{ $format }}',
                                   'endian': '{{ $endian }}'})
        blk.start()
        signal_list = [Signal({'format': 'unsigned_integer',
                               'endian': 'big',
                               'key': 'uint',
                               'value': b'\x00\xFF'}),
                       Signal({'format': 'integer',
                               'endian': 'little',
                               'key': 'int',
                               'value': b'\x00\xFF'}),
                       Signal({'format': 'float',
                               'endian': 'big',
                               'key': 'float',
                               'value': b'\x00\x00\x00\x00'})]
        blk.process_signals(signal_list)
        blk.stop()
        self.assert_signal_list_notified([Signal({'uint': 255}),
                                          Signal({'int': -256}),
                                          Signal({'float': 0.0})])

    def test_invalid_length(self):
        blk = UnpackBytes()
        self.configure_block(blk, {'key': 'foo', 'value': b'\x00\x00\x00'})
        blk.logger = MagicMock()
        blk.start()
        blk.process_signals([Signal()])
        blk.stop()
        blk.logger.error.assert_called_once_with(
            'cannot unpack 3 bytes into int')
        self.assert_num_signals_notified(0)

    @patch(UnpackBytes.__module__ + '.unpack')
    def test_format_not_available(self, mock_unpack):
        """log a helpful error if the installed python version does not
        support the format specified"""
        mock_unpack.side_effect = error('bad char in struct format')
        blk = UnpackBytes()
        # py3.6+ is required to unpack 2 bytes into a float, format char 'e'
        self.configure_block(blk, {'format': 'float',
                                   'key': 'foo',
                                   'value': b'\x00\x00'})
        blk.logger = MagicMock()
        blk.start()
        with self.assertRaises(error):
            blk.process_signals([Signal()])
        blk.stop()
        blk.logger.error.assert_called_once_with(
            'Python >= 3.6 is required to unpack 2 bytes into a float')
        self.assert_num_signals_notified(0)
