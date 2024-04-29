# Py-Milter Documentation

`Py-Milter` is a Python library designed to interact and modify mail pieces during the mail delivery process. It allows users to create custom mail filters (milters) by defining actions such as adding or deleting recipients, modifying headers, changing the body of emails, and more.

## Installation

To use Py-Milter, first clone the repo and put it in your project directory. It can be included with `include milter`. 

## Usage

***If you dont understand something, see section [WTF is a Milter?](#WTF-is-a-Milter?)***
The primary component of Py-Milter are processors, processors are functions that accept 1 argument. 
```python
def processor(mailpiece: milter.MailPiece) -> None:
    # ...
```
The `mailpiece` variable is the current email being processed. See below for reference

### Class `MailPiece`

#### Attributes

( inherited )
- `body: str`: Email body contents (When modified, set_body is automatically called)
- `sender_info: @dataclass Address`: Sender address [attrs address & ESMTP_args]
- `recipient_info: list[@dataclass Address]`: List of recipients [attrs see above]
- `headers: dict[str, str]`: Email headers

#### Methods

- `add_recipient(address: str)`: Adds a new recipient to the mail piece.
- `del_recipient(address: str)`: Removes a recipient from the mail piece.
- `set_body(body: str)`: Sets or modifies the body of the mail piece. (Alternatively, you can directly modify the .body attribute and it will do the same thing.)
- `discard(discard: bool = True)`: Discards the mail piece, stopping further processing.
- `add_header(name: str, value: str)`: Adds a new header to the mail piece.
- `change_header(name: str, value: str, index: int = 0)`: Changes an existing header of the mail piece.
- `quarantine(reason: str)`: Quarantines the mail piece for a specified reason.
- `reject(reject: bool = True)`: Rejects the mail piece, stopping its delivery.
- `tempfail(tempfail: bool = True)`: Marks the mail piece to temporarily fail, possibly for retry.
- `reply_code(code: int, message: str)`: Sets a custom reply code and message for the mail piece.
- `send_response(connection: socket.socket)`: Sends the appropriate responses back to the mail server based on the actions taken.

### Example Milter

Here is a simple example demonstrating how to create and run a milter that modifies mail headers and appends text to the body of messages:

```python
import milter
import random

# Define a custom processor that modifies mail headers and body
def processor(mailpiece: milter.MailPiece) -> None:
    mailpiece.change_header("Date", "Hey look at me!", 0)
    mailpiece.body += "Appended to body!"

# Initialize and run the milter with the defined processor
myMilter = milter.Milter(
    [processor],    # List of processors, called in order
    host="0.0.0.0", # TCP Host (optional, default)
    port=1234,      # TCP Port (optional, default)
)
myMilter.run()
```

## To-Do
	- [ ] Add Unix socket support
    - [ ] Allow more than one header of the same name

---

# WTF is a Milter? 
## Understanding Email Delivery and the Role of Milters

#### Terminology

- `MTA (Mail Transfer Agent)` An MTA is a program (like Postfix) that is responsible for receiving incoming emails, sending outgoing emails, and routing those emails to the proper program for delivery.
- `Milter (Mail Filter)` A Milter is a program that runs separately from the MTA, which the MTA is configured to send incoming emails to for processing, such as spam blocking, virus detection, etc.

### How Email Works (Simplified.. a lot)

Email transmission involves multiple servers which handle the delivery of messages from sender to recipient. Consider a scenario where a user with an email address at `@gmail.com` sends a message to another user at `@example.com`. The server managing emails for `@gmail.com` (Server 1) sends the message to the server for `@example.com` (Server 2).

### The Role of Postfix and Milters

**Postfix** acts as the mail transfer agent (MTA) for Server 2. It is responsible for receiving emails from other servers. Upon receiving an email, Postfix uses **Milters (Mail Filters)** to process and potentially modify the email before it is delivered to the recipient's mailbox.

#### What Happens When Postfix Receives a Message

When Postfix receives an email, it consults a list of milters to determine what actions to take on the incoming mail. These milters can inspect, modify, or take various actions on the email based on predefined rules or conditions. Each milter operates independently, performing tasks such as scanning for viruses, encrypting content, or even altering email headers and body.

### Communication Between Postfix and Milters

#### Milter Protocol

To enable communication between Postfix and milters, the **Milter Protocol** is used. This protocol defines how Postfix, acting as the MTA, communicates with milters. When an email arrives, Postfix can open a connection to milters either through TCP/IP or a UNIX socket.

#### PyMilter: An Implementation of the Milter Protocol

**PyMilter** is a Python implementation of the Milter Protocol, providing a high-level interface for modifying messages among other functionalities. PyMilter sets up a TCP socket that Postfix can connect to, allowing for dynamic interaction as emails are processed.
