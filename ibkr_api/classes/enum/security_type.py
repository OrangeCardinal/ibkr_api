from enum import Enum
class SecurityType(Enum):
    CASH                        = 'CASH'
    STOCK                       = 'STK'
    FUTURES                     = 'FUT'
    OPTIONS                     = 'OPT'
    FUTURES_OPTIONS             = 'FOP'
    WARRANTS                    = 'WAR'
    BONDS                       = 'BONDS'
    CONTRACTS_FOR_DIFFERENCES   = 'CFD'
    DUTCH_WARRANTS              = 'IOPT'