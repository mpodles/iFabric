class HeaderParser(object):
    
    class Packet(object):
        def __init__(self):
            self.protocols = []
        def __getitem__(self, item):
            return self.__getattribute__(item)
        def protocols(self):
            print self.protocols
        def fields(self):
            for item in self.protocols:
                print self.__getattribute__(item).__dict__
    def __init__(self, protocols_description_file_path= "/home/mpodles/iFabric/src/main/configuration_files/topology_description_test.json"):
        self.read_protocols(protocols_description_file_path)
        self.load_variables_and_fields()
        self.translate_next_protocols_fields()
    def read_protocols(self, protocols_description_file_path):
        with open(protocols_description_file_path, "r") as f:
            protocols_file = json.loads(f.read())
            self.protocols_used = protocols_file["protocols_used"]
            self.protocols_stack = protocols_file["protocols_stacks"]
            self.protocols_definition = protocols_file["protocols_definition"]
            self.next_protocols_fields = protocols_file["next_protocols_fields"]
            self.match_fields_used = protocols_file["match_fields_used"]
            self.match_fields_to_learn = protocols_file["match_fields_to_learn"]
            self.lookup = protocols_file["lookup"]
    def load_variables_and_fields(self):
        self.variables = {}
        self.fields = {}
        for protocol, definition in self.protocols_definition.items():
            for variable in definition.get("variables",[]):
                parsed_variable = self.parsereturne"]] = parsed_variable
            self.fields[protocol] = []
            for field in definition["fields"]:
                self.fields[protocol].append((field["name"],field["size"]))
    def parse_variable(self,variable):
        try:
            variable = int(variable, base = 2)
        except:
            pass
        try:
            variable = int(variable, base = 16)
        except:
            pass
        try:
            variable = int(variable)
        except:
            pass
        return variable
    def to_bits(self, payload):
        # payload_bytes = []
        # for x in payload:
        #     payload_bytes.append(ord(x))
        # return payload_bytes
        return ''.join(format(ord(x), '08b') for x in payload)
    def translate_next_protocols_fields(self):
        self.next_protocol = {}
        for protocol, description in self.next_protocols_fields.items():
            next_field = description.get("next_protocol_field", None)
            if next_field is not None:
                self.next_protocol[next_field] = {}
                for next_protocol, value in description.get("next_protocol_value",{}).items():
                    value = self.variables.get(value, value)
                    self.next_protocol[next_field][value] = next_protocol
    def parse_packet(self, packet):
        parsed_packet = Parser.Packet()
        packet = self.to_bits(packet)
        if self.parse_variable(self.lookup["value"]) == self.parse_variable(packet[0:self.lookup["size"]]):
            protocol = self.lookup["match"]
        else:
            protocol = self.lookup["default"]
        still_parsing = True
        while still_parsing:
            parsed_packet.protocols.append(protocol)
            parsed_packet.__setattr__(protocol, Parser.Packet())
            for field_name, field_size in self.fields[protocol]:
                field_value = packet[0:field_size]
                packet = packet[field_size:]
                parsed_packet[protocol].__setattr__(field_name, field_value)
            
            still_parsing = False
            next_field = self.next_protocols_fields[protocol].get("next_protocol_field", None)
            if next_field is not None:
                still_parsing = True
                next_field_value = parsed_packet[protocol][next_field]
                try:
                    print self.parse_variable(next_field_value)
                    protocol = self.next_protocol[next_field][self.parse_variable(next_field_value)]
                except:
                    still_parsing = False
                
        return parsed_packet
