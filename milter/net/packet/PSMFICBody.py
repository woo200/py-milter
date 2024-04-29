import socket

from milter.net.packet.packet import Packet
from milter.net.commands import Commands
from milter.net.packet.PContinue import PContinue

class PSMFICBody(Packet):
    body: str = ""

    def __init__(self) -> None:
        super().__init__(Commands.SMFIC_MAIL)
    
    def _serialize(self) -> bytes:
        return self.body.encode()
    
    @classmethod
    def read(self, packet_len, stream):
        packet = self()

        self.body = stream.recv(packet_len, socket.MSG_WAITALL).decode()
        stream.send(PContinue().serialize())
            
        return packet

    
    def __repr__(self) -> str:
        return f"PSMFICBody(chunk=\"{self.body[10:].strip()}...\")"
    