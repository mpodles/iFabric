
BMV2_SWITCH_EXE = simple_switch_grpc
TOPO = sig-topo/topology_old.json
BUILD_DIR = build
PCAP_DIR = pcaps
LOG_DIR = logs
P4C = p4c-bm2-ss
P4C_ARGS += --p4runtime-files $(BUILD_DIR)/$(basename $@).p4.p4info.txt

RUN_SCRIPT = ./run_exercise.py

ifndef TOPO
TOPO = topology.json
endif

source = $(wildcard build/*.p4)
compiled_json := $(source:.p4=.json)

ifndef DEFAULT_PROG
DEFAULT_PROG = fabric_tunnel.json
endif
DEFAULT_JSON = $(BUILD_DIR)/$(DEFAULT_PROG)

# Define NO_P4 to start BMv2 without a program
ifndef NO_P4
run_args += -j $(DEFAULT_JSON)
endif

# Set BMV2_SWITCH_EXE to override the BMv2 target
ifdef BMV2_SWITCH_EXE
run_args += -b $(BMV2_SWITCH_EXE)
endif

all: run

run: buildp4
	sudo python $(RUN_SCRIPT) -t $(TOPO) $(run_args)

stop:
	sudo mn -c
	
buildp4: generatep4
	$(P4C) --p4v 16 --p4runtime-files $(BUILD_DIR)/fabric_tunnel.p4.p4info.txt -o $(BUILD_DIR)/fabric_tunnel.json $(BUILD_DIR)/fabric_tunnel.p4

generatep4: dirs
	sudo python ./p4runtime_lib/construct_p4.py

dirs:
	mkdir -p $(BUILD_DIR) $(PCAP_DIR) $(LOG_DIR)

clean: stop
	rm -f *.pcap
	rm -rf $(BUILD_DIR) $(PCAP_DIR) $(LOG_DIR)
