from milter.net.commands import Commands, OPTNEG_Protocol, OPTNEG_Actions
from milter.net.packet import SMFIR
import milter.net.packet

from dataclasses import dataclass, field
from enum import Enum

import threading
import socket
import select
import struct
import os

COMMAND_TABLE = {
    Commands.SMFIC_OPTNEG: milter.net.packet.POptNeg,
    Commands.SMFIC_MACRO: milter.net.packet.PMacro,
    Commands.SMFIC_HELO: milter.net.packet.PHELO,
    Commands.SMFIC_CONNECT: milter.net.packet.PSMFICConnect,
    Commands.SMFIC_MAIL: milter.net.packet.PSFMICMail,
    Commands.SMFIC_RCPT: milter.net.packet.PSFMICRcpt,
    ord('T'): milter.net.packet.PIDKWhatThisDoes,
    Commands.SMFIC_HEADER: milter.net.packet.PSMFICHeader,
    Commands.SMFIC_EOH: milter.net.packet.PSMFICEOH,
    Commands.SMFIC_BODY: milter.net.packet.PSMFICBody,
    Commands.SMFIC_BODYEOB: milter.net.packet.PSMFICEOB,
    Commands.SMFIC_ABORT: milter.net.packet.PSIMFICAbort,
    Commands.SMFIC_QUIT: milter.net.packet.PSIMFICQuit,
}

ACTIONS = [
    OPTNEG_Actions.SMFIF_ADDHDRS,
    OPTNEG_Actions.SMFIF_CHGBODY,
    OPTNEG_Actions.SMFIF_ADDRCPT,
    OPTNEG_Actions.SMFIF_DELRCPT,
    OPTNEG_Actions.SMFIF_CHGHDRS,
    OPTNEG_Actions.SMFIF_QUARANTINE
]

class MilterState(Enum):
    AWAIT_MAIL = 0
    PROCESSING = 1
    CONN_ABORT = 2

@dataclass
class Address:
    address: str
    ESMTP_args: list[str]

@dataclass
class MailerConnection:
    job_id: str = ""
    sender_info: Address = None
    recipient_info: list[Address] = field(default_factory=list)
    body: str = ""
    headers: dict[str, str] = field(default_factory=dict)

MAILERCONNATTRS = list(MailerConnection.__annotations__.keys())

class MailState(Enum):
    GOOD = 0
    DISCARD = 1
    QUARANTINED = 2
    REJECTED = 3
    TEMPFAIL = 4

class MailPiece:
    __mailpiece: MailerConnection
    __required_actions: list[str] = {
        "ADDRCPT": [],
        "DELRCPT": [],
        "CHGBODY": True,
        "DISCARD": False,
        "ADDHDRS": [],
        "CHGHDRS": [],
        "QUARANTINE": False,
        "REJECT": False,
        "TEMPFAIL": False,
        "REPLYCODE": None
    }
    state: MailState = MailState.GOOD

    def __init__(self, mailpiece: MailerConnection) -> None:
        self.__mailpiece = mailpiece
    
    def __getattribute__(self, name: str):
        if name in MAILERCONNATTRS:
            return getattr(self.__mailpiece, name)
        return super().__getattribute__(name)
    
    def __setattr__(self, name: str, value) -> None:
        if name in MAILERCONNATTRS:
            if name == "body":
                self.set_body(value)
            else:
                setattr(self.__mailpiece, name, value)
        else:
            super().__setattr__(name, value)
    
    def add_recipient(self, address: str):
        self.__mailpiece.recipient_info.append(Address(address, []))
        self.__required_actions["ADDRCPT"].append(address)
    
    def del_recipient(self, address: str):
        self.__mailpiece.recipient_info = [recipient for recipient in self.__mailpiece.recipient_info if recipient.address != address]
        self.__required_actions["DELRCPT"].append(address)
    
    def set_body(self, body: str):
        self.__mailpiece.body = body
        self.__required_actions["CHGBODY"] = True

    def discard(self, discard: bool = True):
        self.__required_actions["DISCARD"] = discard
        self.state = MailState.DISCARD # TODO: Bug if undiscarded

    def add_header(self, name: str, value: str):
        self.__mailpiece.headers[name] = value
        self.__required_actions["ADDHDRS"].append({"name": name, "value": value})
    
    def change_header(self, name: str, value: str, index: int = 0):
        self.__mailpiece.headers[name] = value
        self.__required_actions["CHGHDRS"].append({"name": name, "value": value, "index": index})
    
    def quarantine(self, reason):
        self.__required_actions["QUARANTINE"] = reason
        self.state = MailState.QUARANTINED
    
    def reject(self, reject: bool = True):
        self.__required_actions["REJECT"] = reject
        self.state = MailState.REJECTED
    
    def tempfail(self, tempfail: bool = True):
        self.__required_actions["TEMPFAIL"] = tempfail
        self.state = MailState.TEMPFAIL

    def reply_code(self, code: int, message: str):
        self.__required_actions["REPLYCODE"] = {"code": code, "message": message}
    
    def send_response(self, connection: socket.socket):
        response = b''
        if self.state == MailState.GOOD:
            for action in self.__required_actions["ADDRCPT"]:
                response += SMFIR.AddRCPT(action).serialize()
            for action in self.__required_actions["DELRCPT"]:
                response += SMFIR.DelRCPT(action).serialize()
            if self.__required_actions["CHGBODY"]:
                SMFIR.ReplBody(self.__mailpiece.body).send(connection)
            for action in self.__required_actions["ADDHDRS"]:
                response += SMFIR.AddHeader(action["name"], action["value"]).serialize()
            for action in self.__required_actions["CHGHDRS"]:
                response += SMFIR.ChangeHeader(action["name"], action["value"], action["index"]).serialize()
            if self.__required_actions["REPLYCODE"]:
                response += SMFIR.ReplyCode(self.__required_actions["REPLYCODE"]["code"], self.__required_actions["REPLYCODE"]["message"]).serialize()
            
            # Send the response
            connection.send(response)
            # Accept the changes
            connection.send(SMFIR.Accept().serialize())

        elif self.state == MailState.DISCARD:
            connection.send(SMFIR.Discard().serialize())
        elif self.state == MailState.QUARANTINED:
            connection.send(SMFIR.Quarantine(self.__required_actions["QUARANTINE"]).serialize())
        elif self.state == MailState.REJECTED:
            connection.send(SMFIR.Reject().serialize())
        elif self.state == MailState.TEMPFAIL:
            connection.send(SMFIR.TempFail().serialize())

class Milter:
    def __init__(self, processors, **kwargs) -> None:
        self.args = {
            "host": '0.0.0.0',
            "port": 1234,
            "socket_type": "tcp", # tcp or unix
            "socket_path": "", # Path to unix socket
            **kwargs
        }
        self.processors = processors
        self._threads = []
        self.listener_socket = None
        # self.milterHandlers = milterHandlers

    def run(self):
        if self.args['socket_type'] == "tcp":
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.args['host'], self.args['port']))
            sock.listen()
        elif self.args['socket_type'] == "unix":
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(self.args['socket_path'])
            sock.listen()
        else:
            raise ValueError(f"Invalid socket type {self.args['socket_type']}")
        self.listener_socket = sock

        read_list = [sock]

        while True:
            readable, _, _ = select.select(read_list, [], [], 1)
            for s in readable:
                if s is sock:
                    connection, addr = sock.accept()
                    conn_thread = threading.Thread(
                        target=self.__handle_conn,
                        args=(connection, addr),
                        daemon=True
                    )
                    conn_thread.start()
                    self._threads.append(conn_thread)
    
    def close(self):
        self.listener_socket.close()
        for thread in self._threads:
            thread.join()
    
        
    def __compute_protocol(self) -> int:
        protocol = []
        for key, value in OPTNEG_Protocol.SMFIP.items():
            if key not in COMMAND_TABLE:
                protocol.append(value)
        return sum(protocol)

    def __handle_conn(self, connection: socket.socket, addr):
        with connection:
            state: MilterState = MilterState.AWAIT_MAIL
            current_job: MailerConnection = MailerConnection()

            while True:
                if state == MilterState.CONN_ABORT:
                    state = MilterState.AWAIT_MAIL
                    current_job = MailerConnection()

                try:
                    packet_len, command = milter.net.packet.Packet.read_header(connection)
                except struct.error:
                    continue

                if command not in COMMAND_TABLE:
                    print(f"Unknown command: {command} ({chr(command)})")
                    print(connection.recv(packet_len-1))
                    continue

                packet = COMMAND_TABLE[command].read(packet_len-1, connection)

                if command == Commands.SMFIC_QUIT:
                    # TODO: Handle this
                    connection.close()
                    break
                if command == Commands.SMFIC_ABORT:
                    state = MilterState.CONN_ABORT
                    continue
                
                # Compute what actions are available and send them back
                if command == Commands.SMFIC_OPTNEG:
                    packet.protocol = self.__compute_protocol()
                    packet.actions = sum(ACTIONS)
                    connection.send(packet.serialize())
                elif command == Commands.SMFIC_HELO:
                    connection.send(milter.net.packet.PContinue().serialize())
                    state = MilterState.PROCESSING
                elif command == Commands.SMFIC_CONNECT:
                    connection.send(milter.net.packet.PContinue().serialize())
            
                # Handle macros
                if command == Commands.SMFIC_MACRO:
                    data = packet.nameval

                    if packet.cmd_code == Commands.SMFIC_MAIL:
                        pass # We dont do anything with this 
                    
                    if packet.cmd_code == Commands.SMFIC_RCPT:
                        pass # TODO: Handle this
                
                # We recieved a new piece of mail
                if command == Commands.SMFIC_MAIL:
                    current_job.sender_info = Address(packet.mail_from, packet.ESMTP_args)
                    connection.send(milter.net.packet.PContinue().serialize())
                    state = MilterState.PROCESSING

                # We recieved a new recipient
                elif command == Commands.SMFIC_RCPT:
                    current_job.recipient_info.append(Address(packet.mail_to, packet.ESMTP_args))
                    connection.send(milter.net.packet.PContinue().serialize())

                # We recieved something we need to respond to
                elif command == ord('T'):
                    connection.send(milter.net.packet.PContinue().serialize())

                # We recieved a header
                elif command == Commands.SMFIC_HEADER:
                    current_job.headers[packet.name] = packet.value
                    connection.send(milter.net.packet.PContinue().serialize())

                # We recieved the end of headers
                elif command == Commands.SMFIC_EOH:
                    connection.send(milter.net.packet.PContinue().serialize())
                
                # Start reading the body
                elif command == Commands.SMFIC_BODY:
                    current_job.body += packet.body
                
                # We recieved the end of the body
                elif command == Commands.SMFIC_BODYEOB:
                    # Process the mail
                    mailpiece = MailPiece(current_job)
                    for processor in self.processors:
                        processor(mailpiece)
                    mailpiece.send_response(connection)
                    
                    state = MilterState.CONN_ABORT
                    continue

