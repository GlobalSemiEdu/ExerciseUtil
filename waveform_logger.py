"""
General Waveform Logger
Works with any protocol that implements the required methods:
- get_clock_signal()
- get_control_signals()
- get_data_signals()
- get_data_validity()
"""


class WaveformLogger:
    """Logs bus signals for waveform generation (WaveDrom format)"""

    def __init__(self, protocol):
        """
        Initialize logger with a protocol

        Args:
            protocol: Protocol instance with required methods
        """
        self.protocol = protocol
        self.waves = {}
        self.prev = {}

        # Initialize waves for clock signal
        clk_sig = protocol.get_clock_signal()
        self.waves[clk_sig] = ''

        # Initialize waves for control signals
        for sig in protocol.get_control_signals():
            self.waves[sig] = ''
            self.prev[sig] = None

        # Initialize waves for data signals
        for sig in protocol.get_data_signals():
            self.waves[sig] = ['', []]
            self.prev[sig] = None

    def record(self, signals):
        """
        Record current bus state

        Args:
            signals: Dictionary of signal name -> value
        """
        # Record clock
        clk_sig = self.protocol.get_clock_signal()
        self.waves[clk_sig] += 'P'

        # Record control signals
        for sig in self.protocol.get_control_signals():
            val = signals.get(sig, 0)
            if sig not in self.prev or self.prev[sig] != val:
                self.waves[sig] += str(val)
                self.prev[sig] = val
            else:
                self.waves[sig] += '.'

        # Record data signals with validity checking
        data_validity = self.protocol.get_data_validity()
        for sig in self.protocol.get_data_signals():
            value = signals.get(sig, 0)
            validity_fn = data_validity[sig]
            is_valid = validity_fn(signals)

            if sig == "HRDATA" and value == 0xDEAD:
                is_valid = False

            self._record_data_signal(sig, value, is_valid)

    def _record_data_signal(self, name, value, is_valid):
        """Record a data signal with validity checking"""
        if not is_valid:
            if name not in self.prev or self.prev[name] != 'INVALID':
                self.waves[name][0] += 'x'
                self.prev[name] = 'INVALID'
            else:
                self.waves[name][0] += '.'
        else:
            if name not in self.prev or self.prev[name] != value or self.prev[name] == 'INVALID':
                self.waves[name][0] += '='
                self.waves[name][1].append(hex(value))
                self.prev[name] = value
            else:
                self.waves[name][0] += '.'

    def to_wavedrom(self):
        """Convert to WaveDrom JSON format"""
        signals = []

        # Clock signal first
        clk_sig = self.protocol.get_clock_signal()
        signals.append({'name': clk_sig, 'wave': self.waves[clk_sig]})

        # Control signals
        for sig in self.protocol.get_control_signals():
            signals.append({'name': sig, 'wave': self.waves[sig]})

        # Data signals
        for sig in self.protocol.get_data_signals():
            wave, data = self.waves[sig]
            signals.append({'name': sig, 'wave': wave, 'data': data})

        return {'signal': signals}