import struct
import time

from milter.net.packet.packet import Packet
from milter.net.commands import Commands
from milter.net.types import StrArray

class PSFMICRcpt(Packet):
    mail_to: str = ""
    ESMTP_args: list[str] = []

    def __init__(self) -> None:
        super().__init__(Commands.SMFIC_MAIL)
    
    def _serialize(self) -> bytes:
        return StrArray.serialize([self.mail_to] + self.ESMTP_args)

    @classmethod
    def read(self, packet_len, stream):
        packet = self()

        packet.mail_to, *packet.ESMTP_args = StrArray.read(packet_len, stream)

        return packet
    
    def __repr__(self) -> str:
        return f"PSFMICRcpt(mail_to=\"{self.mail_to}\", ESMTP_args={self.ESMTP_args})"
    