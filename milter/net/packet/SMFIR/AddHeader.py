import struct

from milter.net.packet.packet import Packet
from milter.net.commands import Commands
from milter.net.types import StrArray

class AddHeader(Packet):
    name: str = ""
    value: str = ""

    def __init__(self, name, value) -> None:
        super().__init__(Commands.SMFIR_ADDHEADER)
        self.name = name
        self.value = value
    
    def _serialize(self) -> bytes:
        return StrArray.serialize([self.name, self.value])

    def __repr__(self) -> str:
        return f"AddHeader(name=\"{self.name}\", value=\"{self.value}\")"
    