import struct

class Packet:
    cmd: str = None

    def __init__(self, cmd) -> None:
        self.cmd = cmd
    
    def _serialize(self) -> bytes:
        raise NotImplementedError("Cannot serialize base packet")

    def serialize(self) -> bytes:
        data = self._serialize()
        return struct.pack("!IB", len(data) + 1, self.cmd) + data

    @staticmethod
    def read_header(stream) -> tuple[int, str]:
        p_len, cmd = struct.unpack("!IB", stream.recv(5)) 
        return p_len, cmd
    
    @staticmethod
    def read(packet_len, stream):
        raise NotImplementedError