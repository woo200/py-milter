import struct

from milter.net.packet.packet import Packet
from milter.net.commands import Commands
from milter.net.types import String

class DelRCPT(Packet):
    rcpt: str = ""

    def __init__(self, rcpt) -> None:
        super().__init__(Commands.SMFIR_DELRCPT)
        self.rcpt = rcpt
    
    def _serialize(self) -> bytes:
        return String.serialize(self.rcpt)
    
    def __repr__(self) -> str:
        return f"DelRCPT(rcpt=\"{self.rcpt}\")"
    