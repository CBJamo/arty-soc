#!/usr/bin/env python3

from arty_etherbone import *

from migen.genlib.cdc import MultiReg

from litescope import LiteScopeAnalyzer

class AnalyzerSoC(EtherboneSoC):
    csr_peripherals = {
        "analyzer",
    }
    csr_map_update(EtherboneSoC.csr_map, csr_peripherals)

    def __init__(self, platform):
        EtherboneSoC.__init__(self, platform)

        pmoda = platform.request("pmoda")

        # use name override to keep naming in capture
        pmoda_0 = Signal(name_override="pmoda_0")
        pmoda_1 = Signal(name_override="pmoda_1")
        pmoda_2 = Signal(name_override="pmoda_2")
        pmoda_3 = Signal(name_override="pmoda_3")
        pmoda_4 = Signal(name_override="pmoda_4")
        pmoda_5 = Signal(name_override="pmoda_5")
        pmoda_6 = Signal(name_override="pmoda_6")
        pmoda_7 = Signal(name_override="pmoda_7")
        # deglitch with multireg
        self.specials += [
            MultiReg(pmoda[0], pmoda_0),
            MultiReg(pmoda[1], pmoda_1),
            MultiReg(pmoda[2], pmoda_2),
            MultiReg(pmoda[3], pmoda_3),
            MultiReg(pmoda[4], pmoda_4),
            MultiReg(pmoda[5], pmoda_5),
            MultiReg(pmoda[6], pmoda_6),
            MultiReg(pmoda[7], pmoda_7)
        ]
        analyzer_signals = [
            pmoda_0,
            pmoda_1,
            pmoda_2,
            pmoda_3,
            pmoda_4,
            pmoda_5,
            pmoda_6,
            pmoda_7
        ]
        self.submodules.analyzer = LiteScopeAnalyzer(analyzer_signals, 8192)

    def do_exit(self, vns):
        if hasattr(self, "analyzer"):
            self.analyzer.export_csv(vns, "test/analyzer.csv")


def main():
    parser = argparse.ArgumentParser(description="Arty LiteX SoC")
    builder_args(parser)
    parser.add_argument("--nocompile-gateware", action="store_true")
    args = parser.parse_args()

    platform = arty.Platform()
    soc = AnalyzerSoC(platform)
    builder = Builder(soc, output_dir="build",
                      compile_gateware=not args.nocompile_gateware,
                      csr_csv="test/csr.csv")
    vns = builder.build()
    soc.do_exit(vns)

if __name__ == "__main__":
    main()

