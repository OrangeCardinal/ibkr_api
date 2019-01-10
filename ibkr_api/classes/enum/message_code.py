from enum import IntEnum

class MessageCode(IntEnum):
    # System Message Codes
    CONNECTION_LOST_BETWEEN_IB_AND_BRIDGE                       = 1100  ,
    CONNECTION_RESTORED_BETWEEN_IB_AND_BRIDGE_DATA_LOST         = 1101  ,
    CONNECTION_RESTORED_BETWEEN_IB_AND_BRIDGE_DATA_SAVED        = 1102  ,
    SOCKET_PORT_RESET_CONNECTION_DROPPED                        = 1300  ,

    # Warning Message Codes
    NEW_ACCOUNT_DATA_REQUESTED                                  = 2100  ,
    UNABLE_TO_SUBSCRIBE_TO_ACCOUNT                              = 2101  ,
    UNABLE_TO_MODIFY_ORDER                                      = 2102  ,
    MARKET_DATA_FARM_DISCONNECTED                               = 2103  ,
    MARKET_DATA_FARM_OK                                         = 2104  ,
    HISTORICAL_DATA_FARM_DISCONNECTED                           = 2105  ,
    HISTORICAL_DATA_FARM_CONNECTED                              = 2106  ,
    HISTORICAL_DATA_FARM_INACTIVE                               = 2107  ,
    MARKET_DATA_FARM_INACTIVE                                   = 2108  ,
    ORDER_EVENT_WARNING                                         = 2109  ,
    CONNECTION_BETWEEN_CLIENT_AND_BRIDGE_LOST                   = 2110  ,
    CROSS_SIDE_WARNING                                          = 2137  ,

    # Client Error Message Codes
    ALREADY_CONNECTED                                           = 501   ,
    COULD_NOT_CONNECT                                           = 502   ,
    BRIDGE_IS_OUT_OF_DATE                                       = 503   ,
    NOT_CONNECTED                                               = 504   ,


    # TWS Error Message Codes
    MAX_MESSAGES_EXCEEDED                                       = 100   ,
    MAX_TICKERS_REACHED                                         = 101   ,
    DUPLICATE_REQUEST_ID                                        = 102   ,
    DUPLICATE_ORDER_ID                                          = 103   ,
    ORDER_ALREADY_FILLED                                        = 104   ,
    ORDER_MODIFICATION_DOES_NOT_MATCH                           = 105   ,
    CANNOT_TRANSMIT_ORDER_ID                                    = 106   ,
    CANNOT_TRANSMIT_INCOMPLETE_ORDER                            = 107   ,
    PRICE_OUTSIDE_DEFINED_RANGE                                 = 109   ,
    INVALID_MINIMUM_PRICE_VARIATION                             = 110   ,
    TIF_TYPE_AND_ORDER_TYPE_INCOMPATIBLE                        = 111   ,
    INVALID_TIME_IN_FORCE_OPTION                                = 113   ,
    INVALID_RELATIVE_ORDER                                      = 114   ,
    INVALID_EXCHANGE_FOR_RELATIVE_ORDER                         = 115   ,
    INVALID_EXCHANGE                                            = 116   ,
    BLOCK_ORDER_SIZE_MUST_BE_50                                 = 117   ,
    VWAP_ORDER_MUST_USE_VWAP_EXCHANGE                           = 118   ,
    INVALID_ORDER_FOR_VWAP_EXCHANGE                             = 119   ,
    TOO_LATE_FOR_VWAP_ORDER                                     = 120   ,
    INVALID_BD_FLAG_FOR_ORDER                                   = 121   ,
    NO_REQUEST_TAG_FOUND_FOR_ORDER                              = 122   ,
    NO_RECORD_FOUND_FOR_CONTRACT_ID                             = 123   ,
    NO_MARKET_RULE_FOR_CONTRACT_ID                              = 124   ,
    BUY_PRICE_MUST_BE_SAME_AS_BEST_ASKING_PRICE                 = 125   ,
    SELL_PRICE_MUST_BE_SAME_AS_BEST_BIDDING_PRICE               = 126   ,
    VWAP_ORDER_MUST_BE_SUBMITTED_AT_LEAST_THREE_MINUTES_BEFORE  = 129   ,
    SWEEP_TO_FILL_FLAG_AND_DISPLAY_SIZE_IGNORED                 = 131   ,
    ORDER_CANNOT_BE_TRASMITTED_WITHOUT_CLEARING_ACCOUNT         = 132   ,
    SUBMIT_NEW_ORDER_FAILED                                     = 133   ,
    MODIFY_ORDER_FAILED                                         = 134   ,
    CANNOT_FIND_ORDER_ID                                        = 135   ,
    ORDER_CANNOT_BE_WATCHED                                     = 136   ,
    TOO_LATE_TO_CANCEL_VWAP_ORDER                               = 137   ,
    CANNOT_PARSE_TICKER_REQUEST                                 = 138   ,
    PARSING_ERROR                                               = 139   ,
    SIZE_SHOULD_BE_INTEGER                                      = 140   ,
    PRICE_VALUE_SHOULD_BE_DOUBLE                                = 141   ,
    INSTITUTIONAL_CUSTOMER_ACCOUNT_DOES_NOT_HAVE_ACCOUNT_INFO   = 142   ,
    REQUEST_ID_MUST_BE_INTEGER                                  = 143   ,
    ORDER_SIZE_DOES_NOT_MATCH_TOTAL_SHARE_ALLOCATION            = 144   ,
    INVALID_ENTRY_FIELDS                                        = 145   ,
    INVALID_TRIGGER_METHOD                                      = 146   ,
    INCOMPLETE_CONDITIONAL_CONTRACT_INFO                        = 147   ,
    INCORRECT_ORDER_TYPE_FOR_CONDITIONAL_ORDER                  = 148   ,
    ORDER_CANNOT_BE_TRANSMITTED_WITHOUT_USER_NAME               = 151   ,
    HIDDEN_ATTRIBUTE_CANNOT_BE_USED_FOR_THIS_ORDER              = 152   ,
    EFPS_CAN_ONLY_BE_LIMIT_ORDERS                               = 153   ,
    ORDERS_CANNOT_BE_TRANSMITTED_FOR_A_HALTED_SECURITY          = 154   ,
    SIZEOP_ORDER_MUST_HAVE_USERNAME_AND_ACCOUNT                 = 155   ,
    SIZEOP_ORDER_MUST_GO_TO_IBSX                                = 156   ,
    ORDER_CAN_BE_EITHER_ICEBERG_OR_DISCRETIONARY                = 157   ,