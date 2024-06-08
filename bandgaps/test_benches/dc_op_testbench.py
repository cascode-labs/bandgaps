from pathlib import Path
import hdl21
from hdl21 import Signal
from hdl21.sim import sim, Op, Include, Meas, Save, SaveMode
from hdl21.external_module import ExternalModule
from hdl21.primitives import Vdc, Cap, IdealCapacitorParams
from viper.schematics.XschemSchematic import XschemSchematic
from viper.results.NgspiceResultReader import NgspiceResultReader
from hdl21.prefix import f
import viper.config.oshic_sitepdks as _
import sky130
from vlsirtools import spice

prj_path = Path("/workspaces/bandgaps/")
lib_path = prj_path / "bandgaps" / "bandgap_sky130_v1"
dut_schematic_path = lib_path / "bandgap_1v_v01" / "bandgap_1v_v01.sch"
netlist_dirpath = prj_path / "tests/dc_op_hdl21/netlist"


dut_schematic = XschemSchematic(path=dut_schematic_path,
                                netlist_dirpath=netlist_dirpath)
dut_schematic.xschemrc_path = "/workspaces/bandgaps/xschemrc"

@hdl21.module
class DcOpTestbench:
    "Bandgap test bench"
    # sources
    VSS = hdl21.Port()  # The testbench interface: sole port VSS
    vdd = Signal(name="vdd")
    vbg = Signal(name="vbg")

    vdd_src = Vdc(dc=1.8)(p=vdd,n=VSS)
  
    C_load = Cap(c=10*f)(p=vbg, n=VSS)

    dut = ExternalModule(
        name="bandgap_1v_v01",
        port_list=[
            hdl21.Input(name="porst"),
            hdl21.Output(name="vbg"),
            hdl21.Input(name="VDD"),
            hdl21.Input(name="GND"),
        ],
        desc="1v bandgap reference",
    )()(porst=VSS, vbg=vbg, VDD=vdd, GND=VSS)

@sim
class DcOpSim:
    "Bandgap DC op simulation"
    tb = DcOpTestbench
    op_analysis = Op()
    # dc_netlist = Include(dut_schematic.netlist_filepath)
    bandgap_lib = Include(netlist_dirpath / "bandgap_1v_v01.lib")
    models = sky130.install.include(hdl21.pdk.Corner.TYP)

    meas_vdd = Meas(name = "vdd", expr="v(xtop.vdd)",analysis=op_analysis)
    meas_vbg = Meas(name = "vbg", expr="v(xtop.vbg)",analysis=op_analysis)
    save_vbg = Save(DcOpTestbench.vbg)
    saves = Include("/workspaces/bandgaps/.viper/sims/dc_op_hdl21/saves.sp")



    # = Lib(
    #     path=sky130.install.pdk_path / sky130.install.lib_path,
    #     section="tt"
    # )
    # save = Save(SaveMode.SELECTED)

if __name__ == "__main__":
    opts = spice.SimOptions(
        simulator=spice.SupportedSimulators.NGSPICE,
        fmt=spice.ResultFormat.SIM_DATA,  # Get Python-native result types
        rundir="/workspaces/bandgaps/.viper/sims/dc_op_hdl21",  # Set the working directory for the simulation. Uses a temporary directory by default.
    )
    dut_schematic.netlist()
    dut_schematic.convert_top_to_lib(netlist_dirpath / "bandgap_1v_v01.lib")
    results = DcOpSim.run(opts)
    # results = NgspiceResultReader.read_raw_file("/workspaces/bandgaps/.viper/sims/dc_op_hdl21/netlist.raw")
    for analysis in results.an:
        print(f"analysis: {analysis.analysis_name}")
        for key,value in analysis.data.items():
            print(f"{key}: {value}")
        # print(analysis.data)
        print("\n")
