from pathlib import Path
import hdl21
from hdl21.sim import sim, Op, Include, Lib
from hdl21.external_module import ExternalModule
from hdl21.primitives import Vdc, Cap, IdealCapacitorParams
from hdl21.schematic.xschem_schematic import XschemSchematic
from hdl21.prefix import f
import viper.oshic_sitepdks as _
import sky130


prj_path = Path("/workspaces/prjs/bandgapReferenceCircuit")
lib_path = prj_path / "bandgap_sky130_v1"
dut_schematic_path = lib_path / "bandgap_1v_v01.sch"
netlist_dirpath = prj_path / "tests/dc_op_hdl21/netlist"

dut_schematic = XschemSchematic(path=dut_schematic_path,
                                netlist_dirpath=netlist_dirpath)

@hdl21.module
class DcOpTestbench:
    "Bandgap test bench"
    # sources
    VSS = hdl21.Port()  # The testbench interface: sole port VSS
    vdd = Vdc(dc=1.8)(n=VSS)  # A DC voltage source  

    # Load
    C_load = Cap(c=10*f)(n=VSS)

    dut = ExternalModule(
        name="bandgap_1v_v01",
        port_list=[
            hdl21.Output(name="vbg"),
            hdl21.Input(name="VDD"),
            hdl21.Input(name="GND"),
        ],
        desc="1v bandgap reference",
        )()(vbg=C_load.p, VDD=vdd.p, GND=VSS)

@sim
class DcOpSim:
    "Bandgap DC op simulation"
    tb = DcOpTestbench
    op_analysis = Op()
    dc_netlist = Include(dut_schematic.netlist_filepath)
    models = Lib(
        path=sky130.install.model_lib,
        section="tt"
    )

if __name__ == "__main__":
    dut_schematic.netlist()
    DcOpSim.run()