import struct

from milter.net.packet.packet import Packet
from milter.net.commands import Commands

from milter.net.types import String

class PSMFICConnect(Packet):
    hostname: str = ""
    family:   int = 0
    port:     int = 0
    address:  str = ""

    def __init__(self) -> None:
        super().__init__(Commands.SMFIC_CONNECT)
    
    def _serialize(self) -> bytes:
        return String.serialize(self.hostname) + \
               struct.pack("!B", self.family) + \
               struct.pack("!H", self.port) + \
               String.serialize(self.address)

    @classmethod
    def read(self, packet_len, stream):
        packet = self()
        
        packet.hostname = String.read(stream)
        packet.family, = stream.recv(1)
        packet.port,   = struct.unpack("!H", stream.recv(2))
        packet.address = String.read(stream)

        return packet
    
    def __repr__(self) -> str:
        return f"PSMFICConnect(hostname=\"{self.hostname}\", family={self.family}, port={self.port}, address=\"{self.address}\")"
    