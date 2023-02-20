import matplotlib.pyplot as plt
import numpy as np
import pyvisa
from windfreak import SynthHD
import time
import tqdm
import csv
from typing import List, Tuple
import datetime

resource_name_windfreak = "COM4"

synthd = SynthHD(resource_name_windfreak)
synthd.init()

rf_out = 0

synthd[rf_out].frequency = 100e6
synthd[rf_out].power = -10
synthd[rf_out].enable = True

for shdpower in tqdm.tqdm(np.linspace(-30, 0, 51)):
    synthd[rf_out].power = shdpower
    time.sleep(1)

synthd[rf_out].power = -20
synthd[rf_out].enable = False
