#!/usr/bin/env python3

from arty_base import *

from litex.soc.cores.uart import UARTWishboneBridge

from litescope import LiteScopeAnalyzer


class BaseSoC(SoCSDRAM):
    csr_peripherals = {
        "ddrphy",
        "dna",
        "xadc",
        "generator",
        "checker",
        "analyzer",
    }
    csr_map_update(SoCSDRAM.csr_map, csr_peripherals)

    def __init__(self, platform,
                 with_sdram_bist=True, bist_async=False, bist_random=True,
                 with_analyzer=False):
        clk_freq = int(100e6)
        SoCSDRAM.__init__(self, platform, clk_freq,
            cpu_type=None,
            l2_size=32,
            csr_data_width=32,
            with_uart=False,
            with_timer=False)

        self.submodules.crg = CRG(platform)
        self.submodules.dna = dna.DNA()
        self.submodules.xadc = xadc.XADC()

        self.crg.cd_sys.clk.attr.add("keep")
        self.platform.add_period_constraint(self.crg.cd_sys.clk, period_ns(100e6))

        # sdram
        self.submodules.ddrphy = a7ddrphy.A7DDRPHY(platform.request("ddram"))
        sdram_module = MT41K128M16(self.clk_freq, "1:4")
        self.register_sdram(self.ddrphy,
                            sdram_module.geom_settings,
                            sdram_module.timing_settings)

        # sdram bist
        if with_sdram_bist:
            generator_user_port = self.sdram.crossbar.get_port(cd="clk50" if bist_async else "sys")
            self.submodules.generator = LiteDRAMBISTGenerator(generator_user_port, random=bist_random)

            checker_user_port = self.sdram.crossbar.get_port(cd="clk50" if bist_async else "sys")
            self.submodules.checker = LiteDRAMBISTChecker(checker_user_port, random=bist_random)

        # uart
        self.add_cpu_or_bridge(UARTWishboneBridge(platform.request("serial"), clk_freq, baudrate=115200))
        self.add_wb_master(self.cpu_or_bridge.wishbone)

        # analyzer
        if with_analyzer:
            generator_group = [
                generator_user_port.cmd.valid,
                generator_user_port.cmd.ready,
                generator_user_port.cmd.we,
                generator_user_port.cmd.adr,

                generator_user_port.wdata.valid,
                generator_user_port.wdata.ready,
                generator_user_port.wdata.we
            ]
            checker_group = [
                checker_user_port.cmd.valid,
                checker_user_port.cmd.ready,
                checker_user_port.cmd.we,
                checker_user_port.cmd.adr,

                checker_user_port.rdata.valid,
                checker_user_port.rdata.ready
            ]
            analyzer_signals = {
                0 : generator_group,
                1 : checker_group
            }
            self.submodules.analyzer = LiteScopeAnalyzer(analyzer_signals, 512)

    def do_exit(self, vns):
        if hasattr(self, "analyzer"):
            self.analyzer.export_csv(vns, "test/analyzer.csv")


def main():
    parser = argparse.ArgumentParser(description="Arty LiteX SoC")
    builder_args(parser)
    soc_sdram_args(parser)
    args = parser.parse_args()

    platform = arty.Platform()
    soc = BaseSoC(platform, **soc_sdram_argdict(args))
    builder = Builder(soc, output_dir="build", csr_csv="test/csr.csv")
    vns = builder.build()
    soc.do_exit(vns)

if __name__ == "__main__":
    main()
