import struct

from milter.net.packet.packet import Packet
from milter.net.commands import Commands

class POptNeg(Packet):
    version:  int = 2
    actions:  int = 0
    protocol: int = 0

    def __init__(self) -> None:
        super().__init__(Commands.SMFIC_OPTNEG)
    
    def _serialize(self) -> bytes:
        return struct.pack("!III", 
                           self.version, 
                           self.actions, 
                           self.protocol)

    @classmethod
    def read(self, packet_len, stream):
        packet = self()
        packet.version, packet.actions, packet.protocol = struct.unpack("!III", stream.recv(4 * 3))
        return packet
    
    def __repr__(self) -> str:
        return f"POptNeg(v={self.version}, act={self.actions}, proto={self.protocol})"
    