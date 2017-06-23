from litex.soc.tools.remote import RemoteClient
from litescope.software.driver.analyzer import LiteScopeAnalyzerDriver

wb = RemoteClient()
wb.open()

# # #

analyzer = LiteScopeAnalyzerDriver(wb.regs, "analyzer", debug=True)
analyzer.configure_trigger(cond={"pmoda_0": 0})
analyzer.configure_subsampler(64)
analyzer.run(offset=128, length=8192)
analyzer.wait_done()
analyzer.upload()
analyzer.save("dump.sr")

# # #

wb.close()
