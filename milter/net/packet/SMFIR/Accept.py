import struct

from milter.net.packet.packet import Packet
from milter.net.commands import Commands

class SMFIRAccept(Packet):
    def __init__(self) -> None:
        super().__init__(Commands.SMFIR_ACCEPT)
    
    def _serialize(self) -> bytes:
        return b""
    
    def __repr__(self) -> str:
        return f"SMFIRAccept"
    