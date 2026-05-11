def format_data_list(data):
    items = []

    for value in data:
        items.append('"' + str(value) + '"')

    return "[" + ", ".join(items) + "]"


def make_bus_wave(trace, signal_index, signal_name, value_func):
    wave = ""
    data = []
    symbols = ["3", "4", "5", "6", "7", "8", "9"]
    symbol_index = 0
    previous_value = None

    for i in range(len(trace)):
        value = trace[i][signal_index]

        if i > 0 and value == previous_value:
            wave += "."
        else:
            wave += symbols[symbol_index % len(symbols)]
            data.append(value_func(value))
            symbol_index += 1

        previous_value = value

    return {"name": signal_name, "wave": wave, "data": data}


def make_bit_wave(trace, signal_index, signal_name):
    wave = ""
    previous_value = None

    for i in range(len(trace)):
        value = trace[i][signal_index]

        if i > 0 and value == previous_value:
            wave += "."
        elif value == 0:
            wave += "0"
        elif value == 1:
            wave += "1"
        else:
            wave += "x"

        previous_value = value

    return {"name": signal_name, "wave": wave}


def trace_to_wavedrom(trace):
    p = AHBLiteProtocol()

    wavedrom = {
        "signal": [
            {"name": "HCLK", "wave": "p" + "." * (len(trace) - 1)},
            make_bus_wave(trace, AHBTrace.HTRANS, "HTRANS", p.htrans_name),
            make_bus_wave(trace, AHBTrace.HADDR, "HADDR", p.to_hex),
            make_bit_wave(trace, AHBTrace.HWRITE, "HWRITE"),
            make_bus_wave(trace, AHBTrace.HSIZE, "HSIZE", str),
            make_bus_wave(trace, AHBTrace.HBURST, "HBURST", p.hburst_name),
            make_bit_wave(trace, AHBTrace.HREADY, "HREADY"),
            make_bus_wave(trace, AHBTrace.HRDATA, "HRDATA", p.to_hex)
        ]
    }

    return wavedrom


def print_wavedrom(wavedrom):
    print("{")
    print("  signal: [")

    signals = wavedrom["signal"]

    for i in range(len(signals)):
        sig = signals[i]
        line = '    { name: "' + sig["name"] + '", wave: "' + sig["wave"] + '"'

        if "data" in sig:
            line += ", data: " + format_data_list(sig["data"])

        line += " }"

        if i != len(signals) - 1:
            line += ","

        print(line)

    print("  ],\n\n  head: { tick: 0 },\n\n  config: { hscale: 2 }\n}")


trace = generator.get_trace()
wavedrom = trace_to_wavedrom(trace)
print_wavedrom(wavedrom)
