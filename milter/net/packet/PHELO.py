import struct

from milter.net.packet.packet import Packet
from milter.net.commands import Commands
from milter.net.types import String

class PHELO(Packet):
    helo: str = ""

    def __init__(self) -> None:
        super().__init__(Commands.SMFIC_HELO)
    
    def _serialize(self) -> bytes:
        return String.serialize(self.helo)

    @classmethod
    def read(self, packet_len, stream):
        packet = self()
        packet.helo = String.read(stream)
        return packet
    
    def __repr__(self) -> str:
        return f"PHELO(helo=\"{self.helo}\")"
    