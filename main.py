import milter
import random

# Define a custom processor that modifies mail headers and body
def processor(mailpiece: milter.MailPiece) -> None:
    print(f"----------------\n{mailpiece.recipient_info}\n----------------")

# Initialize and run the milter with the defined processor
myMilter = milter.Milter(
    [processor],    # List of processors, called in order
    socket_type="unix",
    socket_path="asdf",
)
myMilter.run()