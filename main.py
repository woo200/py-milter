import milter

def processor(mailpiece: milter.MailPiece) -> None:
    mailpiece.set_body("Fuck you")

myMilter = milter.Milter([processor])
myMilter.run()
