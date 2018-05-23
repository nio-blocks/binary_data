from enum import Enum
from struct import unpack, error
from nio import Block, Signal
from nio.block.mixins.enrich.enrich_signals import EnrichSignals
from nio.properties import Property, BoolProperty, ListProperty, \
                           SelectProperty, StringProperty, VersionProperty, \
                           PropertyHolder


class PythonType(Enum):
    unsigned_integer = 'uint'
    integer = 'int'
    float = 'float'

class Endian(Enum):
    little = '<'
    big = '>'

class NewAttributes(PropertyHolder):
    format = SelectProperty(PythonType,
                            title='Format',
                            default=PythonType.integer)
    endian = SelectProperty(Endian, title='Endian', default=Endian.big)
    key = StringProperty(title='New Attribute Key', default='{{ $key }}')
    value = Property(title='Bytes to Unpack', default='{{ $value }}')

class UnpackBytes(EnrichSignals, Block):

    new_attributes = ListProperty(NewAttributes,
                                  title='New Signal Attributes',
                                  default=[{'format': 'integer',
                                             'endian': 'big',
                                             'key': '{{ $key }}',
                                             'value': '{{ $value }}'}])
    version = VersionProperty('0.1.0')

    def process_signals(self, signals):
        outgoing_signals = []
        for signal in signals:
            new_signal_dict = {}
            for attr in self.new_attributes():
                _bytes = attr.value(signal)
                _type = attr.format(signal).value
                _endian = attr.endian(signal).value
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
                    elif len(_bytes) == 4:
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
                            self.logger.error('Python >= 3.6 is required to '
                                              'unpack 2 bytes into a float')
                        raise e
                    new_signal_dict[attr.key(signal)] = value
            if new_signal_dict:
                new_signal = self.get_output_signal(new_signal_dict, signal)
                outgoing_signals.append(new_signal)
        self.notify_signals(outgoing_signals)
