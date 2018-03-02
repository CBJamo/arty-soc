CPU ?= lm32

base:
	rm -rf build
	./arty_base.py --nocompile-gateware --cpu-type $(CPU)
	cd firmware && make clean all
	./arty_base.py --cpu-type $(CPU)

base-s7:
	rm -rf build
	./arty_base.py --nocompile-gateware --cpu-type $(CPU) --with-s7
	cd firmware && make clean all
	./arty_base.py --cpu-type $(CPU) --with-s7

ddr3:
	rm -rf build
	./arty_ddr3.py

ddr3-s7:
	rm -rf build
	./arty_ddr3.py --with-s7

minisoc:
	rm -rf build
	./arty_base.py --with-ethernet --nocompile-gateware --cpu-type $(CPU)
	cd firmware && make clean all
	./arty_base.py --with-ethernet --cpu-type $(CPU)

etherbone:
	rm -rf build
	./arty_etherbone.py

load:
	./load.py

firmware:
	cd firmware && make clean all

load-firmware:
	litex_term --kernel firmware/firmware.bin COM10

.PHONY: load firmware load-firmware
