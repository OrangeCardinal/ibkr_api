from enum import Enum

class OrderAction(Enum):
    BUY     =   "BUY"
    SELL    =   "SELL"
    SSHORT  =   "SSHORT" # Institutional Accounts Only
    SLONG   =   "SLONG"  # Institutional Accounts Only
