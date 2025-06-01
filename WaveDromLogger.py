class WaveDromLogger:
    def __init__(self):
        self.log = {}
        self.prev = {}
        for sig in ["PCLK"] + CONTROL_SIGS:
            self.log[sig] = ""
            self.prev[sig] = None
        for sig in DATA_SIGS:
            self.log[sig] = ["",[]]
            self.prev[sig] = None
        self.cycle = 0

    def record(self, sig):
        # PCLK
        clk = "P" if logger.cycle % 2 == 0 else "."
        self.log["PCLK"] += str(clk)
        logger.cycle += 1

        for field in CONTROL_SIGS:
            if self.prev[field] == sig[field]:
                self.log[field] += "."
            else:
                self.log[field] += str(sig[field])
                self.prev[field] = sig[field]

        for field in DATA_SIGS:
            if self.prev[field] == sig[field]:
                self.log[field][0] += "."
            else:
                self.log[field][0] += "3"
                self.log[field][1].append(hex(sig[field]).upper())
                self.prev[field] = sig[field]

    def to_json(self):
        wavedrom_list = []
        for field in ["PCLK"]+CONTROL_SIGS:
            signal_entry = {"name": field, "wave": self.log[field]}
            wavedrom_list.append(signal_entry)
        for field in DATA_SIGS:
            wave, data = self.log[field]
            signal_entry = {"name": field, "wave": wave, "data": data}
            wavedrom_list.append(signal_entry)
        return {"signal": wavedrom_list}
