import struct

from milter.net.packet.packet import Packet
from milter.net.commands import Commands
from milter.net.types import String

class ReplyCode(Packet):
    smtp_code: int = 0
    smtp_message: str = ""

    def __init__(self, smtp_code, smtp_message) -> None:
        super().__init__(Commands.SMFIR_REPLYCODE)
        self.smtp_code = smtp_code
        self.smtp_message = smtp_message
    
    def _serialize(self) -> bytes:
        return f"{self.smtp_code:03} " + String.serialize(self.smtp_message)

    def __repr__(self) -> str:
        return f"ReplyCode(smtp_code={self.smtp_code}, smtp_message=\"{self.smtp_message}\")"
    