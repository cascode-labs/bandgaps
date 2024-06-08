from pathlib import Path

import hdl21 as h
from hdl21.sim import Op, Include, Save, SaveMode, sim
import viper.config.oshic_sitepdks as _
from vlsirtools import spice
import sky130

# bandgap = h.SchematicModule(
#     name="bandgap_01",
#     desc="The bandgap top-level",
#     domain="xschem schematic",
#     port_list=[h.Inout(name="PLUS"), h.Inout(name="MINUS")],
#     schematic_path=Path("/workspaces/bandgaps/.viper/netlists/bandgap_1v_v01.spice"),
# )

bandgap = h.ExternalModule(
    name="bandgap_1v_v01",
    desc="A bandgap",
    port_list=[h.Port(name="porst"), h.Port(name="vbg"), h.Port(name="VDD"), h.Port(name="GND")],
)

@sim
class BandgapDcopSim:
    """# Bandgap DC Operating Point Simulation Input"""

    @h.module
    class Tb:
        """# Basic Mos Testbench"""

        VSS = h.Port()  # The testbench interface: sole port VSS
        vdc = h.Vdc(dc=1.8)(p=vdd,n=VSS)  # A DC voltage source
        dut = bandgap()()

    # Simulation Stimulus
    op = Op()
    mod = sky130.install.include(h.pdk.Corner.TYP)
    save = Save(SaveMode.ALL)


def run():
    """# Run the simulation."""

    # Set a few runtime options.
    # If you'd like a different simulator, this and the check below are the place to specify it!
    opts = spice.SimOptions(
        simulator=spice.SupportedSimulators.NGSPICE,
        fmt=spice.ResultFormat.SIM_DATA,  # Get Python-native result types
        rundir="/workspaces/bandgaps/.viper/sims",  # Set the working directory for the simulation. Uses a temporary directory by default.
    )
    if not spice.ngspice.available():
        print("ngspice is not available. Skipping simulation.")
        return

    # Run the simulation!
    results = BandgapDcopSim.run(opts)

if __name__ == "__main__":
    run()
