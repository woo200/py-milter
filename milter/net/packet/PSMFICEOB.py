import struct

from milter.net.packet.packet import Packet
from milter.net.commands import Commands

class PSMFICEOB(Packet):
    def __init__(self) -> None:
        super().__init__(Commands.SMFIC_BODYEOB)
    
    def _serialize(self) -> bytes:
        return b""
    
    @classmethod
    def read(self, packet_len, stream):
        return self()
    
    def __repr__(self) -> str:
        return f"PSMFICEOB"
    