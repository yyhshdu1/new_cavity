import numpy as np


def watt_to_dBm(watt: float) -> float:
    return 10 * np.log10(watt * 1e3)


def Vrms_to_watt(Vrms: float) -> float:
    # 50 Ohm impedance
    return Vrms**2 / 50


def Vpp_to_Vrms(Vpp: float) -> float:
    return (Vpp / 2) / np.sqrt(2)


def Vpp_to_dBm(Vpp: float) -> float:
    Vrms = Vpp_to_Vrms(Vpp)
    watt = Vrms_to_watt(Vrms)
    dBm = watt_to_dBm(watt)
    return dBm


def dBm_to_watt(dBm: float) -> float:
    return 10 ** (dBm / 10) / 1000


def watt_to_Vrms(watt: float) -> float:
    # 50 Ohm impedance
    return np.sqrt(watt * 50)


def Vrms_to_Vpp(Vrms: float) -> float:
    return (Vrms * np.sqrt(2)) * 2


def dBm_to_Vpp(dBm: float) -> float:
    watt = dBm_to_watt(dBm)
    Vrms = watt_to_Vrms(watt)
    return Vrms_to_Vpp(Vrms)
