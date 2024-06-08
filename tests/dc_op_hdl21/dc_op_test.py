import pytest
from vlsirtools import spice
from bandgaps.test_benches.dc_op_testbench import dut_schematic, DcOpSim, netlist_dirpath
# from tests.dc_op_hdl21.dc_op_testbench import dut_schematic, DcOpSim, netlist_dirpath


@pytest.fixture(scope="session")
def dcop_result():
    "Netlist and simulate the dcop test bench"
    opts = spice.SimOptions(
        simulator=spice.SupportedSimulators.NGSPICE,
        fmt=spice.ResultFormat.SIM_DATA,  # Get Python-native result types
        rundir="/workspaces/bandgaps/.viper/sims/dc_op_hdl21",  # Set the working directory for the simulation. Uses a temporary directory by default.
    )
    dut_schematic.netlist()
    dut_schematic.convert_top_to_lib(netlist_dirpath / "bandgap_1v_v01.lib")
    result = DcOpSim.run(opts)
    print("DC Op Simulation Complete!")
    return result

def test_vdd(dcop_result):
    assert len(dcop_result.an) > 0
    data = dcop_result.an[0].data
    assert data["v(vdd)"] == 1.8

def test_report_outputs(dcop_result):
    # results = NgspiceResultReader.read_raw_file("/workspaces/bandgaps/.viper/sims/dc_op_hdl21/netlist.raw")
    for analysis in dcop_result.an:
        print(f"analysis: {analysis.analysis_name}")
        for key,value in analysis.data.items():
            print(f"{key}: {value}")
        # print(analysis.data)
        print("\n")
