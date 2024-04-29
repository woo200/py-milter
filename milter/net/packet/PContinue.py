import struct

from milter.net.packet.packet import Packet
from milter.net.commands import Commands

class PContinue(Packet):
    def __init__(self) -> None:
        super().__init__(Commands.SMFIR_CONTINUE)
    
    def _serialize(self) -> bytes:
        return b""
    
    @classmethod
    def read(self, packet_len, stream):
        return self()
    
    def __repr__(self) -> str:
        return f"PContinue"
    