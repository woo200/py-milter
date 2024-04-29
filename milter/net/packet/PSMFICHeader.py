import struct
import time

from milter.net.packet.packet import Packet
from milter.net.commands import Commands
from milter.net.types import StrArray

class PSMFICHeader(Packet):
    name: str = ""
    value: str = ""

    def __init__(self) -> None:
        super().__init__(Commands.SMFIC_HEADER)
    
    def _serialize(self) -> bytes:
        return StrArray.serialize([self.name, self.value])

    @classmethod
    def read(self, packet_len, stream):
        packet = self()
        packet.name, packet.value = StrArray.read(packet_len, stream)
        return packet
    
    def __repr__(self) -> str:
        return f"PSMFICHeader(name=\"{self.name}\", value=\"{self.value}\")"
    