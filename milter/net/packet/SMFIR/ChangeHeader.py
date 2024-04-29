import struct

from milter.net.packet.packet import Packet
from milter.net.commands import Commands
from milter.net.types import StrArray

class ChangeHeader(Packet):
    index: int = 0
    name: str = ""
    value: str = ""

    def __init__(self, name, value, index) -> None:
        super().__init__(Commands.SMFIR_CHGHEADER)
        self.index = index
        self.name = name
        self.value = value
    
    def _serialize(self) -> bytes:
        return struct.pack("!I", self.index) + StrArray.serialize([self.name, self.value])

    def __repr__(self) -> str:
        return f"ChangeHeader(name=\"{self.name}\", value=\"{self.value}\")"
    