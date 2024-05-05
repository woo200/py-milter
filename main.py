import milter
import random

# Define a custom processor that modifies mail headers and body
def processor(mailpiece: milter.MailPiece) -> None:
    random_str = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10))
    mailpiece.add_header("X-Filter-Test", f"Test - {random_str}")

# Initialize and run the milter with the defined processor
myMilter = milter.Milter(
    [processor],    # List of processors, called in order
)
myMilter.run()