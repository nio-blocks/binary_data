from struct import pack
from nio import Block, Signal
from nio.properties import Property, StringProperty, VersionProperty


class PackBytes(Block):

    format = StringProperty(title='Format Character', default='')
    order = StringProperty(title='Byte Order Character', default='')
    data = Property(title='Data to Pack')
    version = VersionProperty('0.1.0')

    def process_signals(self, signals):
        outgoing_signals = []
        for signal in signals:
            bytes = pack(self.format(signal), self.data(signal))
            outgoing_signals.append(Signal({'data': bytes}))
        self.notify_signals(outgoing_signals)
