# Py-Milter Documentation

`Py-Milter` is a Python library designed to interact and modify mail pieces during the mail delivery process. It allows users to create custom mail filters (milters) by defining actions such as adding or deleting recipients, modifying headers, changing the body of emails, and more.

## Installation

To use Py-Milter, first clone the repo and put it in your project directory. It can be included with `include milter`. 

## Usage

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
    - [] Add Unix socket support
    - [] Allow more than one header of the same name