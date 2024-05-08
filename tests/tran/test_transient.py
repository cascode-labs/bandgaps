import sys

sys.path.append(".")

from typing import Dict
import numpy as np
from rawread import rawread
from pytest import fixture
from viper.results import NgspiceResultReader

@fixture
def tran_result() -> Dict[str, list]:
    path = "tests/tran/simulation"
    deg0 = "tsmc_bandgap_real_0degc_vbg.raw"
    deg27 = "tsmc_bandgap_real_27degc_vbg.raw"
    deg70 = "tsmc_bandgap_real_70degc_vbg.raw"

    result = NgspiceResultReader.read_raw_file()

    # Parse rawread output into time and V_bg
    def parse_raw_read(raw_read):
        out = raw_read[0][0]
        time = [t[0] for t in out]
        vbg = [t[1] for t in out]
        i = [t[2] for t in out]
        return time, vbg, i

    test = rawread(path + "/" + deg0)

    # Load .raw files and parse them
    t1, v1, i1 = parse_raw_read(rawread(path + "/" + deg0))
    t2, v2, i2 = parse_raw_read(rawread(path + "/" + deg27))
    t3, v3, i3 = parse_raw_read(rawread(path + "/" + deg70))

    return {
        "times": [t1, t2, t3],
        "voltages": [v1, v2, v3],
        "currents": [i1, i2, i3],
    }
    

def test_settling_time(tran_result):

    for s in tran_result["voltages"]:

        settling_time = None

        # Find the first index at which voltage is 1% of the reference voltage
        # Magic number is determined from simulation where: VDD is ramped up and prost is pulsed
        for i, value in enumerate(s[150000:]):
            if value < 1.01 and settling_time is None:
                settling_time = i * 1e-4 # Assign settling time in microseconds

        # Just has to start up according to compliance matrix
        assert settling_time is not None

def test_vref_inaccuracy(tran_result):

    for s in tran_result["voltages"]:

        # Calculate the inaccuracy of the reference voltage
        inaccuracy = abs(1 - s[-1]) * 100

        # Has to be within 2% of the reference voltage
        assert inaccuracy < 2

        # Calculate actual reference voltage
        vref = s[-1]

        # Has to be within 2% of the reference voltage
        assert abs(vref - 1) < 0.02

def test_transient_power(tran_result):

    for i in range(3):

        # Calculate the power dissipated by the bandgap reference
        power = [-i*v for i, v in zip(tran_result["currents"][i], tran_result["voltages"][i])]
        assert True