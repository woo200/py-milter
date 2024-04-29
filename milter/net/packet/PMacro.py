import struct
import time

from milter.net.packet.packet import Packet
from milter.net.commands import Commands
from milter.net.types import StrArray

class PMacro(Packet):
    cmd_code:  int = 0
    nameval: dict = {}

    def __init__(self) -> None:
        super().__init__(Commands.SMFIC_MACRO)
    
    def _serialize(self) -> bytes:
        nameval = []
        for k, v in self.nameval.items():
            nameval.extend([k, v])
        nameval = StrArray.serialize(nameval)
        return struct.pack("!B", self.cmd_code) + nameval

    @classmethod
    def read(self, packet_len, stream):
        packet = self()
        packet.cmd_code, = stream.recv(1)
        packet_len -= 1

        nameval = StrArray.read(packet_len, stream)
        packet.nameval = dict(zip(nameval[::2], nameval[1::2]))
        return packet
    
    def __repr__(self) -> str:
        return f"PMacro(cmd={self.cmd_code}({chr(self.cmd_code)}), nameval={self.nameval})"
    