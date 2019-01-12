from enum import Enum

class Show(Enum):
    """
    Encapsulates all legal 'what_to_show' values

    Related API Calls
    -----------------
    ``request_historical_data``
    """
    TRADES                      = 'TRADES'
    MIDPOINT                    = 'MIDPOINT'
    BID                         = 'BID'
    ASK                         = 'ASK'
    BID_ASK                     = 'BID_ASK'
    HISTORICAL_VOLATILITY       = 'HISTORICAL_VOLATILITY'
    OPTION_IMPLIED_VOLATILITY   = 'OPTION_IMPLIED_VOLATILITY'