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