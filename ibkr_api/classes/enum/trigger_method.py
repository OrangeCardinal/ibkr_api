from enum import IntEnum

class TriggerMethod(IntEnum):
    """
    Specifies how Simulated Stop, Stop-Limit and Trailing Stop orders are triggered.

    Related Links
    -------------
    `https://interactivebrokers.github.io/tws-api/classIBApi_1_1Order.html#ae2e7e8f4a5bae41db31bf0300c7baa48`

    """
    DEFAULT_VALUE       =   0   #   The "double bid/ask" function will be used for orders for OTC stocks and US options.
                                #   All other orders will used the "last" function.
    DOUBLE_BID_ASK      =   1
    LAST                =   2
    DOUBLE_LAST         =   3
    BID_ASK             =   4
    LAST_OR_BID_ASK     =   7
    MIDPOINT            =   8