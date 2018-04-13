from enum import Enum
from struct import unpack, error
from nio import Block, Signal
from nio.properties import Property, BoolProperty, SelectProperty, \
                           StringProperty, VersionProperty


class PythonType(Enum):
    unsigned_integer = 'uint'
    integer = 'int'
    float = 'float'

class Endian(Enum):
    little = '<'
    big = '>'

class UnpackBytes(Block):

    format = SelectProperty(PythonType,
                            title='Format',
                            default=PythonType.integer)
    endian = SelectProperty(Endian, title='Endian', default=Endian.big)
    key = StringProperty(title='New Attribute Key', default='{{ $key }}')
    value = Property(title='Bytes to Unpack', default='{{ $value }}')
    version = VersionProperty('0.1.0')

    def process_signals(self, signals):
        outgoing_signals = []
        for signal in signals:
            _bytes = self.value(signal)
            _type = self.format(signal).value
            _endian = self.endian(signal).value
            fmt_char = None
            if _type in ['int', 'uint']:
                if len(_bytes) == 2:
                    fmt_char = 'h'
                elif len(_bytes) == 4:
                    fmt_char = 'i'
                elif len(_bytes) == 8:
                    fmt_char = 'q'
                if _type == 'uint':
                    fmt_char = fmt_char.upper()
            elif _type == 'float':
                if len(_bytes) == 2:
                    fmt_char = 'e'  # added in python 3.6
                if len(_bytes) == 4:
                    fmt_char = 'f'
                elif len(_bytes) == 8:
                    fmt_char = 'd'
            if fmt_char == None:
                self.logger.error('cannot unpack {} bytes into {}'.format(
                        len(_bytes), _type))
            else:
                fmt = _endian + fmt_char
                try:
                    value = unpack(fmt, _bytes)[0]
                except error as e:
                    if e.args[-1] == 'bad char in struct format':
                        self.logger.error('Python >= 3.6 is required to unpack'
                                          ' 2 bytes into a float')
                    raise e
                new_signal_dict = {self.key(signal): value}
                outgoing_signals.append(Signal(new_signal_dict))
        self.notify_signals(outgoing_signals)
