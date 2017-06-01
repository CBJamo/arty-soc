#!/usr/bin/env python3

from arty_base import *

from litex.soc.integration.soc_core import *

from liteeth.common import convert_ip
from liteeth.phy.mii import LiteEthPHYMII
from liteeth.core import LiteEthUDPIPCore
from liteeth.frontend.etherbone import LiteEthEtherbone


class EtherboneSoC(BaseSoC):
    csr_peripherals = {
        "ethphy",
        "ethcore",
    }
    csr_map_update(BaseSoC.csr_map, csr_peripherals)

    def __init__(self, platform, mac_address=0x10e2d5000000, ip_address="192.168.1.50"):
        BaseSoC.__init__(self, platform, cpu_type=None, csr_data_width=32)

        # ethernet mac/udp/ip stack
        self.submodules.ethphy = LiteEthPHYMII(self.platform.request("eth_clocks"),
                                               self.platform.request("eth"))
        self.submodules.ethcore = LiteEthUDPIPCore(self.ethphy,
                                                   mac_address,
                                                   convert_ip(ip_address),
                                                   self.clk_freq,
                                                   with_icmp=True)

        # etherbone bridge
        self.add_cpu_or_bridge(LiteEthEtherbone(self.ethcore.udp, 20000))
        self.add_wb_master(self.cpu_or_bridge.wishbone.bus)

        self.ethphy.crg.cd_eth_rx.clk.attr.add("keep")
        self.ethphy.crg.cd_eth_tx.clk.attr.add("keep")
        self.platform.add_period_constraint(self.ethphy.crg.cd_eth_rx.clk, period_ns(125e6))
        self.platform.add_period_constraint(self.ethphy.crg.cd_eth_tx.clk, period_ns(125e6))

        self.platform.add_false_path_constraints(
            self.crg.cd_sys.clk,
            self.ethphy.crg.cd_eth_rx.clk,
            self.ethphy.crg.cd_eth_tx.clk)


def main():
    parser = argparse.ArgumentParser(description="Arty LiteX SoC")
    builder_args(parser)
    parser.add_argument("--nocompile-gateware", action="store_true")
    args = parser.parse_args()

    platform = arty.Platform()
    soc = EtherboneSoC(platform)
    builder = Builder(soc, output_dir="build",
                      compile_gateware=not args.nocompile_gateware,
                      csr_csv="test/csr.csv")
    vns = builder.build()

if __name__ == "__main__":
    main()

