class Packet(object):
    def __getitem__(self, item):
        return self.__getattribute__(item)

def parse_packet():
    packet = Packet()
    packet.__setattr__("tcp", 1)
    return packet

a = parse_packet()
print a.tcp         
print a["tcp"]