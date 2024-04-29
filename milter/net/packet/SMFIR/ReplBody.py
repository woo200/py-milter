import struct
import time
import io

from milter.net.packet.packet import Packet
from milter.net.commands import Commands

class ReplBody(Packet):
    body: str = ""
    c_byte: int = 0 # index when sending
    chunk_size: int = 65535 # chunk size when sending

    def __init__(self, body="") -> None:
        self.body = body
        super().__init__(Commands.SMFIR_REPLBODY)
    
    def serialize(self) -> bytes:
        raise NotImplementedError("To send this packet, use the send method instead.")\
    
    # I dont think this is needed
    def __wait_for_ack(self, stream):
        cmd = None
        while cmd != Commands.SMFIR_CONTINUE:
            _, cmd = Packet.read_header(stream)

    # send the chunked buffer
    def send(self, stream):
        buffer = io.BytesIO(self.body.encode())
        while True:
            chunk = buffer.read(self.chunk_size)
            if not chunk:
                break
            packet = struct.pack("!IB", len(chunk) + 1, self.cmd) + chunk
            stream.sendall(packet)
            time.sleep(10 / 1000) # 10ms delay
    
    @classmethod
    def read(self, packet_len, stream):
        raise NotImplementedError("not implemented yet. :(")
        packet = self()
        return packet

    
    def __repr__(self) -> str:
        return f"ReplBody(chunk=\"{self.body[10:].strip()}...\")"
    