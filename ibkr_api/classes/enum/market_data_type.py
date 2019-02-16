from enum import IntEnum

class MarketDataType(IntEnum):
    LIVE            = 1
    FROZEN          = 2
    DELAYED         = 3
    DELAYED_FROZEN  = 4
