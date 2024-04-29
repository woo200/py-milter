class Commands:
    # MTA ---> Milter
    SMFIC_ABORT    = ord('A')
    SMFIC_BODY     = ord('B')
    SMFIC_CONNECT  = ord('C')
    SMFIC_MACRO    = ord('D')
    SMFIC_BODYEOB  = ord('E')
    SMFIC_HELO     = ord('H')
    SMFIC_HEADER   = ord('L')
    SMFIC_MAIL     = ord('M')
    SMFIC_EOH      = ord('N')
    SMFIC_OPTNEG   = ord('O')
    SMFIC_RCPT     = ord('R')
    SMFIC_QUIT     = ord('Q')

    # Milter ---> MTA
    SMFIR_ADDRCPT    = ord('+')
    SMFIR_DELRCPT    = ord('-')
    SMFIR_ACCEPT     = ord('a')
    SMFIR_REPLBODY   = ord('b')
    SMFIR_CONTINUE   = ord('c')
    SMFIR_DISCARD    = ord('d')
    SMFIR_ADDHEADER  = ord('h')
    SMFIR_CHGHEADER  = ord('m')
    SMFIR_PROGRESS   = ord('p')
    SMFIR_QUARANTINE = ord('q')
    SMFIR_REJECT     = ord('r')
    SMFIR_TEMPFAIL   = ord('t')
    SMFIR_REPLYCODE  = ord('y')
    SMFIR_OPTNEG     = ord('O')

class Bitmask:
    @staticmethod
    def check(expression, mask):
        return (expression & mask) == mask
    
    @staticmethod
    def set(expression, mask):
        return expression | mask

    @staticmethod
    def unset(expression, mask):
        return expression & ~mask

class OPTNEG_Actions(Bitmask):
    SMFIF_ADDHDRS    = 2 ** 0
    SMFIF_CHGBODY    = 2 ** 1
    SMFIF_ADDRCPT    = 2 ** 2
    SMFIF_DELRCPT    = 2 ** 3 
    SMFIF_CHGHDRS    = 2 ** 4
    SMFIF_QUARANTINE = 2 ** 5

    SMFIF = {
        Commands.SMFIR_ADDHEADER:  SMFIF_ADDHDRS,
        Commands.SMFIR_REPLBODY:   SMFIF_CHGBODY,
        Commands.SMFIR_ADDRCPT:    SMFIF_ADDRCPT,
        Commands.SMFIR_DELRCPT:    SMFIF_DELRCPT,
        Commands.SMFIR_CHGHEADER:  SMFIF_CHGHDRS,
        Commands.SMFIR_QUARANTINE: SMFIF_QUARANTINE,
    }

class OPTNEG_Protocol(Bitmask):
    SMFIP_NOCONNECT  = 2 ** 0
    SMFIP_NOHELO     = 2 ** 1
    SMFIP_NOMAIL     = 2 ** 2
    SMFIP_NORCPT     = 2 ** 3
    SMFIP_NOBODY     = 2 ** 4
    SMFIP_NOHDRS     = 2 ** 5
    SMFIP_NOEOH      = 2 ** 6

    SMFIP = {
        Commands.SMFIC_CONNECT: SMFIP_NOCONNECT,
        Commands.SMFIC_HELO:    SMFIP_NOHELO,
        Commands.SMFIC_MAIL:    SMFIP_NOMAIL,
        Commands.SMFIC_RCPT:    SMFIP_NORCPT,
        Commands.SMFIC_BODY:    SMFIP_NOBODY,
        Commands.SMFIC_HEADER:  SMFIP_NOHDRS,
        Commands.SMFIC_EOH:     SMFIP_NOEOH,
    }