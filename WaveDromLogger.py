class WaveformLogger:
    def __init__(self):
        self.log = {}
        self.prev = {}
        self.clk_sig = None
        self.ctrl_sigs = None
        self.data_sigs = None

    def init_signals(self, signals):
        self.clk_sig = signals.ClkSig
        self.ctrl_sigs = signals.CtrlSigs
        self.data_sigs = signals.DataSigs

        for sig in [self.clk_sig] + self.ctrl_sigs:
            self.log[sig] = ""
            self.prev[sig] = None

        for sig in self.data_sigs:
            self.log[sig] = ["", []]
            self.prev[sig] = None

        self.cycle = 0

    def record(self, current_signals):
        clk = "P" if self.cycle % 2 == 0 else "."
        self.log[self.clk_sig] += str(clk)
        self.cycle += 1

        for sig in self.ctrl_sigs:
            if self.prev[sig] == current_signals[sig]:
                self.log[sig] += "."
            else:
                self.log[sig] += str(current_signals[sig])
                self.prev[sig] = current_signals[sig]

        for sig in self.data_sigs:
            if self.prev[sig] == current_signals[sig]:
                self.log[sig][0] += "."
            else:
                self.log[sig][0] += "3"
                self.log[sig][1].append(hex(current_signals[sig]).upper())
                self.prev[sig] = current_signals[sig]

    def to_json(self):
        wavedrom_list = []
        for sig in [self.clk_sig] + self.ctrl_sigs:
            signal_entry = {"name": sig, "wave": self.log[sig]}
            wavedrom_list.append(signal_entry)
        for sig in self.data_sigs:
            wave, data = self.log[sig]
            signal_entry = {"name": sig, "wave": wave, "data": data}
            wavedrom_list.append(signal_entry)
        return {"signal": wavedrom_list}


