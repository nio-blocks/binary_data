from enum import Enum
from struct import pack, error
from nio import Block
from nio.block.mixins.enrich.enrich_signals import EnrichSignals
from nio.properties import Property, BoolProperty, ListProperty, \
                           SelectProperty, StringProperty, VersionProperty, \
                           PropertyHolder


class Length(Enum):
    two = 2
    four = 4
    eight = 8

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
    value = Property(title='Value to Pack', default='{{ $value }}')
    length = SelectProperty(Length,
                            title='Packed Length (Bytes)',
                            default=Length.four)


class PackBytes(EnrichSignals, Block):

    new_attributes = ListProperty(NewAttributes,
                                  title='New Signal Attributes',
                                  default=[{'format': 'integer',
                                             'endian': 'big',
                                             'key': '{{ $key }}',
                                             'value': '{{ $value }}',
                                             'length': 'four'}])
    version = VersionProperty('0.1.0')

    def process_signals(self, signals):
        outgoing_signals = []
        for signal in signals:
            new_signal_dict = {}
            for attr in self.new_attributes():
                _value = attr.value(signal)
                _type = attr.format(signal).value
                _endian = attr.endian(signal).value
                _length = attr.length(signal).value
                fmt_char = None
                if _type in ['int', 'uint']:
                    if _length == 2:
                        fmt_char = 'h'
                    elif _length == 4:
                        fmt_char = 'i'
                    elif _length == 8:
                        fmt_char = 'q'
                    if _type == 'uint':
                        fmt_char = fmt_char.upper()
                else:
                    if _length == 2:
                        fmt_char = 'e'  # added in python 3.6
                    if _length == 4:
                        fmt_char = 'f'
                    elif _length == 8:
                        fmt_char = 'd'
                fmt = _endian + fmt_char
                try:
                    value = pack(fmt, _value)
                except error as e:
                    if e.args[-1] == 'bad char in struct format':
                        self.logger.error('Python >= 3.6 is required to '
                                          'pack a float into 2 bytes')
                    raise e
                new_signal_dict[attr.key(signal)] = value
            if new_signal_dict:
                new_signal = self.get_output_signal(new_signal_dict, signal)
                outgoing_signals.append(new_signal)
        self.notify_signals(outgoing_signals)
