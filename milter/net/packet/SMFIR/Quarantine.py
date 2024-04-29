import struct

from milter.net.packet.packet import Packet
from milter.net.commands import Commands
from milter.net.types import String

class Quarantine(Packet):
    reason: str = ""

    def __init__(self, reason) -> None:
        super().__init__(Commands.SMFIR_QUARANTINE)
        self.reason = reason
    
    def _serialize(self) -> bytes:
        return String.serialize(self.reason)

    def __repr__(self) -> str:
        return f"Quarantine(reason=\"{self.reason}\")"
    