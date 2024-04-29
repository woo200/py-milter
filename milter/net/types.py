class NetType:
    @staticmethod
    def read(stream):
        raise NotImplementedError
    
    @staticmethod
    def serialize(data) -> bytes:
        raise NotImplementedError("Cannot serialize base packet")

class String(NetType):
    @staticmethod
    def read(stream) -> str:
        theString = ""
        while True:
            c = stream.recv(1)
            if c == b'\0':
                break
            theString += c.decode()
        return theString

    @staticmethod
    def serialize(data: str) -> bytes:
        return data.encode() + b'\0'

class StrArray(NetType):
    @staticmethod
    def read(total_length, stream) -> list[str]:
        arr = []
        read_length = 0

        while True:
            if read_length >= total_length:
                break

            c = String.read(stream)
            arr.append(c)
            read_length += len(c) + 1
        return arr

    @staticmethod
    def serialize(data: list[str]) -> bytes:
        return b''.join([String.serialize(x) for x in data])
    