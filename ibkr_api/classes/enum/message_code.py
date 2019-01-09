from enum import IntEnum

class MessageCode(IntEnum):
    # System Message Codes
    CONNECTION_LOST_BETWEEN_IB_AND_BRIDGE                   = 1100  ,
    CONNECTION_RESTORED_BETWEEN_IB_AND_BRIDGE_DATA_LOST     = 1101  ,
    CONNECTION_RESTORED_BETWEEN_IB_AND_BRIDGE_DATA_SAVED    = 1102  ,
    SOCKET_PORT_RESET_CONNECTION_DROPPED                    = 1300  ,

    # Warning Message Codes
    NEW_ACCOUNT_DATA_REQUESTED                              = 2100  ,
    UNABLE_TO_SUBSCRIBE_TO_ACCOUNT                          = 2101  ,
    UNABLE_TO_MODIFY_ORDER                                  = 2102  ,
    MARKET_DATA_FARM_DISCONNECTED                           = 2103  ,
    MARKET_DATA_FARM_OK                                     = 2104  ,
    HISTORICAL_DATA_FARM_DISCONNECTED                       = 2105  ,
    HISTORICAL_DATA_FARM_CONNECTED                          = 2106  ,
    HISTORICAL_DATA_FARM_INACTIVE                           = 2107  ,
    MARKET_DATA_FARM_INACTIVE                               = 2108  ,
    ORDER_EVENT_WARNING                                     = 2109  ,
    CONNECTION_BETWEEN_CLIENT_AND_BRIDGE_LOST               = 2110  ,
    CROSS_SIDE_WARNING                                      = 2137  ,

    # Client Error Message Codes
    ALREADY_CONNECTED                                       = 501   ,
    COULD_NOT_CONNECT                                       = 502   ,
    BRIDGE_IS_OUT_OF_DATE                                   = 503   ,
    NOT_CONNECTED                                           = 504   ,


    # TWS Error Message Codes
    MAX_MESSAGES_EXCEEDED                                   = 100   ,
    MAX_TICKERS_REACHED                                     = 101   ,
    DUPLICATE_REQUEST_ID                                    = 102   ,
    DUPLICATE_ORDER_ID                                      = 103   ,
    ORDER_ALREADY_FILLED                                    = 104   ,
    ORDER_MODIFICATION_DOES_NOT_MATCH                       = 105   ,
    CANNOT_TRANSMIT_ORDER_ID                                = 106   ,
    CANNOT_TRANSMIT_INCOMPLETE_ORDER                        = 107   ,
    PRICE_OUTSIDE_DEFINED_RANGE                             = 109   ,
    INVALID_MINIMUM_PRICE_VARIATION                         = 110   ,
    TIF_TYPE_AND_ORDER_TYPE_INCOMPATIBLE                    = 111   ,
    INVALID_TIME_IN_FORCE_OPTION                            = 113   ,
    INVALID_RELATIVE_ORDER                                  = 114   ,
    INVALID_EXCHANGE_FOR_RELATIVE_ORDER                     = 115   ,
    INVALID_EXCHANGE                                        = 116   ,
    BLOCK_ORDER_SIZE_MUST_BE_50                             = 117   ,
    VWAP_ORDER_MUST_USE_VWAP_EXCHANGE                       = 118   ,
    INVALID_ORDER_FOR_VWAP_EXCHANGE                         = 119   ,
    TOO_LATE_FOR_VWAP_ORDER                                 = 120   ,