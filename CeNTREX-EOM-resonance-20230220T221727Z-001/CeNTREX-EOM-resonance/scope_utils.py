from dataclasses import dataclass
from typing import Sequence

import numpy as np
import numpy.typing as npt
import pyvisa
from tqdm import tqdm


def get_waveform(
    scope: pyvisa.resources.USBInstrument,
    ch,
    max_pts: int = 250_000,
    tqdm_on: bool = True,
):
    # set the scope data format
    scope.write(f":WAV:SOUR CHAN{ch}")
    scope.write(":WAV:MODE RAW")
    scope.write("WAV:FORM BYTE")

    # get & set waveform parameters
    mdepth = int(scope.query(":ACQ:MDEP?"))
    x_increment = float(scope.query(":WAV:XINC?"))
    x_origin = float(scope.query(":WAV:XOR?"))
    # x_reference = float(scope.query(":WAV:XREF?"))
    y_increment = float(scope.query(":WAV:YINC?"))
    y_origin = float(scope.query(":WAV:YOR?"))
    y_reference = float(scope.query(":WAV:YREF?"))

    # get waveform data from scope
    curve = np.zeros(mdepth)
    tqdm_sq = tqdm if tqdm_on else lambda x: x
    for i in tqdm_sq(range(int(np.ceil(mdepth / max_pts)))):
        # read a chunck from the scope
        i0, i1 = i * max_pts, i * max_pts + min(max_pts, mdepth - i * max_pts)
        scope.write(f":WAV:STAR {i0+1}")
        scope.write(f":WAV:STOP {i1}")
        scope.write(":WAV:DATA?")
        raw_data = scope.read_raw()[11:-1]
        curve[i0:i1] = np.frombuffer(raw_data, dtype=np.uint8).astype(float)

        # convert raw data into voltage and time
        volts = (curve - y_reference - y_origin) * y_increment
        t = np.linspace(x_origin, x_origin + x_increment * len(volts), len(volts))

        return t, volts


def set_scope(
    scope: pyvisa.resources.USBInstrument,
    ch: int,
    scale: float,
    offset: float,
    timebase: float,
    time_offset: float,
    coupling: str = "DC",
):
    # discretise the timebase
    steps = np.ravel([np.array([5, 2, 1]) * x for x in np.geomspace(10, 1e-9, 11)])[:-2]
    if timebase < 5e-9:
        tb = 5e-9
    for s in steps:
        if timebase >= s:
            tb = s
            break

    # vertical scale sanity check
    scale = 10 if scale > 10 else scale
    scale = 1e-3 if scale < 1e-3 else scale

    scope.write(f":TIM:MAIN:SCAL {tb:.1e}")
    scope.write(f":TIM:MAIN:OFFS {time_offset}")
    scope.write(f":CHAN{ch}:SCAL {scale}")
    scope.write(f":CHAN{ch}:COUP {coupling}")
    scope.write(f":CHAN{ch}:OFFS {offset}")


def set_trigger(scope, source_ch, level, mode="EDGE", slope="POS", coupling="DC"):
    scope.write(f":TRIG:MODE {mode}")
    scope.write(f":TRIG:COUP {coupling}")
    scope.write(f":TRIG:EDG:SOUR CHAN{source_ch}")
    scope.write(f":TRIG:EDG:SLOPE {slope}")
    scope.write(f":TRIG:EDG:LEV {level}")


@dataclass
class TraceData:
    timestamp: npt.NDArray[np.float_]
    transmission: npt.NDArray[np.float_]
    reflection: npt.NDArray[np.float_]


def get_trace_data(scope: pyvisa.resources.USBInstrument, channels: Sequence[int]):
    traces = []
    for ch in channels:
        t, signal = get_waveform(scope, ch, tqdm_on=False)
        traces.append(signal)
    return TraceData(t, *traces)
